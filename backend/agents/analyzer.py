import json
import logging
from datetime import datetime
from backend.services.cloud_monitor import cloud_monitor
from backend.services.qwen_client import qwen_client
from backend.models.schemas import AnomalyReport

logger = logging.getLogger("cloudsense")


class CloudSenseAnalyzer:
    def __init__(self):
        self.monitor = cloud_monitor
        self.qwen = qwen_client

    def run_full_audit(self) -> list[AnomalyReport]:
        """
        Scans all active services, queries metrics from CloudMonitor,
        and analyzes them via the Qwen cost reasoning model.
        """
        anomalies = []
        services = self.monitor.get_monitored_services()
        
        logger.info(f"Starting infrastructure scan across {len(services)} services...")
        
        for svc in services:
            instance_id = svc["instance_id"]
            svc_name = svc["name"]
            
            # Fetch appropriate metric based on service type
            if svc["type"] == "ECS":
                metric_name = "CPUUtilization"
            elif svc["type"] == "RDS":
                metric_name = "SlowQueryCount"
            else:
                metric_name = "AttachmentState"

            logger.info(f"Fetching metrics for {svc_name} ({instance_id}) - {metric_name}")
            
            metrics = self.monitor.fetch_metrics(instance_id, metric_name)
            
            # Compile metric points summary for LLM
            points_summary = "\n".join(
                [f"[{pt.timestamp}] value: {pt.value}" for pt in metrics.points[-10:]]
            )
            
            payload = (
                f"Resource Name: {svc_name}\n"
                f"Resource ID: {instance_id}\n"
                f"Instance Type: {svc.get('details', 'Unknown')}\n"
                f"Metric Checked: {metric_name} ({metrics.unit})\n"
                f"Recent Telemetry Points:\n{points_summary}"
            )
            
            # Request Qwen decision
            logger.info(f"Invoking Qwen cost optimization auditor for {instance_id}")
            report_data = self.qwen.analyze_metrics_anomaly(payload)
            
            # Check if this is a real anomaly (savings > 0)
            if report_data.get("estimated_monthly_savings", 0.0) > 0.0:
                report = AnomalyReport(
                    id=f"anom-{instance_id.lower()}-{int(datetime.utcnow().timestamp())}",
                    instance_id=instance_id,
                    service_type=svc["type"],
                    metric_name=metric_name,
                    severity=report_data.get("severity", "warning"),
                    current_value=report_data.get("current_value", 0.0),
                    baseline_value=report_data.get("baseline_value", 0.0),
                    root_cause=report_data.get("root_cause", "Overprovisioned resource config"),
                    impact_description=report_data.get("impact_description", "Wasted spending"),
                    remediation_action=report_data.get("remediation_action", "Downsize to cheaper instance tier"),
                    estimated_monthly_savings=report_data.get("estimated_monthly_savings", 0.0)
                )
                anomalies.append(report)
                logger.info(f"🚨 Anomaly Detected on {instance_id}: Savings Estimate ${report.estimated_monthly_savings}/mo")
                
        return anomalies


# Shared analyzer instance
analyzer = CloudSenseAnalyzer()
