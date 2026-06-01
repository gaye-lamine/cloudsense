import React, { useState, useEffect, useRef } from "react";
import {
  Activity,
  AlertTriangle,
  TrendingDown,
  DollarSign,
  Play,
  CheckCircle,
  Terminal,
  Cpu,
  Database,
  HardDrive,
  ArrowRight,
  Sparkles,
  GitPullRequest,
  Check,
  X,
  RefreshCw,
  ExternalLink,
  Settings
} from "lucide-react";

export default function App() {
  const [stats, setStats] = useState({
    total_anomalies_detected: 0,
    total_anomalies_resolved: 0,
    pending_approvals: 0,
    active_monitored_instances: 4,
    total_monthly_spend: 577.44,
    projected_monthly_savings: 0.0,
    actual_savings_realized: 0.0,
  });

  const [anomalies, setAnomalies] = useState([]);
  const [fixes, setFixes] = useState([]);
  const [logs, setLogs] = useState([
    {
      timestamp: new Date().toISOString(),
      type: "status_change",
      message: "CloudSense core system initialized. Awaiting Alibaba Cloud connection...",
    },
  ]);
  const [isScanning, setIsScanning] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");

  // Custom configurations settings
  const [configSettings, setConfigSettings] = useState({
    cpu_utilization_threshold: "10.0",
    slow_query_threshold: "50",
    egress_egress_alert_mb: "100.0"
  });
  const [showConfigAlert, setShowConfigAlert] = useState(false);
  
  const [connectionStatus, setConnectionStatus] = useState({
    status: "demo",
    message: "Demo Mode: Running with simulated resources. Configure live credentials in .env to connect.",
    ram_user_details: null,
    region: "us-east-1"
  });

  const consoleEndRef = useRef(null);
  const ws = useRef(null);

  // Load state and settings on mount
  useEffect(() => {
    fetchSettings();
    fetchConnectionStatus();
  }, []);

  // Initialize WebSocket connection
  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws`;

    console.log("Connecting to WebSocket:", wsUrl);
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      addLog("status_change", "WebSocket connection established with CloudSense core API.");
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message received:", data);

      if (data.type === "welcome") {
        setAnomalies(data.payload.anomalies || []);
        setFixes(data.payload.fixes || []);
        setStats(data.payload.stats);
        if (data.payload.connection_status) {
          setConnectionStatus(data.payload.connection_status);
        }
      } else {
        // Handle stream update messages
        addLog(data.type, data.message);
        
        // Reset scanning state when complete or failed
        if (data.type === "status_change" && 
            (data.message.includes("completed") || 
             data.message.includes("failed") || 
             data.message.includes("completed."))) {
          setIsScanning(false);
        }
        
        // Reload global states on significant structural events
        if (["anomaly_detected", "tool_call", "tool_output", "status_change"].includes(data.type)) {
          fetchState();
        }
      }
    };

    ws.current.onerror = (err) => {
      console.error("WebSocket error:", err);
      addLog("status_change", "WebSocket connection error. Retrying integration services...");
    };

    ws.current.onclose = () => {
      addLog("status_change", "WebSocket link disconnected. Reconnection scheduled.");
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  // Scroll to bottom of terminal console
  useEffect(() => {
    if (consoleEndRef.current) {
      consoleEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs]);

  const addLog = (type, message) => {
    setLogs((prev) => [...prev, { timestamp: new Date().toISOString(), type, message }]);
  };

  const fetchConnectionStatus = async () => {
    try {
      const res = await fetch("/api/connection-status");
      const data = await res.json();
      setConnectionStatus(data);
    } catch (e) {
      console.error("Failed to load connection status:", e);
    }
  };

  const fetchSettings = async () => {
    try {
      const res = await fetch("/api/settings");
      const data = await res.json();
      setConfigSettings(data);
    } catch (e) {
      console.error("Failed to load settings:", e);
    }
  };

  const saveSettings = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(configSettings)
      });
      if (res.ok) {
        setShowConfigAlert(true);
        setTimeout(() => setShowConfigAlert(false), 3000);
        addLog("status_change", "Operator updated global cost alert thresholds.");
      }
    } catch (e) {
      console.error("Failed to save settings:", e);
    }
  };

  const fetchState = async () => {
    try {
      const resStats = await fetch("/api/stats");
      const dataStats = await resStats.json();
      setStats(dataStats);

      const resAnom = await fetch("/api/anomalies");
      const dataAnom = await resAnom.json();
      setAnomalies(dataAnom);

      const resFixes = await fetch("/api/fixes");
      const dataFixes = await resFixes.json();
      setFixes(dataFixes);

      fetchConnectionStatus();
    } catch (e) {
      console.error("Failed to sync backend state:", e);
    }
  };

  const triggerScan = async () => {
    if (isScanning) return;
    setIsScanning(true);
    try {
      await fetch("/api/scan", { method: "POST" });
      addLog("status_change", "Manual scan cycle triggered by user.");
    } catch (e) {
      console.error("Failed to trigger scan:", e);
      setIsScanning(false);
    }
  };

  const handleHITLAction = async (fixId, action) => {
    try {
      addLog("status_change", `Sending Operator Verification: ${action.toUpperCase()} for ${fixId}`);
      const res = await fetch("/api/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fix_id: fixId, action }),
      });
      if (res.ok) {
        fetchState();
      } else {
        addLog("status_change", `Failed to complete verification decision on backend.`);
      }
    } catch (e) {
      console.error("Error submitting HITL validation:", e);
    }
  };

  // Render highlighted git diff representation
  const renderGitDiff = (diffText) => {
    if (!diffText) return null;
    return diffText.split("\n").map((line, idx) => {
      if (line.startsWith("+")) {
        return <span key={idx} className="diff-line-added">{line}</span>;
      }
      if (line.startsWith("-")) {
        return <span key={idx} className="diff-line-removed">{line}</span>;
      }
      return <span key={idx}>{line}</span>;
    });
  };

  return (
    <div className="app-container">
      {/* Sidebar Section */}
      <aside className="sidebar">
        <div className="brand-section">
          <div className="brand-logo">
            <Cpu />
          </div>
          <span className="brand-name">CloudSense</span>
        </div>

        <ul className="nav-links">
          <li
            className={`nav-item ${activeTab === "dashboard" ? "active" : ""}`}
            onClick={() => setActiveTab("dashboard")}
          >
            <Activity />
            <span>Dashboard</span>
          </li>
          <li
            className={`nav-item ${activeTab === "console" ? "active" : ""}`}
            onClick={() => setActiveTab("console")}
          >
            <Terminal />
            <span>Agent Console</span>
          </li>
          <li
            className={`nav-item ${activeTab === "settings" ? "active" : ""}`}
            onClick={() => setActiveTab("settings")}
          >
            <Settings />
            <span>Threshold Settings</span>
          </li>
        </ul>

        <div className="sidebar-footer">
          <div className="status-badge-container">
            <div className={`pulse-dot ${connectionStatus.status}`} />
            <span>
              {connectionStatus.status === "connected" ? "Live Account Connected" :
               connectionStatus.status === "forbidden_ram" ? "RAM Permission Denied" :
               connectionStatus.status === "invalid_credentials" ? "Invalid Credentials" : "Demo Sandbox Mode"}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-panel">
        
        {/* CONDITIONAL RENDER: DASHBOARD VIEW */}
        {activeTab === "dashboard" && (
          <>
            <header className="dashboard-header">
              <div className="welcome-title">
                <h1>Cloud Optimization Autopilot</h1>
                <p>Autonomous cost optimization for Alibaba Cloud services, gated by human approval.</p>
              </div>

              <button
                className="btn-primary"
                onClick={triggerScan}
                disabled={isScanning || stats.pending_approvals > 0}
              >
                {isScanning ? (
                  <>
                    <RefreshCw className="animate-spin" style={{ animation: "spin 1.5s linear infinite" }} />
                    <span>Scanning Infrastructure...</span>
                  </>
                ) : (
                  <>
                    <Play />
                    <span>Run Audit Cycle</span>
                  </>
                )}
              </button>
            </header>

            {/* Real-time Alibaba Cloud Connection Status Alert */}
            {connectionStatus && (
              <div className={`connection-status-banner ${connectionStatus.status}`}>
                <div className="status-banner-content">
                  <div className="status-banner-icon">
                    {connectionStatus.status === "connected" && <CheckCircle size={20} style={{ color: "hsl(var(--emerald))" }} />}
                    {connectionStatus.status === "forbidden_ram" && <AlertTriangle size={20} style={{ color: "hsl(var(--amber))" }} />}
                    {connectionStatus.status === "invalid_credentials" && <AlertTriangle size={20} style={{ color: "hsl(var(--rose))" }} />}
                    {connectionStatus.status === "demo" && <Settings size={20} style={{ color: "hsl(var(--text-muted))" }} />}
                  </div>
                  <div className="status-banner-text">
                    <div className="status-banner-title">
                      {connectionStatus.status === "connected" && `Connected to Alibaba Cloud (${connectionStatus.region})`}
                      {connectionStatus.status === "forbidden_ram" && `RAM Permissions Required — Alibaba Cloud (${connectionStatus.region})`}
                      {connectionStatus.status === "invalid_credentials" && `Alibaba Cloud Connection Failed`}
                      {connectionStatus.status === "demo" && `Demo Sandbox Mode`}
                    </div>
                    <div className="status-banner-desc">
                      {connectionStatus.message}
                    </div>
                    {connectionStatus.status === "forbidden_ram" && connectionStatus.ram_user_details && (
                      <div className="ram-troubleshoot-box">
                        <strong>Action Required:</strong> Log in to the <strong>Alibaba Cloud Console</strong>, navigate to <strong>RAM &gt; Users &gt; cloudsense-agent</strong>, and attach the following policies:
                        <ul>
                          <li><code className="code-policy">AliyunECSReadOnlyAccess</code> (Allows reading ECS configurations)</li>
                          <li><code className="code-policy">AliyunCloudMonitorReadOnlyAccess</code> (Allows reading resource metrics)</li>
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Global KPI Stats Grid */}
            <section className="stats-grid">
              <div className="kpi-card">
                <div className="kpi-details">
                  <h3>Monthly Cloud Spend</h3>
                  <div className="kpi-value">${stats.total_monthly_spend.toFixed(2)}</div>
                  <span className="kpi-sub" style={{ color: "hsl(var(--text-muted))" }}>Active Telemetry</span>
                </div>
                <div className="kpi-icon">
                  <DollarSign />
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-details">
                  <h3>Projected Monthly Savings</h3>
                  <div className="kpi-value" style={{ color: "hsl(var(--emerald))" }}>
                    +${stats.projected_monthly_savings.toFixed(2)}
                  </div>
                  <span className="kpi-sub">Ready to deploy</span>
                </div>
                <div className="kpi-icon saved">
                  <TrendingDown />
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-details">
                  <h3>Realized Savings (ROI)</h3>
                  <div className="kpi-value" style={{ color: "hsl(var(--secondary))" }}>
                    +${stats.actual_savings_realized.toFixed(2)}
                  </div>
                  <span className="kpi-sub" style={{ color: "hsl(var(--secondary))" }}>Deployed changes</span>
                </div>
                <div className="kpi-icon" style={{ color: "hsl(var(--secondary))", background: "hsl(var(--secondary) / 0.08)" }}>
                  <CheckCircle />
                </div>
              </div>

              <div className="kpi-card">
                <div className="kpi-details">
                  <h3>Pending Approvals</h3>
                  <div className="kpi-value" style={{ color: "hsl(var(--amber))" }}>
                    {stats.pending_approvals}
                  </div>
                  <span className="kpi-sub" style={{ color: "hsl(var(--amber))" }}>Awaiting Human Check</span>
                </div>
                <div className="kpi-icon pending">
                  <AlertTriangle />
                </div>
              </div>
            </section>

            {/* Dashboard Console Preview (Neat, small console) */}
            <section className="console-panel">
              <div className="console-header">
                <h3>
                  <Terminal />
                  <span>Qwen Core Reasoning & Tool Logs</span>
                </h3>
                <span style={{ fontSize: "12px", color: "hsl(var(--text-muted))" }}>Console Preview</span>
              </div>
              <div className="console-output" style={{ height: "140px" }}>
                {logs.slice(-4).map((log, index) => (
                  <div key={index} className={`console-line ${log.type}`}>
                    <span className="console-time">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span style={{ fontWeight: 600, marginRight: "8px" }}>
                      [{log.type.toUpperCase()}]
                    </span>
                    <span>{log.message}</span>
                  </div>
                ))}
                <div ref={consoleEndRef} />
              </div>
            </section>

            {/* Main panels: anomalies list and HITL approval box */}
            <div className="dashboard-sections-grid">
              {/* Anomaly Feed Column */}
              <div className="panel-card">
                <h2 className="panel-title">
                  <AlertTriangle />
                  <span>Detected Cost Anomalies</span>
                </h2>

                <div className="anomaly-list">
                  {anomalies.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px", color: "hsl(var(--text-muted))" }}>
                      <Sparkles size={36} style={{ marginBottom: "12px", color: "hsl(var(--primary))" }} />
                      <p>No anomalies detected. Run an audit cycle to scan Alibaba Cloud.</p>
                    </div>
                  ) : (
                    anomalies.map((anom) => {
                      const associatedFix = fixes.find((f) => f.anomaly_id === anom.id);
                      return (
                        <div key={anom.id} className="anomaly-item">
                          <div className="anomaly-header">
                            <span className="instance-badge">
                              {anom.service_type === "ECS" ? (
                                <Cpu size={14} style={{ marginRight: "4px" }} />
                              ) : anom.service_type === "EBS" ? (
                                <HardDrive size={14} style={{ marginRight: "4px" }} />
                              ) : (
                                <Database size={14} style={{ marginRight: "4px" }} />
                              )}
                              {anom.instance_id}
                            </span>
                            <span className={`severity-badge ${anom.severity}`}>
                              {anom.severity}
                            </span>
                          </div>

                          <div className="anomaly-details">
                            <p style={{ fontWeight: 500, color: "white", marginBottom: "6px" }}>
                              {anom.root_cause}
                            </p>
                            <p style={{ fontSize: "13px" }}>{anom.impact_description}</p>
                            
                            <div className="remediation-box">
                              <ArrowRight size={14} />
                              <span>Remediation action: <strong>{anom.remediation_action}</strong></span>
                            </div>

                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                              <span className="saving-tag">
                                <DollarSign size={16} />
                                <span>Est. Savings: +${anom.estimated_monthly_savings.toFixed(2)}/mo</span>
                              </span>

                              {associatedFix && (
                                <span style={{
                                  fontSize: "12px",
                                  fontWeight: 600,
                                  textTransform: "uppercase",
                                  padding: "4px 8px",
                                  borderRadius: "4px",
                                  color: associatedFix.status === "deployed" ? "hsl(var(--emerald))" :
                                         associatedFix.status === "rejected" ? "hsl(var(--rose))" : "hsl(var(--amber))"
                                }}>
                                  Status: {associatedFix.status}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Human-in-the-loop Gate Column */}
              <div>
                <div className="panel-card" style={{ height: "100%" }}>
                  <h2 className="panel-title">
                    <GitPullRequest />
                    <span>HITL Validation Control</span>
                  </h2>

                  {fixes.filter(f => f.status === "pending").length === 0 ? (
                    <div style={{ textAlign: "center", padding: "40px", color: "hsl(var(--text-muted))" }}>
                      <CheckCircle size={36} style={{ marginBottom: "12px", color: "hsl(var(--emerald))" }} />
                      <p>All optimization requests have been processed. Systems fully optimized.</p>
                    </div>
                  ) : (
                    fixes.filter(f => f.status === "pending").map((fix) => (
                      <div key={fix.id} className="anomaly-item approval-card">
                        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                          <GitPullRequest size={18} style={{ color: "hsl(var(--amber))" }} />
                          <span style={{ fontWeight: 600, fontSize: "14px", color: "white" }}>
                            PR #{fix.pr_number} Optimization
                          </span>
                        </div>

                        <p style={{ fontSize: "13px", color: "hsl(var(--text-muted))", marginBottom: "8px" }}>
                          CloudSense agent has drafted infrastructure scaling code changes. Review git diff below:
                        </p>

                        <div className="git-diff-container">
                          {renderGitDiff(fix.diff_content)}
                        </div>

                        <div style={{ display: "flex", gap: "10px", marginTop: "12px" }}>
                          <a 
                            href={fix.pr_url} 
                            target="_blank" 
                            rel="noreferrer"
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "4px",
                              fontSize: "12px",
                              color: "hsl(var(--secondary))",
                              textDecoration: "none"
                            }}
                          >
                            <span>Review PR on GitHub</span>
                            <ExternalLink size={12} />
                          </a>
                        </div>

                        <div className="action-buttons">
                          <button
                            className="btn-approve"
                            onClick={() => handleHITLAction(fix.id, "approve")}
                          >
                            <Check size={16} />
                            <span>Approve & Deploy</span>
                          </button>
                          <button
                            className="btn-reject"
                            onClick={() => handleHITLAction(fix.id, "reject")}
                          >
                            <X size={16} />
                            <span>Reject</span>
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Vector SVG ROI Analytics chart */}
            <section className="panel-card" style={{ marginTop: "24px" }}>
              <h2 className="panel-title">
                <TrendingDown />
                <span>Cost Optimization Vector — CloudSense Real-time ROI (USD)</span>
              </h2>
              
              <div style={{ position: "relative", width: "100%", height: "260px", background: "#030712", borderRadius: "12px", overflow: "hidden", border: "1px solid hsl(var(--border-light))", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <svg viewBox="0 0 800 220" style={{ width: "92%", height: "82%" }}>
                  {/* Horizontal baseline grids */}
                  <line x1="0" y1="180" x2="800" y2="180" stroke="hsl(var(--border-light))" strokeWidth="1" strokeDasharray="4 4" />
                  <line x1="0" y1="120" x2="800" y2="120" stroke="hsl(var(--border-light))" strokeWidth="1" strokeDasharray="4 4" />
                  <line x1="0" y1="60" x2="800" y2="60" stroke="hsl(var(--border-light))" strokeWidth="1" strokeDasharray="4 4" />
                  
                  {/* Area under the curves */}
                  <path d="M 0,60 L 200,60 L 400,60 L 600,140 L 800,140 L 800,220 L 0,220 Z" fill="url(#grad-spend)" opacity="0.15" />
                  <path d="M 0,200 L 200,200 L 400,200 L 600,120 L 800,120 L 800,220 L 0,220 Z" fill="url(#grad-savings)" opacity="0.15" />

                  {/* Line 1: spend Trend (Descending) */}
                  <path d="M 0,60 L 200,60 L 400,60 L 600,140 L 800,140" fill="none" stroke="hsl(var(--rose))" strokeWidth="3" strokeLinecap="round" />
                  
                  {/* Line 2: Savings ROI (Ascending) */}
                  <path d="M 0,200 L 200,200 L 400,200 L 600,120 L 800,120" fill="none" stroke="hsl(var(--emerald))" strokeWidth="3" strokeLinecap="round" strokeDasharray="3 3" />

                  {/* Markers */}
                  <circle cx="400" cy="60" r="5" fill="hsl(var(--rose))" stroke="white" strokeWidth="2" />
                  <circle cx="600" cy="140" r="5" fill="hsl(var(--rose))" stroke="white" strokeWidth="2" />
                  <circle cx="600" cy="120" r="5" fill="hsl(var(--emerald))" stroke="white" strokeWidth="2" />

                  {/* Text legends */}
                  <text x="20" y="40" fill="hsl(var(--text-muted))" fontSize="12" fontWeight="500">Initial spend: $577.44/mo</text>
                  <text x="610" y="160" fill="hsl(var(--rose))" fontSize="12" fontWeight="700">Optimized spend: ${ (577.44 - stats.actual_savings_realized).toFixed(2) }/mo</text>
                  <text x="610" y="105" fill="hsl(var(--emerald))" fontSize="12" fontWeight="700">Realized: +${stats.actual_savings_realized.toFixed(2)}/mo</text>

                  {/* Gradients definitions */}
                  <defs>
                    <linearGradient id="grad-spend" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="hsl(var(--rose))" />
                      <stop offset="100%" stopColor="transparent" />
                    </linearGradient>
                    <linearGradient id="grad-savings" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="hsl(var(--emerald))" />
                      <stop offset="100%" stopColor="transparent" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              
              <div style={{ display: "flex", justifyContent: "space-between", marginTop: "12px", fontSize: "12px", color: "hsl(var(--text-muted))" }}>
                <span>Phase 1: Baselines setup</span>
                <span>Phase 2: CloudSense Scan (Anomalies logged)</span>
                <span>Phase 3: Automated remediation applied (HITL Deployed)</span>
              </div>
            </section>
          </>
        )}

        {/* CONDITIONAL RENDER: FULL AGENT CONSOLE VIEW */}
        {activeTab === "console" && (
          <div className="panel-card" style={{ height: "calc(100vh - 80px)", display: "flex", flexDirection: "column", animation: "fadeIn 0.2s ease" }}>
            <h2 className="panel-title" style={{ borderBottom: "1px solid hsl(var(--border-light))", paddingBottom: "16px", marginBottom: "16px" }}>
              <Terminal />
              <span>Full Agent Console & Chain-of-Thought Stream</span>
            </h2>
            
            <div className="console-output" style={{ flexGrow: 1, height: "100%", maxHeight: "none", background: "#020617", padding: "20px", borderRadius: "12px" }}>
              {logs.map((log, index) => (
                <div key={index} className={`console-line ${log.type}`}>
                  <span className="console-time">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span style={{ fontWeight: 600, marginRight: "8px" }}>
                    [{log.type.toUpperCase()}]
                  </span>
                  <span>{log.message}</span>
                </div>
              ))}
              <div ref={consoleEndRef} />
            </div>
          </div>
        )}

        {/* CONDITIONAL RENDER: CONFIGURATION SETTINGS VIEW */}
        {activeTab === "settings" && (
          <div className="panel-card" style={{ maxWidth: "800px", margin: "0 auto", animation: "fadeIn 0.2s ease" }}>
            <h2 className="panel-title" style={{ borderBottom: "1px solid hsl(var(--border-light))", paddingBottom: "16px" }}>
              <Settings />
              <span>Operational Cost Alert Thresholds</span>
            </h2>

            {showConfigAlert && (
              <div style={{
                background: "hsl(var(--emerald) / 0.1)",
                color: "hsl(var(--emerald))",
                border: "1px solid hsl(var(--emerald) / 0.3)",
                borderRadius: "8px",
                padding: "12px 16px",
                fontSize: "14px",
                fontWeight: 600,
                marginBottom: "20px",
                display: "flex",
                alignItems: "center",
                gap: "8px"
              }}>
                <CheckCircle size={16} />
                <span>Configuration setting values persisted in SQLite database successfully!</span>
              </div>
            )}

            <form onSubmit={saveSettings} style={{ display: "flex", flexDirection: "column", gap: "24px", marginTop: "20px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontSize: "14px", fontWeight: 600, color: "white" }}>
                  Low CPU Utilization Alert Boundary (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={configSettings.cpu_utilization_threshold || ""}
                  onChange={(e) => setConfigSettings({ ...configSettings, cpu_utilization_threshold: e.target.value })}
                  style={{
                    background: "hsl(var(--bg-dark))",
                    border: "1px solid hsl(var(--border-light))",
                    borderRadius: "8px",
                    color: "white",
                    padding: "10px 14px",
                    fontSize: "14px",
                    outline: "none"
                  }}
                  required
                />
                <span style={{ fontSize: "12px", color: "hsl(var(--text-muted))" }}>
                  Trigger cost anomaly audit warning if ECS instance averages CPU under this percentage boundary (Default: 10%).
                </span>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontSize: "14px", fontWeight: 600, color: "white" }}>
                  RDS Slow Query Anomaly Trigger Boundary (Count)
                </label>
                <input
                  type="number"
                  value={configSettings.slow_query_threshold || ""}
                  onChange={(e) => setConfigSettings({ ...configSettings, slow_query_threshold: e.target.value })}
                  style={{
                    background: "hsl(var(--bg-dark))",
                    border: "1px solid hsl(var(--border-light))",
                    borderRadius: "8px",
                    color: "white",
                    padding: "10px 14px",
                    fontSize: "14px",
                    outline: "none"
                  }}
                  required
                />
                <span style={{ fontSize: "12px", color: "hsl(var(--text-muted))" }}>
                  Maximum slow sequential scans allowed before flagging RDS instance scale anomalies (Default: 50).
                </span>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontSize: "14px", fontWeight: 600, color: "white" }}>
                  Egress Egress Monthly Cost Alert Limit (MB)
                </label>
                <input
                  type="number"
                  step="1"
                  value={configSettings.egress_egress_alert_mb || ""}
                  onChange={(e) => setConfigSettings({ ...configSettings, egress_egress_alert_mb: e.target.value })}
                  style={{
                    background: "hsl(var(--bg-dark))",
                    border: "1px solid hsl(var(--border-light))",
                    borderRadius: "8px",
                    color: "white",
                    padding: "10px 14px",
                    fontSize: "14px",
                    outline: "none"
                  }}
                  required
                />
                <span style={{ fontSize: "12px", color: "hsl(var(--text-muted))" }}>
                  Trigger egress costs alerts when uncompressed data files egress exceeds this sizing boundary (Default: 100MB).
                </span>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "12px" }}>
                <button type="submit" className="btn-primary" style={{ padding: "10px 24px" }}>
                  <Check size={16} />
                  <span>Save Operations Settings</span>
                </button>
              </div>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
