"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Upload, FileCode, Settings, Zap, CheckCircle2, XCircle, 
  Loader2, Play, ArrowRight, Download, RefreshCw, Network, 
  AlertTriangle, ExternalLink, Code2, Terminal, HelpCircle
} from "lucide-react";

interface Step {
  index: number;
  name: string;
  description: string;
  status: "pending" | "running" | "completed" | "failed";
}

interface LogEntry {
  timestamp: number;
  message: string;
}

interface RepairAttempt {
  attempt: number;
  type: string;
  description: string;
  status: string;
}

interface CodeFile {
  name: string;
  path: string;
  content: string;
}

interface NavigationNode {
  id: string;
  label: string;
  type: string;
  entryPoint: boolean;
}

interface NavigationEdge {
  source: string;
  target: string;
  action: string;
  transition: string;
}

interface NavigationGraph {
  nodes: NavigationNode[];
  edges: NavigationEdge[];
}

interface UnsupportedFeature {
  feature: string;
  details: string;
  ios_alternative: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
}

interface JobData {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed";
  current_step: number;
  total_steps: number;
  logs: LogEntry[];
  quality_score: number;
  repair_attempts: RepairAttempt[];
  build_status: "pending" | "success" | "failed";
  testing_status: "pending" | "passed" | "failed";
  metadata: {
    app_name?: string;
    package_name?: string;
    version_name?: string;
    target_sdk?: string;
    file_size_bytes?: number;
    estimated_conversion_time_seconds?: number;
  };
  zip_filename?: string;
  steps: Step[];
}

