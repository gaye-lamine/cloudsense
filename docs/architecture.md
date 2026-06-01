# CloudSense Architecture

## System Overview

CloudSense is an autonomous Alibaba Cloud cost optimization agent built on Qwen Cloud (Track 4: Autopilot Agent). It continuously monitors infrastructure metrics, detects cost anomalies using Qwen's reasoning capabilities, generates fixes, and requires human approval before deploying changes.

## Architecture Diagram

```mermaid
graph TB
    subgraph "Data Sources"
        CM["☁️ Alibaba CloudMonitor<br/>(ARMS / CMS API)"]
        ECS["🖥️ Alibaba ECS<br/>(Instance Metrics)"]
        RDS["🗄️ Alibaba RDS<br/>(Query Performance)"]
    end

    subgraph "Backend — FastAPI on Alibaba Cloud ECS"
        direction TB
        API["🔌 FastAPI Server<br/>REST + WebSocket"]
        
        subgraph "Agent Core"
            ORCH["🧠 Agent Orchestrator<br/>(Main Decision Loop)"]
            QWEN["🤖 Qwen Cloud API<br/>via OpenAI SDK<br/>dashscope-intl.aliyuncs.com"]
        end
        
        subgraph "MCP Server"
            MCP["⚙️ MCP Tool Registry"]
            T1["fetch_metrics()"]
            T2["analyze_anomaly()"]
            T3["generate_fix()"]
            T4["estimate_savings()"]
            T5["deploy_fix()"]
        end
        
        DB["💾 SQLite/PostgreSQL<br/>(Anomaly History)"]
        GH["🔗 GitHub API<br/>(PR Generation)"]
    end

    subgraph "Frontend — React + Vite"
        DASH["📊 Dashboard"]
        METRICS["📈 Metrics Panel<br/>(Real-time Charts)"]
        COT["💭 Chain-of-Thought<br/>(Agent Reasoning View)"]
        HITL["✅ HITL Approval Cards<br/>(Human Validation)"]
        ROI["💰 Savings Tracker<br/>(ROI Visualization)"]
    end

    CM -->|"Metrics API"| T1
    ECS -->|"Instance API"| T1
    RDS -->|"Slow Query Logs"| T1
    
    T1 --> ORCH
    ORCH <-->|"Reasoning"| QWEN
    ORCH --> T2
    T2 --> T3
    T3 --> T4
    T4 -->|"Awaits Approval"| HITL
    HITL -->|"Approved"| T5
    
    T3 --> GH
    ORCH --> DB
    
    API <-->|"WebSocket"| DASH
    DASH --> METRICS
    DASH --> COT
    DASH --> HITL
    DASH --> ROI

    style QWEN fill:#6366f1,stroke:#4f46e5,color:#fff
    style HITL fill:#f59e0b,stroke:#d97706,color:#fff
    style MCP fill:#10b981,stroke:#059669,color:#fff
    style ORCH fill:#8b5cf6,stroke:#7c3aed,color:#fff
```

## Data Flow

```mermaid
sequenceDiagram
    participant CM as CloudMonitor
    participant Agent as Qwen Agent
    participant MCP as MCP Tools
    participant DB as Database
    participant WS as WebSocket
    participant UI as Dashboard
    participant Human as Operator

    loop Every 5 minutes
        Agent->>MCP: fetch_metrics(all_services, last_5m)
        MCP->>CM: Query Alibaba CMS API
        CM-->>MCP: Raw metrics (CPU, memory, cost, queries)
        MCP-->>Agent: Structured MetricSnapshot
    end

    Agent->>Agent: Detect anomaly (cost spike, slow query, oversized instance)
    Agent->>MCP: analyze_anomaly(metric_data)
    MCP->>Agent: AnomalyReport with severity & root cause

    Agent->>WS: Push chain-of-thought reasoning
    WS->>UI: Display reasoning in real-time

    Agent->>MCP: generate_fix(anomaly_report)
    MCP-->>Agent: ProposedFix (code diff, config change)

    Agent->>MCP: estimate_savings(fix)
    MCP-->>Agent: SavingsEstimate ($X/month)

    Agent->>DB: Store anomaly + proposed fix
    Agent->>WS: Push ApprovalRequest
    WS->>UI: Render HITL ApprovalCard

    Human->>UI: Review reasoning + approve/reject
    UI->>WS: Send approval decision
    WS->>Agent: Approval received

    alt Approved
        Agent->>MCP: deploy_fix(fix_id)
        MCP-->>Agent: Deployment confirmation
        Agent->>WS: Push success notification
        Agent->>DB: Update status → deployed
    else Rejected
        Agent->>DB: Update status → rejected
        Agent->>WS: Push rejection logged
    end
```

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Integration | OpenAI SDK → Qwen Cloud | API-compatible, zero custom wrappers needed |
| Agent Framework | Custom orchestrator | Full control over tool calling loop, MCP native |
| Real-time Comms | WebSocket | Live chain-of-thought streaming to dashboard |
| MCP Protocol | Custom MCP server | Required by judging criteria (MCP integrations) |
| Database | SQLite (demo) / PostgreSQL (prod) | Lightweight for hackathon, swappable |
| Frontend | React + Vite | Fast dev cycle, modern tooling |
| Deployment | Docker on Alibaba ECS | Matches hackathon requirement |

## MCP Tools Specification

| Tool | Input | Output | Side Effects |
|------|-------|--------|-------------|
| `fetch_metrics` | service: str, time_range: str | MetricSnapshot[] | None (read-only) |
| `analyze_anomaly` | metric_data: MetricSnapshot | AnomalyReport | None (Qwen reasoning) |
| `generate_fix` | anomaly: AnomalyReport | ProposedFix | Creates GitHub PR |
| `estimate_savings` | fix: ProposedFix | SavingsEstimate | None (calculation) |
| `deploy_fix` | fix_id: str | DeployResult | **Deploys change** (HITL gated) |
