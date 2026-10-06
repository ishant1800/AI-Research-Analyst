import React, { useState } from 'react';
import { Search, Sparkles, Sliders, ArrowRight, ShieldCheck, Zap } from 'lucide-react';

export default function ResearchInput({ onSubmit, isRunning }) {
  const [question, setQuestion] = useState('');
  const [deepMode, setDeepMode] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || isRunning) return;
    onSubmit(question.trim(), deepMode);
  };

  const QUICK_SUGGESTIONS = [
    "What is the commercial timeline for solid-state batteries in EVs?",
    "SLMs vs Frontier LLMs in extraction benchmarks",
    "Deterministic state machines vs multi-agent swarms in production"
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl relative overflow-hidden">
      {/* Decorative sky blue gradient blur */}
      <div className="absolute top-0 right-0 -mt-8 -mr-8 w-48 h-48 bg-sky-500/15 rounded-full blur-3xl pointer-events-none"></div>

      <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-slate-300">
              <Search className="w-4 h-4 text-sky-400" />
              Autonomous Research Query
            </span>
            <span className="text-[11px] font-normal text-slate-500">
              Decomposes into sub-questions, executes web tools, audits conflicts
            </span>
          </label>
          <div className="relative">
            <textarea
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter a complex research question (e.g., 'Will solid-state batteries replace lithium-ion in commercial EVs before 2030, and what are the main technical hurdles?')..."
              className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500 transition-all resize-none font-sans"
              disabled={isRunning}
            />
          </div>
        </div>

        {/* Suggestion pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] text-slate-500 font-medium">Quick Examples:</span>
          {QUICK_SUGGESTIONS.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setQuestion(s)}
              disabled={isRunning}
              className="text-[11px] px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-sky-300 hover:border-sky-800/60 border border-slate-800 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Controls Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between pt-3 border-t border-slate-800/80 gap-3">
          
          {/* Deep Mode Option */}
          <div className="flex items-center space-x-3 w-full sm:w-auto">
            <label className="flex items-center space-x-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={deepMode}
                onChange={(e) => setDeepMode(e.target.checked)}
                disabled={isRunning}
                className="w-4 h-4 text-sky-500 rounded bg-slate-900 border-slate-700 focus:ring-sky-400"
              />
              <span className="text-xs font-medium text-slate-300 flex items-center gap-1">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                Deep Investigation Mode
              </span>
            </label>
            <span className="text-[11px] text-slate-500 hidden md:inline">
              (Executes 5 tool cycles & full page extractions)
            </span>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!question.trim() || isRunning}
            className={`w-full sm:w-auto flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-semibold transition-all transform shadow-lg ${
              !question.trim() || isRunning
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
                : 'bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold hover:shadow-sky-500/25 active:scale-98 border border-sky-300/40'
            }`}
          >
            {isRunning ? (
              <>
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                <span>Agent Reasoning Active...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Initiate Autonomous Research</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </>
            )}
          </button>

        </div>
      </form>
    </div>
  );
}
