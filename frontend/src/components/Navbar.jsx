import React from 'react';
import { Layers, Activity, Sparkles, BookOpen, ExternalLink, ShieldCheck } from 'lucide-react';
import { API_BASE } from '../api';

export default function Navbar({ health, onNewResearch }) {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Logo */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 via-sky-400 to-cyan-300 p-[1px] shadow-lg shadow-sky-500/25">
            <div className="w-full h-full bg-slate-950 rounded-xl flex items-center justify-center">
              <Layers className="w-5 h-5 text-sky-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-1.5">
                AI Research Analyst
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                  Agentic MVP
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Autonomous Decomposition, Evidence Mining, Conflict Arbitration & Verification
            </p>
          </div>
        </div>

        {/* System Telemetry & Actions */}
        <div className="flex items-center space-x-3">
          {/* Health status pill */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-300">Model:</span>
            <span className="font-mono text-sky-300 font-medium">
              {health?.model || 'gpt-4o-mini'}
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-300">Search:</span>
            <span className="font-mono text-cyan-300 capitalize">
              {health?.search_provider || 'duckduckgo'}
            </span>
          </div>

          {/* API Docs Link */}
          <a
            href={API_BASE ? `${API_BASE}/docs` : "http://127.0.0.1:8008/docs"}
            target="_blank"
            rel="noreferrer"
            className="hidden lg:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-900 hover:bg-slate-850 border border-slate-800 transition-colors"
          >
            <BookOpen className="w-3.5 h-3.5 text-slate-400" />
            <span>FastAPI Docs</span>
            <ExternalLink className="w-3 h-3 text-slate-500" />
          </a>

          {/* New Session Button */}
          <button
            onClick={onNewResearch}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-950 bg-sky-400 hover:bg-sky-300 shadow-md shadow-sky-500/20 transition-all transform active:scale-95 border border-sky-300/40"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>New Research</span>
          </button>
        </div>

      </div>
    </header>
  );
}
