import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ResearchInput from './components/ResearchInput';
import ProgressTracker from './components/ProgressTracker';
import TimelineFeed from './components/TimelineFeed';
import ResearchPlanView from './components/ResearchPlanView';
import SourcesPanel from './components/SourcesPanel';
import EvidenceMatrix from './components/EvidenceMatrix';
import ConflictsView from './components/ConflictsView';
import VerificationAudit from './components/VerificationAudit';
import ReportViewer from './components/ReportViewer';
import { API_BASE } from './api';

import {
  FileText,
  Compass,
  Globe,
  Database,
  Split,
  ShieldCheck,
  Terminal,
  Layers,
  Sparkles,
  AlertCircle
} from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessionState, setSessionState] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [activeTab, setActiveTab] = useState('report');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const eventSourceRef = useRef(null);

  // Load health and sessions on mount
  useEffect(() => {
    fetchHealth();
    fetchSessions();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      }
    } catch (e) {
      console.error('Health check failed:', e);
    }
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/research/sessions`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        if (data.length > 0 && !currentSessionId) {
          loadSession(data[0].session_id);
        }
      }
    } catch (e) {
      console.error('Failed to load sessions:', e);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      setCurrentSessionId(sessionId);
      const res = await fetch(`${API_BASE}/api/research/sessions/${sessionId}`);
      if (res.ok) {
        const data = await res.json();
        setSessionState(data);
        setIsRunning(data.status !== 'completed' && data.status !== 'failed');
        if (data.report) {
          setActiveTab('report');
        } else if (data.plan) {
          setActiveTab('plan');
        }
      }
    } catch (e) {
      console.error('Failed to fetch session detail:', e);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await fetch(`${API_BASE}/api/research/sessions/${sessionId}`, { method: 'DELETE' });
      const updated = sessions.filter((s) => s.session_id !== sessionId);
      setSessions(updated);
      if (currentSessionId === sessionId) {
        if (updated.length > 0) {
          loadSession(updated[0].session_id);
        } else {
          setCurrentSessionId(null);
          setSessionState(null);
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handleStartResearch = async (question, deepMode) => {
    try {
      setIsRunning(true);
      setActiveTab('timeline'); // View live execution immediately
      
      const res = await fetch(`${API_BASE}/api/research/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, deep_mode: deepMode })
      });

      if (!res.ok) {
        throw new Error('Failed to initiate research session');
      }

      const { session_id } = await res.json();
      setCurrentSessionId(session_id);
      
      // Initialize local state
      setSessionState({
        session_id,
        question,
        status: 'planning',
        progress_percentage: 5,
        timeline: [],
        sources: [],
        evidence: [],
        conflicts: [],
        plan: null,
        verification: null,
        report: null,
      });

      // Connect to SSE stream
      connectStream(session_id);
      fetchSessions();
    } catch (e) {
      console.error('Start research error:', e);
      setIsRunning(false);
    }
  };

  const connectStream = (sessionId) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const es = new EventSource(`${API_BASE}/api/research/stream/${sessionId}`);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        setSessionState((prev) => {
          if (!prev) return prev;
          const updatedTimeline = data.event
            ? [...(prev.timeline || []), data.event]
            : (data.timeline || prev.timeline || []);

          return {
            ...prev,
            status: data.status || prev.status,
            progress_percentage: data.progress !== undefined ? data.progress : prev.progress_percentage,
            plan: data.plan || prev.plan,
            sources: data.sources || prev.sources || [],
            evidence: data.evidence || prev.evidence || [],
            conflicts: data.conflicts || prev.conflicts || [],
            verification: data.verification || prev.verification,
            report: data.report || prev.report,
            timeline: updatedTimeline,
            error: data.error || prev.error
          };
        });

        if (data.status === 'completed') {
          setIsRunning(false);
          setActiveTab('report');
          fetchSessions();
          es.close();
        } else if (data.status === 'failed') {
          setIsRunning(false);
          fetchSessions();
          es.close();
        }
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    es.onerror = (err) => {
      console.warn('SSE stream closed or error encountered:', err);
      es.close();
    };
  };

  const handleNewResearch = () => {
    setSessionState(null);
    setCurrentSessionId(null);
    setIsRunning(false);
    setActiveTab('report');
  };

  const TABS = [
    { key: 'report', label: 'Final Report', icon: FileText, count: sessionState?.report ? '1' : null },
    { key: 'plan', label: 'Research Plan', icon: Compass, count: sessionState?.plan ? `${sessionState.plan.sub_questions?.length}` : null },
    { key: 'sources', label: 'Sources', icon: Globe, count: sessionState?.sources?.length || null },
    { key: 'evidence', label: 'Evidence Matrix', icon: Database, count: sessionState?.evidence?.length || null },
    { key: 'conflicts', label: 'Conflicts & Nuance', icon: Split, count: sessionState?.conflicts?.length || null },
    { key: 'verification', label: 'Verification Audit', icon: ShieldCheck, count: sessionState?.verification ? 'Audited' : null },
    { key: 'timeline', label: 'Agent Timeline', icon: Terminal, count: sessionState?.timeline?.length || null },
  ];

  return (
    <div className="min-h-screen flex flex-col font-sans relative selection:bg-sky-500/30 selection:text-sky-200">
      
      {/* Subtle Sky Blue Ambient Glows */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[900px] h-[360px] bg-sky-500/10 rounded-full blur-[120px] pointer-events-none -z-10"></div>
      <div className="fixed bottom-0 right-0 w-[500px] h-[300px] bg-sky-600/5 rounded-full blur-[100px] pointer-events-none -z-10"></div>

      {/* Top Navbar */}
      <Navbar health={health} onNewResearch={handleNewResearch} />

      {/* Main Container */}
      <div className="flex-1 flex overflow-hidden max-w-7xl w-full mx-auto">
        
        {/* Left Drawer / Sidebar */}
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={loadSession}
          onDeleteSession={handleDeleteSession}
          onSelectPrompt={(q) => handleStartResearch(q, false)}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />

        {/* Primary Content Workspace */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-6">
          
          {/* Research Input Bar */}
          <ResearchInput
            onSubmit={handleStartResearch}
            isRunning={isRunning}
          />

          {/* Progress Tracker (visible when session is active or loaded) */}
          {sessionState && (
            <ProgressTracker
              currentStage={sessionState.status}
              progressPercentage={sessionState.progress_percentage || 0}
              error={sessionState.error}
            />
          )}

          {/* Research Workspace Views */}
          {sessionState ? (
            <div className="space-y-4">
              
              {/* Navigation Tabs Bar */}
              <div className="flex items-center space-x-1 overflow-x-auto border-b border-slate-800 pb-2 scrollbar-none">
                {TABS.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.key;

                  return (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key)}
                      className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                        isActive
                          ? 'bg-sky-600 text-white shadow-md shadow-sky-600/25 border border-sky-400/30'
                          : 'bg-slate-900/60 hover:bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800/80'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{tab.label}</span>
                      {tab.count !== null && (
                        <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                          isActive ? 'bg-sky-800 text-white' : 'bg-slate-800 text-slate-300'
                        }`}>
                          {tab.count}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Active Tab Panels */}
              <div className="pt-2">
                {activeTab === 'report' && (
                  sessionState.report ? (
                    <ReportViewer report={sessionState.report} />
                  ) : (
                    <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
                      <Sparkles className="w-8 h-8 text-sky-400 mx-auto mb-3 animate-spin-slow" />
                      <h4 className="text-sm font-bold text-white">Synthesizing Final Report...</h4>
                      <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                        The agent is currently extracting empirical evidence, cross-referencing conflicts, and verifying claims before generating the publication-grade report.
                      </p>
                    </div>
                  )
                )}

                {activeTab === 'plan' && (
                  <ResearchPlanView plan={sessionState.plan} />
                )}

                {activeTab === 'sources' && (
                  <SourcesPanel sources={sessionState.sources || []} />
                )}

                {activeTab === 'evidence' && (
                  <EvidenceMatrix evidence={sessionState.evidence || []} />
                )}

                {activeTab === 'conflicts' && (
                  <ConflictsView conflicts={sessionState.conflicts || []} />
                )}

                {activeTab === 'verification' && (
                  <VerificationAudit
                    verification={sessionState.verification}
                    sessionId={sessionState.session_id}
                  />
                )}

                {activeTab === 'timeline' && (
                  <TimelineFeed timeline={sessionState.timeline || []} />
                )}
              </div>

            </div>
          ) : (
            /* Welcome / Onboarding Card */
            <div className="glass-panel rounded-2xl p-10 text-center border border-slate-800 shadow-xl">
              <div className="w-12 h-12 rounded-2xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center mx-auto mb-4">
                <Layers className="w-6 h-6 text-sky-400" />
              </div>
              <h3 className="text-lg font-bold text-white tracking-tight">
                Autonomous Evidence & Synthesis Intelligence
              </h3>
              <p className="text-xs text-slate-400 mt-2 max-w-xl mx-auto leading-relaxed">
                Submit any complex research question or pick a benchmark inquiry from the sidebar.
                The system will automatically generate a multi-faceted research plan, execute web retrieval tools, extract atomic evidence quotes, arbitrate conflicting findings, perform pre-synthesis verification, and produce a structured publication report with citations.
              </p>
            </div>
          )}

        </main>
      </div>

    </div>
  );
}
