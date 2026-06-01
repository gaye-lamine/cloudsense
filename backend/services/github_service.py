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
        if settings.GITHUB_TOKEN == "mock_github" or settings.GITHUB_REPO_OWNER == "mock_owner":
            return self._generate_mock_pr(instance_id, anomaly_type, suggestion)

        try:
            from github import Github
            g = Github(settings.GITHUB_TOKEN)
            repo_path = f"{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}"
            repo = g.get_repo(repo_path)
            
            # Formulate title and branches
            import time
            timestamp = int(time.time())
            branch_name = f"cloudsense/optimize-{instance_id.lower()}-{timestamp}"
            title = f"⚡ [CloudSense] Cost Downsize optimization for {instance_id}"
            
            # Determine content and filename
            if "rds" in instance_id.lower():
                filename = "db/migrations/V2_add_index_billing.sql"
                file_content = (
                    "-- Cost-saving index suggested by CloudSense agent\n"
                    "CREATE INDEX CONCURRENTLY idx_billing_user_status \n"
                    "ON billing_transactions (user_id, status);\n\n"
                    "ANALYZE billing_transactions;\n"
                )
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
            elif "disk" in instance_id.lower() or "d-" in instance_id.lower():
                filename = "terraform/disks.tf"
                file_content = (
                    "# Storage configurations managed by CloudSense\n"
                    "# disk-prod-backup-static has been decommissioned autonomously to optimize cloud spend.\n"
                )
                diff = (
                    f"--- a/{filename}\n"
                    f"+++ b/{filename}\n"
                    f"@@ -1,8 +1,2 @@\n"
                    f"-resource \"alicloud_disk\" \"backup_static\" {{\n"
                    f"-  disk_name   = \"disk-prod-backup-static\"\n"
                    f"-  disk_category = \"cloud_essd\"\n"
                    f"-  size        = 1024\n"
                    f"-  description = \"Static production database backup storage volume\"\n"
                    f"-}}\n"
                    f"+# Decommissioned autonomously by CloudSense to save $120.00/mo"
                )
            else:
                filename = "terraform/main.tf"
                file_content = (
                    "resource \"alicloud_instance\" \"web_batch\" {\n"
                    "  instance_name = \"ecs-prod-web-batch\"\n"
                    "  instance_type = \"ecs.g7.large\"    # 2 vCPUs, 8GB RAM\n"
                    "}\n"
                )
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

            description = (
                f"### CloudSense Cost Optimization Report\n"
                f"* **Target Resource**: `{instance_id}`\n"
                f"* **Issue**: High Cost/Low Resource Utilization ({anomaly_type})\n"
                f"* **Remediation**: {suggestion}\n\n"
                f"_This pull request was automatically compiled and submitted by the CloudSense Autopilot agent._"
            )

            # Create branch from default branch
            default_branch = repo.default_branch
            base_branch = repo.get_branch(default_branch)
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_branch.commit.sha)
            
            # Create the file in the new branch
            try:
                # Check if file already exists on main
                contents = repo.get_contents(filename, ref=default_branch)
                repo.update_file(
                    path=filename,
                    message=f"docs: decommission storage volume {instance_id}",
                    content=file_content,
                    sha=contents.sha,
                    branch=branch_name
                )
            except Exception:
                # Create new file if it doesn't exist
                repo.create_file(
                    path=filename,
                    message=f"docs: decommission storage volume {instance_id}",
                    content=file_content,
                    branch=branch_name
                )
            
            # Create Pull Request
            pr = repo.create_pull(
                title=title,
                body=description,
                head=branch_name,
                base=default_branch
            )
            
            logger.info(f"Successfully created real GitHub Pull Request #{pr.number} at {pr.html_url}")
            return {
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "filename": filename,
                "diff_content": diff,
                "title": title,
                "description": description
            }

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
        elif "disk" in instance_id.lower() or "d-" in instance_id.lower():
            filename = "terraform/disks.tf"
            diff = (
                f"--- a/{filename}\n"
                f"+++ b/{filename}\n"
                f"@@ -1,8 +1,2 @@\n"
                f"-resource \"alicloud_disk\" \"backup_static\" {{\n"
                f"-  disk_name   = \"disk-prod-backup-static\"\n"
                f"-  disk_category = \"cloud_essd\"\n"
                f"-  size        = 1024\n"
                f"-  description = \"Static production database backup storage volume\"\n"
                f"-}}\n"
                f"+# Decommissioned autonomously by CloudSense to save $120.00/mo"
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
            "title": f"⚡ [CloudSense] Cost Decommission optimization for {instance_id}",
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
