import React from 'react';
import { Compass, HelpCircle, Key, Search, Target } from 'lucide-react';

export default function ResearchPlanView({ plan }) {
  if (!plan) return null;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-md space-y-6">
      
      {/* Scope & Objective */}
      <div className="flex items-start justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center space-x-2 text-sky-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <Compass className="w-4 h-4" />
            <span>Autonomous Research Plan</span>
          </div>
          <h3 className="text-base font-bold text-white">
            {plan.main_question}
          </h3>
          <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
            <span className="font-semibold text-slate-300">Clarified Scope:</span> {plan.clarified_scope}
          </p>
        </div>
      </div>

      {/* Information Required */}
      {plan.information_required && plan.information_required.length > 0 && (
        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800/80">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2.5">
            <Key className="w-3.5 h-3.5 text-amber-400" />
            <span>Required Empirical Evidence</span>
          </div>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-300">
            {plan.information_required.map((item, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Decomposed Sub-Questions Grid */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
          <Target className="w-3.5 h-3.5 text-sky-400" />
          Decomposed Sub-Questions ({plan.sub_questions?.length || 0})
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {plan.sub_questions?.map((subQ) => (
            <div
              key={subQ.id}
              className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950/60 text-sky-300 border border-sky-800/60 font-semibold">
                    {subQ.id}
                  </span>
                </div>
                <h5 className="text-xs font-semibold text-white mb-1.5 leading-snug">
                  {subQ.question}
                </h5>
                <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                  <span className="text-slate-500 font-medium">Objective:</span> {subQ.purpose}
                </p>
              </div>

              {/* Planned Queries */}
              <div className="pt-2 border-t border-slate-800/80">
                <span className="text-[10px] text-slate-500 font-medium block mb-1">
                  Generated Retrieval Queries:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {subQ.suggested_queries?.map((query, qIdx) => (
                    <span
                      key={qIdx}
                      className="text-[10px] font-mono bg-slate-950 px-2 py-0.5 rounded text-cyan-300 border border-slate-800 flex items-center gap-1"
                    >
                      <Search className="w-2.5 h-2.5 text-cyan-500" />
                      {query}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strategy Summary */}
      <div className="text-[11px] text-slate-400 bg-slate-950/60 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
        <div>
          <span className="font-semibold text-slate-300">Search Strategy:</span> {plan.search_strategy}
        </div>
        <span className="font-mono text-[10px] text-sky-400 whitespace-nowrap ml-2">
          Max Iterations: {plan.estimated_iterations || 3}
        </span>
      </div>

    </div>
  );
}
