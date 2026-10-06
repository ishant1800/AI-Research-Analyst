import React from 'react';
import { History, PlusCircle, Trash2, CheckCircle2, Clock, AlertCircle, Sparkles, Database } from 'lucide-react';

export default function Sidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
  onSelectPrompt,
  isOpen,
  onToggle
}) {
  const PRESET_BENCHMARKS = [
    {
      title: "Solid-State Batteries vs Li-Ion",
      question: "Will solid-state batteries replace lithium-ion in commercial EVs before 2030, and what are the main technical hurdles?"
    },
    {
      title: "Agentic State Machines vs Swarms",
      question: "Are deterministic state-machine agent architectures more reliable in enterprise production than open-ended multi-agent swarms?"
    },
    {
      title: "Small Language Models (SLMs) vs Frontier",
      question: "How do small language models (SLMs, 7B-14B) compare against frontier LLMs for specialized extraction and verification tasks?"
    }
  ];

  return (
    <aside className={`w-80 flex-shrink-0 flex flex-col border-r border-slate-800 bg-slate-950/95 transition-all duration-300 ${isOpen ? 'block' : 'hidden lg:flex'}`}>
      
      {/* Sidebar Header */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center space-x-2 text-slate-200">
          <History className="w-4 h-4 text-sky-400" />
          <h2 className="text-sm font-semibold tracking-wide">Research Archive</h2>
        </div>
        <span className="px-2 py-0.5 text-[11px] font-mono rounded bg-slate-900 border border-slate-800 text-slate-400">
          {sessions.length} sessions
        </span>
      </div>

      {/* Preset Prompts Section */}
      <div className="p-3 border-b border-slate-800/60 bg-slate-900/40">
        <div className="flex items-center space-x-1.5 mb-2 px-1 text-slate-400 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Benchmark Case Studies</span>
        </div>
        <div className="space-y-1.5">
          {PRESET_BENCHMARKS.map((item, idx) => (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.question)}
              className="w-full text-left p-2 rounded-lg text-xs bg-slate-900/80 hover:bg-slate-850 hover:text-sky-300 hover:border-sky-800/60 border border-slate-800/80 transition-all text-slate-300 group"
            >
              <div className="font-medium group-hover:text-sky-300 truncate">{item.title}</div>
              <div className="text-[10px] text-slate-500 line-clamp-1 mt-0.5">{item.question}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Saved Sessions List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 px-1 py-1">
          Recent Inquiries
        </div>

        {sessions.length === 0 ? (
          <div className="text-center py-8 px-4 text-slate-500 text-xs">
            <Database className="w-8 h-8 mx-auto mb-2 opacity-30 text-slate-400" />
            No research sessions in SQLite archive yet. Start an inquiry to populate.
          </div>
        ) : (
          sessions.map((session) => {
            const isSelected = session.session_id === currentSessionId;
            const isCompleted = session.status === 'completed';
            const isFailed = session.status === 'failed';

            return (
              <div
                key={session.session_id}
                onClick={() => onSelectSession(session.session_id)}
                className={`group relative flex flex-col p-3 rounded-xl border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-sky-950/40 border-sky-500/50 text-white shadow-sm shadow-sky-900/20 ring-1 ring-sky-500/30'
                    : 'bg-slate-900/50 hover:bg-slate-900 border-slate-800/80 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="text-xs font-medium line-clamp-2 leading-snug">
                    {session.question}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(session.session_id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition-opacity p-1 -mt-1 -mr-1"
                    title="Delete session"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-slate-800/60 text-[10px] text-slate-400">
                  <div className="flex items-center space-x-1">
                    {isCompleted ? (
                      <span className="flex items-center text-emerald-400 gap-1 font-medium">
                        <CheckCircle2 className="w-3 h-3" />
                        Report Ready
                      </span>
                    ) : isFailed ? (
                      <span className="flex items-center text-rose-400 gap-1 font-medium">
                        <AlertCircle className="w-3 h-3" />
                        Failed
                      </span>
                    ) : (
                      <span className="flex items-center text-amber-400 gap-1 font-medium">
                        <Clock className="w-3 h-3 animate-spin" />
                        {session.progress_percentage}% Active
                      </span>
                    )}
                  </div>
                  <span className="font-mono text-[9px] text-slate-500">
                    {session.created_at ? new Date(session.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

    </aside>
  );
}
