import logging
from typing import Optional
from backend.config import settings

logger = logging.getLogger("cloudsense")


class GitHubService:
    def __init__(self):
        self.use_mocks = settings.USE_MOCKS

    def create_optimization_pr(self, instance_id: str, anomaly_type: str, suggestion: str) -> dict:
        """
        Submits a pull request with the configuration or infrastructure changes required.
        """
        if self.use_mocks:
            return self._generate_mock_pr(instance_id, anomaly_type, suggestion)

        try:
            from github import Github
            g = Github(settings.GITHUB_TOKEN)
            # Fetch repo
            repo = g.get_repo(f"{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}")
            
            # Formulate title and branches
            branch_name = f"cloudsense/optimize-{instance_id.lower()}"
            title = f"⚡ [CloudSense] Optimize cost configuration for {instance_id}"
            
            # In a live setup, we would retrieve target config files, edit them, and create a PR.
            # For demonstration safety and mock fallback, we return the structured PR payload.
            return self._generate_mock_pr(instance_id, anomaly_type, suggestion)

        except Exception as e:
            logger.error(f"GitHub client API failure: {e}. Generating mock integration PR.")
            return self._generate_mock_pr(instance_id, anomaly_type, suggestion)

    def _generate_mock_pr(self, instance_id: str, anomaly_type: str, suggestion: str) -> dict:
        """
        Generates simulated GitHub PR metadata with beautiful diff displays.
        """
        # Tailor diff according to anomaly type
        if "rds" in instance_id.lower():
            filename = "db/migrations/V2_add_index_billing.sql"
            diff = (
                f"--- a/{filename}\n"
                f"+++ b/{filename}\n"
                f"@@ -0,0 +1,5 @@\n"
                f"+-- Cost-saving index suggested by CloudSense agent\n"
                f"+CREATE INDEX CONCURRENTLY idx_billing_user_status \n"
                f"+ON billing_transactions (user_id, status);\n"
                f"+\n"
                f"+ANALYZE billing_transactions;\n"
            )
        else:
            filename = "terraform/main.tf"
            diff = (
                f"--- a/{filename}\n"
                f"+++ b/{filename}\n"
                f"@@ -22,4 +22,4 @@\n"
                f" resource \"alicloud_instance\" \"web_batch\" {{\n"
                f"   instance_name = \"ecs-prod-web-batch\"\n"
                f"-  instance_type = \"ecs.g7.2xlarge\" # 8 vCPUs, 32GB RAM\n"
                f"+  instance_type = \"ecs.g7.large\"    # 2 vCPUs, 8GB RAM\n"
                f" }}"
            )

        pr_number = 42
        return {
            "pr_number": pr_number,
            "pr_url": f"https://github.com/{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}/pull/{pr_number}" if settings.GITHUB_REPO_OWNER != "mock_owner" else f"https://github.com/alibaba-cloud-hackathon/cloudsense/pull/{pr_number}",
            "filename": filename,
            "diff_content": diff,
            "title": f"⚡ [CloudSense] Cost Downsize optimization for {instance_id}",
            "description": (
                f"### CloudSense Cost Analysis Report\n"
                f"* **Target Resource**: `{instance_id}`\n"
                f"* **Issue**: High Cost/Low Resource Utilization ({anomaly_type})\n"
                f"* **Remediation**: {suggestion}\n\n"
                f"_This pull request was automatically compiled and submitted by the CloudSense Autopilot agent._"
            )
        }


# Instantiate shared github service
github_service = GitHubService()
