# Devpost Submission — CloudSense

## Project Info
* **Project Name**: CloudSense
* **Tagline**: Autonomous Cost Optimization & Auto-Billing Auditor for Alibaba Cloud, gated by manual validation.
* **Track**: Track 4: Autopilot Agent
* **API Used**: Qwen Cloud (DashScope)
* **API Base URL**: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

---

## ⚡ The Elevator Pitch

CloudSense is an autonomous cloud optimization autopilot. It continuously monitors your infrastructure metrics on Alibaba Cloud, leverages Qwen-Plus's advanced reasoning capabilities to detect cost anomalies (oversized ECS nodes, unindexed RDS tables, egress leaks), drafts the exact infrastructure configuration correction, submits a Git Pull Request, and alerts the operator on an interactive Human-in-the-loop dashboard. **No scaling or resizing is deployed without manual validation.**

---

## 🛠️ The Architecture

```
Alibaba CloudMonitor API
       │ [Metric Telemetry]
       ▼
 FastAPI Agent Core ◄───[WebSocket Chain-of-Thought]───► React HITL Dashboard
       │
       ├─► Qwen Cloud API (via OpenAI-Compatible SDK)
       │     └─► response_format={"type": "json_object"} (Structured Output)
       │
       └─► Custom FastMCP Server
             ├─► fetch_metrics()
             ├─► analyze_anomaly()
             ├─► generate_fix() (GitHub PR API)
             ├─► estimate_savings()
             └─► deploy_fix() (Alibaba ECS Scale API)
```

---

## 🧠 Strategic Qwen Cloud API Integrations (How we satisfy the 30% Tech Depth)

1. **Alibaba Compatible-Mode Base URL**: We configure the official OpenAI Python SDK to query `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` directly.
2. **Platform-Native Structured Outputs**: We leverage the official Qwen parameters by enforcing `response_format={"type": "json_object"}`. This guarantees that Qwen's cost analysis conforms perfectly to our Pydantic schemas, eliminating string parsing vulnerabilities.
3. **Multi-Agent Tool Calling (MCP)**: Core actions are wrapped inside FastMCP tool definitions, separating core LLM reasoning from file writing, GitHub PR submissions, and server resizing execution.

---

## 📜 Alibaba Cloud Proof of Deployment

* **Proof Location in Repo**: [/infra/alibaba_cloud_proof.py](file:///Users/mac/.gemini/antigravity/scratch/cloudsense/infra/alibaba_cloud_proof.py)
* **What it does**: This script explicitly utilizes the official `alibabacloud-cms` and `alibabacloud-ecs` python SDKs to initialize connections, verify CloudMonitor dimensions, list running ECS instances, and complete a secure chat completion loop with DashScope.