export default function Dashboard() {
  // State
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<JobData | null>(null);
  
  // Code comparison state
  const [sourceFiles, setSourceFiles] = useState<{ android: CodeFile[]; ios: CodeFile[] }>({ android: [], ios: [] });
  const [selectedAndroidFile, setSelectedAndroidFile] = useState<CodeFile | null>(null);
  const [selectedIosFile, setSelectedIosFile] = useState<CodeFile | null>(null);
  const [activeTab, setActiveTab] = useState<"code" | "architecture" | "reports" | "healing">("code");
  const [codePair, setCodePair] = useState<"login" | "home">("login");

  // WebSocket ref
  const ws = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [job?.logs]);

  // Connect WebSockets when jobId changes
  useEffect(() => {
    if (!jobId) return;

    // Connect to WebSocket
    const wsUrl = `ws://${window.location.hostname}:8000/api/ws/${jobId}`;
    console.log(`Connecting to WebSocket: ${wsUrl}`);
    const socket = new WebSocket(wsUrl);
    ws.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connection established");
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === "state") {
          const updatedJob = message.data as JobData;
          setJob(updatedJob);
          
          // Trigger file fetch if completed
          if (updatedJob.status === "completed" || updatedJob.current_step >= 6) {
             fetchJobFiles(jobId);
          }
        } else if (message.type === "log") {
          const logEntry = message.data as LogEntry;
          setJob((prev) => {
            if (!prev) return null;
            return {
              ...prev,
              logs: [...prev.logs, logEntry]
            };
          });
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [jobId]);

  // Fetch generated files
  const fetchJobFiles = async (id: string) => {
    try {
      const res = await fetch(`http://${window.location.hostname}:8000/api/job/${id}/files`);
      if (res.ok) {
        const data = await res.json();
        setSourceFiles(data);
        
        // Select initial file pair
        if (data.android.length > 0) {
          const loginAct = data.android.find((f: CodeFile) => f.name.includes("LoginActivity"));
          setSelectedAndroidFile(loginAct || data.android[0]);
        }
        if (data.ios.length > 0) {
          const loginView = data.ios.find((f: CodeFile) => f.name.includes("LoginView"));
          setSelectedIosFile(loginView || data.ios[0]);
        }
      }
    } catch (err) {
      console.error("Failed to fetch job files:", err);
    }
  };

  // Handle file select
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  // Trigger Upload APK
  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setJobId(null);
    setJob(null);
    setSourceFiles({ android: [], ios: [] });

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`http://${window.location.hostname}:8000/api/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        alert(`Upload failed: ${err.detail || "Unknown error"}`);
        setUploading(false);
        return;
      }

      const data = await res.json();
      setJobId(data.job_id);
    } catch (err) {
      console.error("Upload request failed:", err);
      alert("Failed to reach the backend API server. Check if backend is running on port 8000.");
    } finally {
      setUploading(false);
    }
  };

  // Change active code pair view (Login vs Home)
  const handleCodePairChange = (pair: "login" | "home") => {
    setCodePair(pair);
    if (pair === "login") {
      const andF = sourceFiles.android.find(f => f.name.includes("LoginActivity"));
      const iosF = sourceFiles.ios.find(f => f.name.includes("LoginView"));
      if (andF) setSelectedAndroidFile(andF);
      if (iosF) setSelectedIosFile(iosF);
    } else {
      const andF = sourceFiles.android.find(f => f.name.includes("HomeActivity"));
      const iosF = sourceFiles.ios.find(f => f.name.includes("HomeView"));
      if (andF) setSelectedAndroidFile(andF);
      if (iosF) setSelectedIosFile(iosF);
    }
  };

  // Helper formatting for file size
  const formatBytes = (bytes?: number) => {
    if (!bytes) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  // Sample upload helper
  const handleMockSampleUpload = async () => {
    // Generate dummy file
    const mockApk = new File(["dummyapkcontent"], "fittrack_pro.apk", { type: "application/vnd.android.package-archive" });
    setFile(mockApk);
  };

  // Navigation Nodes & Edges
  const navigationGraph: NavigationGraph = (job as any)?.navigation_graph || {
    nodes: [
      { id: "LoginActivity", label: "Login Screen", type: "Activity", entryPoint: true },
      { id: "HomeActivity", label: "Home Dashboard", type: "Activity", entryPoint: false }
    ],
    edges: [
      { source: "LoginActivity", target: "HomeActivity", action: "Sign In Tap", transition: "Intent Transition" }
    ]
  };

  const unsupportedFeatures: UnsupportedFeature[] = (job as any)?.unsupported_features || [];

  return (
    <div className="min-h-screen text-slate-100 flex bg-slate-950 font-sans">
      {/* Sidebar */}
      <aside className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 glass">
        <div>
          {/* Logo */}
          <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
            <div className="p-2 bg-primary-600 rounded-lg shadow-lg shadow-primary-500/20 text-white animate-pulse-slow">
              <Zap size={22} className="fill-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg tracking-wider bg-gradient-to-r from-violet-400 to-indigo-200 bg-clip-text text-transparent">ANTIGRAVITY</h1>
              <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-widest">APK to iOS Platform</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="p-4 space-y-1">
            <div className="text-[11px] text-slate-500 font-semibold px-3 py-2 uppercase tracking-widest">Workspace</div>
            <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-200 bg-slate-800/80 border border-slate-700/50 shadow-inner font-medium text-sm transition-all duration-200">
              <Settings size={18} className="text-violet-400" />
              <span>Conversion Console</span>
            </button>
            
            <a 
              href="/Users/jeetpitale/.gemini/antigravity/brain/f066a99a-8111-4ffb-9ad5-4a9fa9acfedc/implementation_plan.md"
              target="_blank"
              className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent hover:border-slate-800/50 font-medium text-sm transition-all duration-200"
            >
              <FileCode size={18} />
              <span>Implementation Plan</span>
            </a>
          </nav>

          {/* Downloads */}
          <div className="p-4 border-t border-slate-800/80 mt-4">
            <div className="text-[11px] text-slate-500 font-semibold px-3 py-1 uppercase tracking-widest mb-2">Deliverables</div>
            <a 
              href={`http://localhost:8000/api/download/${job?.zip_filename || 'fitlife_tracker_ios_migration.zip'}`}
              className="w-full flex items-center justify-center space-x-2 bg-emerald-600/95 hover:bg-emerald-500 text-white font-semibold text-xs py-2.5 px-3 rounded-xl shadow-md transition-colors"
            >
              <Download size={14} />
              <span>Download Converted iOS App</span>
            </a>
          </div>
        </div>

        {/* Profile Info */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/40 flex items-center space-x-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center font-bold text-sm shadow">
            JP
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-200">Jeet Pitale</div>
            <div className="text-[10px] text-slate-500 font-semibold">Active Workspaces</div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 bg-slate-900/60 border-b border-slate-800/60 backdrop-blur flex items-center justify-between px-8 z-10">
          <div className="flex items-center space-x-3">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">System Status: Ready</span>
          </div>

          <div className="flex items-center space-x-4">
            {job && (
              <div className="text-sm">
                <span className="text-slate-400">Job: </span>
                <span className="font-mono text-xs font-bold text-violet-400 bg-slate-800 px-2 py-0.5 rounded">{job.job_id.substring(0, 8)}</span>
              </div>
            )}
            <button className="text-slate-400 hover:text-slate-200 transition-colors">
              <HelpCircle size={20} />
            </button>
          </div>
        </header>

        {/* Console view layout */}
        <div className="flex-1 p-8 overflow-y-auto space-y-8">
          {/* Top Row: File Uploader and Step Tracker */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Stage 1: APK Upload */}
            <div className="lg:col-span-1 glass rounded-2xl p-6 shadow-2xl relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 right-0 p-8 opacity-5">
                <Upload size={120} className="text-slate-400" />
              </div>

              <div>
                <div className="flex items-center space-x-2 text-violet-400 font-bold text-sm tracking-wider uppercase mb-3">
                  <span className="h-2 w-2 rounded-full bg-violet-400"></span>
                  <span>Step 1 — File Intake</span>
                </div>
                <h3 className="font-bold text-xl mb-4 text-slate-200">Upload Target APK</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">
                  Select your binary Android APK pack file. The platform will read structure headers, manifest metadata, and initialize decompilation.
                </p>

                {/* Upload drag drop box */}
                <div className="border-2 border-dashed border-slate-700 hover:border-violet-500/80 bg-slate-900/40 transition-all rounded-xl p-6 text-center cursor-pointer mb-4 relative">
                  <input 
                    type="file" 
                    accept=".apk"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <Upload className="mx-auto text-slate-500 mb-2" size={24} />
                  <p className="text-xs font-medium text-slate-300">
                    {file ? file.name : "Choose an APK or drag it here"}
                  </p>
                  <p className="text-[10px] text-slate-500 mt-1">Supports standard APK packages</p>
                </div>

                {file && (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 space-y-2 mb-4">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 font-semibold">File Size:</span>
                      <span className="font-mono text-slate-200">{formatBytes(file.size)}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 font-semibold">Estimated Migration Time:</span>
                      <span className="text-violet-400 font-semibold">~ 3.5 minutes</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <button
                  onClick={handleUpload}
                  disabled={!file || uploading || job?.status === "running"}
                  className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-500 text-white font-semibold text-sm py-3 px-4 rounded-xl shadow-lg transition-all"
                >
                  {uploading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <Play size={16} className="fill-white" />
                      <span>Start Migration Pipeline</span>
                    </>
                  )}
                </button>

                {!file && (
                  <button
                    onClick={mockSampleUploadHelper}
                    className="w-full text-center text-xs text-slate-500 hover:text-slate-400 font-medium transition-colors"
                  >
                    Use Sample Demo APK (FitTrack Pro)
                  </button>
                )}
              </div>
            </div>

            {/* Stepper Pipeline Progress (14 Stages) */}
            <div className="lg:col-span-2 glass rounded-2xl p-6 shadow-2xl flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="font-bold text-lg text-slate-200">Migration Pipeline Stages</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Tracking APK decompile, mapping, translation, testing, and healing</p>
                </div>
                {job && (
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-slate-400">Step:</span>
                    <span className="font-mono text-xs font-bold bg-violet-950 text-violet-400 px-2 py-0.5 rounded border border-violet-800/40">
                      {job.current_step} / {job.total_steps}
                    </span>
                  </div>
                )}
              </div>

              {/* Progress Stepper List */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 flex-1">
                {job ? (
                  job.steps.map((s) => (
                    <div 
                      key={s.index}
                      className={`border rounded-xl p-3 flex flex-col justify-between transition-all duration-300 relative overflow-hidden ${
                        s.status === "running" 
                          ? "bg-slate-900 border-violet-500 shadow-md shadow-violet-500/10" 
                          : s.status === "completed"
                          ? "bg-slate-950/80 border-slate-800"
                          : s.status === "failed"
                          ? "bg-rose-950/20 border-rose-800/80"
                          : "bg-slate-950/40 border-slate-900/60 opacity-60"
                      }`}
                    >
                      {/* Pulse ring for active step */}
                      {s.status === "running" && (
                        <div className="absolute top-0 left-0 w-1.5 h-full bg-violet-500 animate-pulse"></div>
                      )}

                      <div className="flex items-start justify-between">
                        <span className="font-mono text-[10px] text-slate-500 font-bold uppercase">Stage {s.index}</span>
                        {s.status === "completed" && <CheckCircle2 size={14} className="text-emerald-500 fill-emerald-950/40" />}
                        {s.status === "running" && <Loader2 size={14} className="text-violet-400 animate-spin" />}
                        {s.status === "failed" && <XCircle size={14} className="text-rose-500 fill-rose-950/40" />}
                        {s.status === "pending" && <span className="h-1.5 w-1.5 rounded-full bg-slate-700"></span>}
                      </div>

                      <div className="mt-2">
                        <div className={`text-xs font-bold leading-snug ${s.status === "running" ? "text-violet-300" : s.status === "failed" ? "text-rose-300" : "text-slate-300"}`}>{s.name}</div>
                        <p className="text-[9px] text-slate-500 leading-normal mt-1 truncate">{s.description}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  Array.from({ length: 14 }).map((_, i) => (
                    <div key={i} className="bg-slate-950/30 border border-slate-900/50 rounded-xl p-3 flex flex-col justify-between opacity-40">
                      <span className="font-mono text-[10px] text-slate-600 font-bold uppercase">Stage {i+1}</span>
                      <div className="mt-4">
                        <div className="h-3 w-28 bg-slate-800 rounded"></div>
                        <div className="h-2 w-20 bg-slate-900 rounded mt-2"></div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Row 2: Live Log Terminal */}
          <div className="glass rounded-2xl p-6 shadow-2xl flex flex-col h-80 relative overflow-hidden">
            <div className="flex justify-between items-center mb-4 shrink-0">
              <div className="flex items-center space-x-2.5">
                <Terminal size={18} className="text-violet-400" />
                <h3 className="font-bold text-sm tracking-wider uppercase text-slate-200">System Logs Terminal Stream</h3>
              </div>
              {job && (
                <div className="flex items-center space-x-3 text-xs">
                  {job.status === "running" && (
                    <span className="flex items-center space-x-1.5 text-violet-400 font-semibold animate-pulse">
                      <span className="h-1.5 w-1.5 rounded-full bg-violet-400"></span>
                      <span>Streaming via WebSocket</span>
                    </span>
                  )}
                  {job.status === "completed" && <span className="text-emerald-400 font-semibold">Done</span>}
                  {job.status === "failed" && <span className="text-rose-400 font-semibold">Error occurred</span>}
                </div>
              )}
            </div>

            {/* Terminal console */}
            <div className="flex-1 bg-slate-950/95 border border-slate-800 rounded-xl p-4 font-mono text-xs overflow-y-auto space-y-1.5 shadow-inner">
              {job && job.logs.length > 0 ? (
                job.logs.map((l, index) => {
                  let isError = l.message.includes("[ERROR]") || l.message.includes("failed") || l.message.includes("error:");
                  let isSuccess = l.message.includes("[BUILD SUCCESS]") || l.message.includes("successfully") || l.message.includes("passed");
                  let isStepHeader = l.message.startsWith("---");

                  let colorClass = "text-slate-400";
                  if (isError) colorClass = "text-rose-400";
                  else if (isSuccess) colorClass = "text-emerald-400 font-medium";
                  else if (isStepHeader) colorClass = "text-violet-300 font-semibold mt-2";

                  return (
                    <div key={index} className={`leading-relaxed whitespace-pre-wrap ${colorClass}`}>
                      <span className="text-slate-600 select-none mr-2">[{new Date(l.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}]</span>
                      {l.message}
                    </div>
                  );
                })
              ) : (
                <div className="h-full flex items-center justify-center text-slate-600 text-xs">
                  <span>Waiting for pipeline execution logs...</span>
                </div>
              )}
              <div ref={logsEndRef}></div>
            </div>
          </div>

          {/* Row 3: Advanced Pipeline Output Controls (Tabs: Code Diff, Architecture Graph, Report Details, Self-Healing) */}
          {job && (job.current_step >= 3 || job.status === "completed") && (
            <div className="glass rounded-2xl p-6 shadow-2xl flex flex-col min-h-[500px]">
              {/* Tab Navigation header */}
              <div className="flex flex-wrap items-center justify-between border-b border-slate-800 pb-4 mb-6 gap-4">
                <div className="flex items-center space-x-1.5 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
                  <button 
                    onClick={() => setActiveTab("code")}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === "code" ? "bg-primary-600 text-white shadow" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    <Code2 size={14} />
                    <span>Code Conversion</span>
                  </button>
                  <button 
                    onClick={() => setActiveTab("architecture")}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === "architecture" ? "bg-primary-600 text-white shadow" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    <Network size={14} />
                    <span>Architecture Recovered</span>
                  </button>
                  <button 
                    onClick={() => setActiveTab("healing")}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === "healing" ? "bg-primary-600 text-white shadow" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    <Zap size={14} />
                    <span>AI Healing ({job.repair_attempts.length})</span>
                  </button>
                  <button 
                    onClick={() => setActiveTab("reports")}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === "reports" ? "bg-primary-600 text-white shadow" : "text-slate-400 hover:text-slate-200"}`}
                  >
                    <FileCode size={14} />
                    <span>Deliverables & Reports</span>
                  </button>
                </div>

                {/* KPI Metrics */}
                <div className="flex items-center space-x-6">
                  {/* Quality radial dial */}
                  <div className="flex items-center space-x-3">
                    <div className="relative w-11 h-11 flex items-center justify-center rounded-full bg-slate-900 border border-slate-800 shadow">
                      <svg className="w-10 h-10 transform -rotate-90">
                        <circle cx="20" cy="20" r="16" stroke="currentColor" className="text-slate-800" strokeWidth="3" fill="transparent" />
                        <circle cx="20" cy="20" r="16" stroke="currentColor" className="text-violet-500" strokeWidth="3" fill="transparent"
                          strokeDasharray={100}
                          strokeDashoffset={100 - (job.quality_score || 0)}
                        />
                      </svg>
                      <span className="absolute text-[9px] font-bold text-violet-300">{Math.round(job.quality_score)}%</span>
                    </div>
                    <div>
                      <div className="text-[10px] text-slate-500 font-bold uppercase">Similarity Score</div>
                      <div className="text-xs font-bold text-slate-300">{job.quality_score > 0 ? `${job.quality_score.toFixed(1)}% Match` : "Calculating..."}</div>
                    </div>
                  </div>

                  {/* Compiler status */}
                  <div className="text-xs">
                    <div className="text-[10px] text-slate-500 font-bold uppercase">Compiler status</div>
                    <div className="flex items-center space-x-1.5 mt-0.5">
                      {job.build_status === "success" && (
                        <>
                          <CheckCircle2 size={14} className="text-emerald-500" />
                          <span className="font-bold text-emerald-400">Build Succeeded</span>
                        </>
                      )}
                      {job.build_status === "failed" && (
                        <>
                          <XCircle size={14} className="text-rose-500" />
                          <span className="font-bold text-rose-400">Failed</span>
                        </>
                      )}
                      {job.build_status === "pending" && (
                        <>
                          <Loader2 size={12} className="text-slate-500 animate-spin" />
                          <span className="font-semibold text-slate-500">Awaiting Compilation</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Tab: Code Diff Viewer */}
              {activeTab === "code" && (
                <div className="flex-1 flex flex-col space-y-4">
                  {/* Selectors */}
                  <div className="flex justify-between items-center bg-slate-900/40 p-3 border border-slate-850 rounded-xl">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-slate-400 font-semibold">Compare Components:</span>
                      <button 
                        onClick={() => handleCodePairChange("login")}
                        className={`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${codePair === "login" ? "bg-slate-800 text-violet-400 border-slate-700" : "bg-transparent text-slate-500 border-transparent hover:text-slate-300"}`}
                      >
                        Login Screen (Kotlin vs SwiftUI)
                      </button>
                      <button 
                        onClick={() => handleCodePairChange("home")}
                        className={`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${codePair === "home" ? "bg-slate-800 text-violet-400 border-slate-700" : "bg-transparent text-slate-500 border-transparent hover:text-slate-300"}`}
                      >
                        Home Dashboard (Kotlin vs SwiftUI)
                      </button>
                    </div>
                    
                    <div className="text-[10px] text-violet-400 font-bold bg-violet-950/60 border border-violet-850 px-3 py-1 rounded-lg">
                      Android API Transpilation: SharedPreferences ➔ UserDefaults
                    </div>
                  </div>

                  {/* Code columns */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
                    {/* Left: Kotlin */}
                    <div className="bg-slate-950 border border-slate-850 rounded-xl p-4 flex flex-col h-[400px]">
                      <div className="flex justify-between items-center border-b border-slate-900 pb-2 mb-3 shrink-0">
                        <span className="text-xs font-bold text-slate-300 flex items-center space-x-1.5">
                          <span className="h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
                          <span>{selectedAndroidFile ? selectedAndroidFile.name : "Android Source"}</span>
                        </span>
                        <span className="text-[9px] font-mono bg-indigo-950/80 text-indigo-400 border border-indigo-900 px-1.5 py-0.5 rounded">Kotlin</span>
                      </div>
                      <div className="flex-1 overflow-auto font-mono text-[11px] leading-relaxed text-slate-300 bg-slate-950 p-2 whitespace-pre select-all scrollbar-thin">
                        {selectedAndroidFile ? selectedAndroidFile.content : "// Awaiting Android sources extraction..."}
                      </div>
                    </div>

                    {/* Right: SwiftUI */}
                    <div className="bg-slate-950 border border-slate-850 rounded-xl p-4 flex flex-col h-[400px]">
                      <div className="flex justify-between items-center border-b border-slate-900 pb-2 mb-3 shrink-0">
                        <span className="text-xs font-bold text-slate-300 flex items-center space-x-1.5">
                          <span className="h-1.5 w-1.5 rounded-full bg-violet-500 animate-pulse"></span>
                          <span>{selectedIosFile ? selectedIosFile.name : "iOS SwiftUI View"}</span>
                        </span>
                        <span className="text-[9px] font-mono bg-violet-950/80 text-violet-400 border border-violet-900 px-1.5 py-0.5 rounded">SwiftUI</span>
                      </div>
                      <div className="flex-1 overflow-auto font-mono text-[11px] leading-relaxed text-slate-300 bg-slate-950 p-2 whitespace-pre select-all scrollbar-thin">
                        {selectedIosFile ? selectedIosFile.content : "// Awaiting SwiftUI code generation..."}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab: Architecture Flow Graph */}
              {activeTab === "architecture" && (
                <div className="flex-1 flex flex-col space-y-4">
                  <div className="bg-slate-900/40 p-4 border border-slate-850 rounded-xl text-xs leading-relaxed text-slate-400">
                    <span className="font-bold text-slate-200 block mb-1">Recovered Navigation & Event Graph</span>
                    The platform parses Activity Intent references, layouts and click events to construct a flow chart. The platform model is platform-independent.
                  </div>

                  <div className="flex-1 bg-slate-950 border border-slate-850 rounded-xl p-6 flex flex-col md:flex-row items-center justify-center gap-12 min-h-[350px]">
                    {navigationGraph.nodes.map((node, index) => {
                      // We generate lines between nodes
                      const isEntry = node.entryPoint;
                      return (
                        <React.Fragment key={node.id}>
                          <div className={`p-5 rounded-xl border relative w-64 shadow-xl ${isEntry ? "border-violet-500 bg-slate-900" : "border-slate-850 bg-slate-900/40"}`}>
                            {isEntry && (
                              <div className="absolute -top-2.5 left-4 bg-violet-600 text-white font-mono text-[9px] px-2 py-0.5 rounded-full uppercase tracking-wider font-bold">
                                App Entry Launcher
                              </div>
                            )}
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-slate-200">{node.label}</span>
                              <span className="text-[9px] font-mono bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{node.type}</span>
                            </div>
                            <p className="text-[10px] text-slate-500 mt-2 font-mono">{node.id}.kt ➔ {node.id.replace("Activity", "View")}.swift</p>
                          </div>
                          
                          {index < navigationGraph.nodes.length - 1 && (
                            <div className="flex flex-col items-center select-none text-slate-500 font-mono text-[10px]">
                              <ArrowRight className="text-violet-400 animate-pulse-slow" />
                              <span className="mt-1 font-bold text-slate-400">{navigationGraph.edges[index]?.action}</span>
                              <span className="text-[9px] text-slate-600 mt-0.5 text-center px-2">{navigationGraph.edges[index]?.transition}</span>
                            </div>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Tab: Self Healing Attempts */}
              {activeTab === "healing" && (
                <div className="flex-1 flex flex-col space-y-6">
                  <div className="bg-slate-900/40 p-4 border border-slate-850 rounded-xl text-xs leading-relaxed text-slate-400">
                    <span className="font-bold text-slate-200 block mb-1">AI Self-Healing Repair Log</span>
                    The platform compiles the generated project, analyzes compiler errors, and loops automatically to fix the Swift source code files. Below is the patch log.
                  </div>

                  <div className="border border-slate-850 rounded-xl overflow-hidden">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-slate-900 text-slate-400 border-b border-slate-850 font-bold uppercase tracking-wider">
                          <th className="p-4">Attempt</th>
                          <th className="p-4">Patch Type</th>
                          <th className="p-4">Description</th>
                          <th className="p-4">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-850 font-medium">
                        {job.repair_attempts.length > 0 ? (
                          job.repair_attempts.map((a, i) => (
                            <tr key={i} className="hover:bg-slate-900/20">
                              <td className="p-4 font-mono text-violet-400 font-bold"># {a.attempt}</td>
                              <td className="p-4">
                                <span className="px-2 py-0.5 rounded font-mono text-[10px] bg-slate-800 text-slate-300 border border-slate-700">
                                  {a.type}
                                </span>
                              </td>
                              <td className="p-4 text-slate-300 leading-relaxed max-w-md">{a.description}</td>
                              <td className="p-4">
                                <span className="flex items-center space-x-1 text-emerald-400 font-bold">
                                  <CheckCircle2 size={14} className="fill-emerald-950/40" />
                                  <span>{a.status.toUpperCase()}</span>
                                </span>
                              </td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan={4} className="p-8 text-center text-slate-500 font-semibold">
                              No code repairs were required. Compiler build succeeded on first validation pass.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab: Deliverables & Reports */}
              {activeTab === "reports" && (
                <div className="flex-1 flex flex-col space-y-6">
                  {/* Grid for Reports and ZIP download */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Zip Deliverable Card */}
                    <div className="md:col-span-1 border border-slate-850 bg-slate-900/20 rounded-xl p-5 flex flex-col justify-between shadow-lg">
                      <div>
                        <div className="p-3 bg-violet-950 border border-violet-850 rounded-xl w-fit text-violet-400 mb-4">
                          <FileCode size={24} />
                        </div>
                        <h4 className="font-bold text-base text-slate-200">Xcode Project Bundle</h4>
                        <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                          A fully functional and compiling Xcode Swift Package Manager project containing SwiftUI views, state navigation, model persistence, and tests.
                        </p>
                      </div>
                      
                      <div className="mt-6">
                        {job.zip_filename ? (
                          <a 
                            href={`http://${window.location.hostname}:8000/api/download/${job.zip_filename}`}
                            className="w-full flex items-center justify-center space-x-2 bg-violet-600 hover:bg-violet-500 text-white font-bold text-xs py-3 px-4 rounded-xl shadow transition-colors"
                          >
                            <Download size={14} />
                            <span>Download ZIP Package</span>
                          </a>
                        ) : (
                          <button 
                            disabled 
                            className="w-full flex items-center justify-center space-x-2 bg-slate-800 text-slate-500 font-bold text-xs py-3 px-4 rounded-xl"
                          >
                            <Loader2 size={14} className="animate-spin" />
                            <span>Creating ZIP Package...</span>
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Report Documents */}
                    <div className="md:col-span-2 border border-slate-850 rounded-xl p-5 flex flex-col justify-between">
                      <div>
                        <h4 className="font-bold text-base text-slate-200 mb-4">Incompatibility & Feature Mappings</h4>
                        
                        {/* List of incompatibilities */}
                        <div className="space-y-4">
                          {unsupportedFeatures.length > 0 ? (
                            unsupportedFeatures.map((item, idx) => (
                              <div key={idx} className="border border-slate-850/60 bg-slate-950/40 rounded-lg p-3 space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="font-bold text-xs text-slate-300 flex items-center space-x-1.5">
                                    <AlertTriangle size={14} className="text-amber-500" />
                                    <span>{item.feature}</span>
                                  </span>
                                  <span className={`font-mono text-[9px] px-1.5 py-0.5 rounded font-bold ${
                                    item.severity === "HIGH" ? "bg-rose-950 text-rose-400 border border-rose-900" : "bg-amber-950 text-amber-400 border border-amber-900"
                                  }`}>
                                    {item.severity} SEVERITY
                                  </span>
                                </div>
                                <p className="text-[10px] text-slate-500 font-mono bg-slate-900 p-1.5 rounded">{item.details}</p>
                                <p className="text-[11px] text-slate-400 leading-normal"><span className="font-bold text-slate-300">iOS Alternative:</span> {item.ios_alternative}</p>
                              </div>
                            ))
                          ) : (
                            <div className="text-center p-6 text-slate-500 text-xs">
                              Scanning Android code compatibility...
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );

  // Quick helper to avoid passing parameter mismatch in onClick
  function mockUploadHelper() {
    handleUpload();
  }

  function mockSampleUploadHelper() {
    handleMockSampleUpload();
  }
}
