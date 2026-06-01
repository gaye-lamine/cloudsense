# CloudSense — Alibaba Cloud Cost Optimization Agent

> **Submission for the Global AI Hackathon Qwen Cloud — Track 4: Autopilot Agent**
>
> CloudSense is an autonomous agent that monitors infrastructure metrics on Alibaba Cloud, detects cost anomalies (such as oversized ECS instances, slow SQL queries, or memory leaks), generates pull requests for automatic remediation, and provides a Human-in-the-loop (HITL) validation dashboard before deploying any cost-saving configurations.

---

## 🚀 Key Features

*   **Continuous Autonomous Monitoring**: Fetches real-time infrastructure metrics from Alibaba CloudMonitor (CPU, Memory, Cost, Egress) and RDS.
*   **Deep Reasoning with Qwen**: Leverages `qwen-plus` via DashScope to perform structural anomaly detection and analyze the root causes of cost anomalies.
*   **Automated Remediation (PRs)**: Dynamically writes and submits pull requests to GitHub to downsize instances or update optimization configurations.
*   **Human-in-the-loop (HITL) Verification**: Interactive dashboard showing the agent's chain-of-thought reasoning, estimated monthly savings in USD, and a single-click "Approve / Reject" gate.
*   **Robust MCP Server Integrations**: Built natively using the Model Context Protocol (MCP) to decouple core agent reasoning from resource operations.
*   **Measurable ROI**: Visualizes real-time and projected savings in a premium, responsive dashboard.

---

## 📊 System Architecture

For a detailed view of the data flow and sequence diagrams, see [docs/architecture.md](docs/architecture.md).

```
                      +-----------------------------+
                      |   Alibaba CloudMonitor API  |
                      +--------------+--------------+
                                     |
                                     v [Metric Snapshots]
+-----------------+   +--------------+--------------+   +-------------------+
|  React Dashboard| < |     FastAPI Agent Core      | > |  Qwen Cloud API   |
|   (HITL UI)     |   |   (WebSocket Orchestrator)  |   | (OpenAI-compatible|
+-----------------+   +--------------+--------------+   +-------------------+
                                     |
                                     v [Executes Tools via MCP]
                      +--------------+--------------+
                      |    MCP Tool Registry Server |
                      +--------------+--------------+
                                     |
             +-----------------------+-----------------------+
             |                       |                       |
             v                       v                       v
+------------+------------+ +--------+---------+ +-----------+-----------+
| fetch_metrics()         | | generate_fix()   | | deploy_fix()            |
| (Alibaba SDK)           | | (GitHub PR API)  | | (Infrastructure Deploy) |
+-------------------------+ +------------------+ +-------------------------+
```

---

## 🛠️ Tech Stack

*   **Backend**: Python 3.12, FastAPI, MCP Server (`mcp` library), SQLAlchemy, Uvicorn, OpenAI SDK.
*   **Frontend**: React, Vite, Tailwind CSS, WebSockets.
*   **Infrastructure & Deployment**: Alibaba Cloud ECS, Alibaba CloudMonitor, Alibaba RDS, Docker.
*   **AI Reasoning**: Qwen-Plus via Alibaba DashScope.

---

## 📦 Quick Start

### 1. Prerequisites
*   Python 3.12+
*   Node.js 18+
*   Alibaba Cloud Account with CloudMonitor / ECS metrics active.
*   Qwen Cloud (DashScope) API Key.

### 2. Installation & Setup
1.  Clone the repository and navigate to the project directory:
    ```bash
    git clone https://github.com/yourusername/cloudsense.git
    cd cloudsense
    ```
2.  Set up environment variables:
    ```bash
    cp .env.example .env
    # Edit the .env file with your API credentials
    ```
3.  Install Python dependencies and run the backend server:
    ```bash
    pip install -r requirements.txt
    python -m backend.main
    ```
4.  Install frontend dependencies and run the client:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

---

## ⚡ MCP Tools Exposure

CloudSense operates under the Model Context Protocol (MCP). The following tools are exposed directly to the Qwen agent:

1.  `fetch_metrics(service, time_range)`: Hits Alibaba CloudMonitor to download CPU, memory, and billing metrics.
2.  `analyze_anomaly(metric_data)`: Instructs Qwen to output a structured root-cause analysis report.
3.  `generate_fix(anomaly_report)`: Rewrites config files or scripts and creates a GitHub pull request.
4.  `estimate_savings(fix)`: Projects the exact USD reduction in monthly spend.
5.  `deploy_fix(pr_id)`: **Critical gate** — Runs the ECS resizing or config deployment only after manual operator confirmation.

---

## 📜 Alibaba Cloud Integration Proof

As required by the official hackathon rules, explicit API usage verification is provided:
*   **Proof Location**: [infra/alibaba_cloud_proof.py](infra/alibaba_cloud_proof.py)
*   This script verifies the connection to the Alibaba CloudMonitor client, queries running ECS instances, and completes a round-trip test with the Qwen reasoning engine.
