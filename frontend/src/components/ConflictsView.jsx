import React from 'react';
import { Split, AlertTriangle, ArrowRightLeft, Info, ExternalLink } from 'lucide-react';

export default function ConflictsView({ conflicts }) {
  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'direct_contradiction':
        return 'bg-rose-950/70 text-rose-300 border-rose-800/80';
      case 'moderate_divergence':
        return 'bg-amber-950/70 text-amber-300 border-amber-800/80';
      case 'minor_nuance':
        return 'bg-blue-950/70 text-blue-300 border-blue-800/80';
      default:
        return 'bg-slate-900 text-slate-300 border-slate-800';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-md">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Split className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-slate-200">
            Cross-Source Conflicts & Divergence Analysis ({conflicts.length})
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          Disagreement Preservation Active
        </span>
      </div>

      {conflicts.length === 0 ? (
        <div className="text-center py-8 text-slate-400 text-xs bg-slate-900/30 rounded-xl border border-slate-800/60 p-6">
          <div className="w-8 h-8 rounded-full bg-emerald-950/60 border border-emerald-800 flex items-center justify-center mx-auto mb-2 text-emerald-400">
            ✓
          </div>
          <p className="font-medium text-slate-300">High Cross-Source Consensus</p>
          <p className="text-[11px] text-slate-500 mt-1 max-w-md mx-auto">
            Retrieved primary sources are in broad empirical agreement on all measured dimensions. No unreconciled contradictory claims were detected.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {conflicts.map((conf) => (
            <div
              key={conf.id}
              className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all"
            >
              {/* Conflict Header */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/60 text-amber-300 border border-amber-800/60 font-semibold">
                    {conf.id}
                  </span>
                  <h4 className="text-xs font-bold text-white uppercase tracking-wide">
                    Topic: {conf.topic}
                  </h4>
                </div>
                <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded border ${getSeverityBadge(conf.severity)}`}>
                  {conf.severity?.replace('_', ' ')}
                </span>
              </div>

              {/* Competing Claims Side-by-Side Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 my-3">
                
                {/* Perspective A */}
                <div className="bg-slate-950/80 border border-sky-900/40 rounded-xl p-3.5 flex flex-col justify-between">
                  <div>
                    <div className="text-[10px] font-semibold text-sky-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                      <span>Perspective A</span>
                    </div>
                    <p className="text-xs text-slate-200 leading-snug">
                      "{conf.claim_a}"
                    </p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-slate-900 flex items-center justify-between text-[10px] text-slate-400">
                    <span className="truncate max-w-[75%] text-slate-300">{conf.source_a_title}</span>
                    <a
                      href={conf.source_a_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sky-400 hover:text-sky-300 flex items-center gap-0.5"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>

                {/* Perspective B */}
                <div className="bg-slate-950/80 border border-cyan-900/40 rounded-xl p-3.5 flex flex-col justify-between">
                  <div>
                    <div className="text-[10px] font-semibold text-cyan-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                      <span>Perspective B</span>
                    </div>
                    <p className="text-xs text-slate-200 leading-snug">
                      "{conf.claim_b}"
                    </p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-slate-900 flex items-center justify-between text-[10px] text-slate-400">
                    <span className="truncate max-w-[75%] text-slate-300">{conf.source_b_title}</span>
                    <a
                      href={conf.source_b_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-0.5"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </div>

              </div>

              {/* Explanatory root cause */}
              <div className="bg-amber-950/20 border border-amber-900/40 rounded-xl p-3 mt-3 flex items-start space-x-2.5">
                <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="text-xs text-slate-300 leading-relaxed">
                  <span className="font-semibold text-amber-300">Analytical Root Cause: </span>
                  {conf.possible_reason}
                </div>
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
}
