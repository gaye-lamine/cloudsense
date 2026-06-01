FROM python:3.12-slim

LABEL maintainer="CloudSense Team"
LABEL description="CloudSense - Alibaba Cloud Cost Optimization Agent"
LABEL hackathon="Global AI Hackathon Qwen Cloud - Track 4: Autopilot Agent"

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/
COPY infra/ ./infra/

# Copy frontend build (pre-built)
COPY frontend/dist/ ./frontend/dist/

# Environment
ENV APP_ENV=production
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
