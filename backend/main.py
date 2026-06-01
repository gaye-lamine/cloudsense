import asyncio
import logging
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from backend.config import settings
from backend.models.schemas import DashboardStats, ApprovalRequest
from backend.agents.orchestrator import orchestrator
from backend.mcp.server import mcp

# Set up beautiful structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloudsense")

# WebSocket active client pool
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message_dict: dict):
        """Sends data dictionary as JSON to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message_dict)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")


manager = ConnectionManager()

from backend.models.database import init_db

# Define FastAPI context lifespan for background scheduling
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create SQLite database tables if they do not exist
    try:
        init_db()
        logger.info("SQLAlchemy database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

    # Hook orchestrator callback to WebSocket broadcaster
    async def socket_broadcaster(live_msg):
        await manager.broadcast(live_msg.model_dump(mode="json"))
    
    orchestrator.set_broadcast_callback(socket_broadcaster)
    
    # Run an initial autonomous scan in the background
    asyncio.create_task(orchestrator.run_scan_cycle())
    
    yield


app = FastAPI(
    title="CloudSense Backend API",
    description="Autopilot Agent cost monitoring and optimization backend built with Qwen Cloud",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite dev development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────
# REST Endpoints
# ──────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Service health state status check."""
    return {"status": "healthy", "environment": settings.APP_ENV, "mocks": settings.USE_MOCKS}


@app.get("/api/stats", response_model=DashboardStats)
def get_stats():
    """Retrieve full dashboard KPI performance stats."""
    return orchestrator.get_dashboard_stats()


@app.get("/api/anomalies")
def get_anomalies():
    """List all detected cost anomalies directly from the database."""
    return [a.model_dump(mode="json") for a in orchestrator.get_anomalies()]


@app.get("/api/fixes")
def get_fixes():
    """List all proposed optimization fixes (PRs) directly from the database."""
    return [f.model_dump(mode="json") for f in orchestrator.get_fixes()]


@app.get("/api/connection-status")
def get_connection_status():
    """Retrieve current Alibaba Cloud and Qwen connection state/errors."""
    from backend.services.cloud_monitor import cloud_monitor
    return cloud_monitor.check_credentials_status()


# ──────────────────────────────────────────────────────────
# Configuration Settings Endpoints
# ──────────────────────────────────────────────────────────

@app.get("/api/settings")
def get_settings():
    """Retrieve operational config thresholds (CPU, queries)."""
    from backend.models.database import SessionLocal, ConfigurationSetting
    db = SessionLocal()
    try:
        settings_list = db.query(ConfigurationSetting).all()
        # Default fallback values
        default_config = {
            "cpu_utilization_threshold": "10.0",
            "slow_query_threshold": "50",
            "egress_egress_alert_mb": "100.0"
        }
        for s in settings_list:
            default_config[s.key] = s.value
        return default_config
    finally:
        db.close()


@app.post("/api/settings")
def update_settings(payload: dict):
    """Save custom threshold variables into persistent storage."""
    from backend.models.database import SessionLocal, ConfigurationSetting
    db = SessionLocal()
    try:
        for k, v in payload.items():
            setting = db.query(ConfigurationSetting).filter(ConfigurationSetting.key == k).first()
            if setting:
                setting.value = str(v)
            else:
                db.add(ConfigurationSetting(key=k, value=str(v)))
        db.commit()
        return {"status": "success", "message": "Threshold configurations saved successfully."}
    finally:
        db.close()


@app.post("/api/scan")
def trigger_manual_scan(background_tasks: BackgroundTasks):
    """Manually forces a background scan of CloudMonitor telemetry."""
    if orchestrator.is_scanning:
        raise HTTPException(status_code=400, detail="An autonomous scan is already in execution.")
    background_tasks.add_task(orchestrator.run_scan_cycle)
    return {"status": "initiated", "message": "Background scanning has been initiated."}


@app.post("/api/approve")
async def approve_fix(approval: ApprovalRequest):
    """Processes Human-in-the-loop validation actions (Approve/Reject)."""
    success = await orchestrator.handle_human_checkpoint(approval.fix_id, approval.action)
    if not success:
        raise HTTPException(status_code=400, detail="Action could not be executed or fix_id is invalid.")
    return {"status": "success", "action": approval.action}


# ──────────────────────────────────────────────────────────
# WebSockets Endpoint (Live Agent CoT Stream)
# ──────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial config setup and current anomalies/fixes immediately
        from backend.services.cloud_monitor import cloud_monitor
        await websocket.send_json({
            "type": "welcome",
            "payload": {
                "anomalies": [a.model_dump(mode="json") for a in orchestrator.get_anomalies()],
                "fixes": [f.model_dump(mode="json") for f in orchestrator.get_fixes()],
                "stats": orchestrator.get_dashboard_stats().model_dump(mode="json"),
                "connection_status": cloud_monitor.check_credentials_status()
            }
        })
        
        while True:
            # Maintain connection alive, process incoming heartbeats or client commands
            data = await websocket.receive_text()
            logger.info(f"WebSocket client data received: {data}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket unexpected connection exception: {e}")
        manager.disconnect(websocket)


# Mount static build files (for production deployment packaging)
# Handled gracefully if frontend/dist doesn't exist yet during development
try:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
except Exception:
    logger.warning("Frontend build distribution folder not found. Mounting static assets skipped.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True if settings.APP_ENV == "development" else False
    )
