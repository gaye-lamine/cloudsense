from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Metric snapshot representation
class MetricPoint(BaseModel):
    timestamp: datetime
    value: float


class MetricSnapshot(BaseModel):
    instance_id: str
    metric_name: str
    unit: str
    points: List[MetricPoint]


# Anomaly detection & analysis schemas
class AnomalyReport(BaseModel):
    id: str
    instance_id: str
    service_type: str = "ECS"  # ECS, RDS, Object Storage, etc.
    metric_name: str
    severity: str = "warning"  # critical, warning, info
    current_value: float
    baseline_value: float
    root_cause: str
    impact_description: str
    remediation_action: str
    estimated_monthly_savings: float
    detected_at: datetime = Field(default_factory=datetime.utcnow)


# Proposed Fix & Pull Request schemas
class ProposedFix(BaseModel):
    id: str
    anomaly_id: str
    title: str
    description: str
    files_to_modify: List[str]
    diff_content: str
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    status: str = "pending"  # pending, approved, rejected, deploying, deployed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


# Dashboard summary metrics
class DashboardStats(BaseModel):
    total_anomalies_detected: int
    total_anomalies_resolved: int
    pending_approvals: int
    active_monitored_instances: int
    total_monthly_spend: float
    projected_monthly_savings: float
    actual_savings_realized: float


# Human-In-The-Loop action
class ApprovalRequest(BaseModel):
    fix_id: str
    action: str  # approve, reject
    notes: Optional[str] = None


# Agent websocket output schema for live logs & reasoning streaming
class AgentLiveMessage(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str  # reasoning, tool_call, tool_output, anomaly_detected, status_change
    message: str
    payload: Optional[dict] = None
