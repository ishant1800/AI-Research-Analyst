import React from 'react';
import { FileText, ShieldAlert, CheckCircle, ExternalLink, Quote, Sparkles } from 'lucide-react';

export default function EvidenceMatrix({ evidence }) {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-md">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <FileText className="w-4 h-4 text-sky-400" />
          <h3 className="text-sm font-semibold text-slate-200">
            Extracted Evidence Matrix & Provenance ({evidence.length})
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          Anti-Hallucination Quotes Required
        </span>
      </div>

      {evidence.length === 0 ? (
        <div className="text-center py-8 text-slate-500 text-xs">
          No evidence extracted yet. Extractor will parse retrieved sources.
        </div>
      ) : (
        <div className="space-y-4">
          {evidence.map((item) => {
            const confidencePercent = Math.round((item.confidence_score || 0.9) * 100);

            return (
              <div
                key={item.id}
                className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 transition-all hover:border-slate-700"
              >
                {/* Header row */}
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950/60 text-sky-300 border border-sky-800/60 font-semibold">
                      {item.id}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                      Sub-Q: {item.sub_question_id}
                    </span>
                    {item.contradiction_potential && (
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-950/70 text-amber-300 border border-amber-800/60 flex items-center gap-1">
                        <ShieldAlert className="w-3 h-3 text-amber-400" />
                        Divergence Flag
                      </span>
                    )}
                  </div>

                  {/* Confidence gauge badge */}
                  <div className="flex items-center space-x-1.5">
                    <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-sky-400 h-full rounded-full"
                        style={{ width: `${confidencePercent}%` }}
                      ></div>
                    </div>
                    <span className="text-[10px] font-mono font-bold text-sky-300">
                      {confidencePercent}%
                    </span>
                  </div>
                </div>

                {/* Claim Statement */}
                <h4 className="text-xs font-semibold text-white mb-2 leading-snug">
                  {item.claim}
                </h4>

                {/* Verbatim quote block */}
                <div className="bg-slate-950/80 border-l-2 border-sky-400 rounded-r-lg p-3 my-2 text-xs text-slate-300 italic font-sans flex items-start space-x-2">
                  <Quote className="w-3.5 h-3.5 text-sky-400 flex-shrink-0 mt-0.5" />
                  <span className="leading-relaxed">"{item.verbatim_quote}"</span>
                </div>

                {/* Source attribution footer */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/60 mt-2">
                  <div className="flex items-center space-x-1.5 truncate max-w-[80%]">
                    <span className="text-slate-500">Source:</span>
                    <span className="text-slate-300 font-medium truncate">{item.source_title}</span>
                  </div>
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sky-400 hover:text-sky-300 flex items-center gap-1 text-[10px] flex-shrink-0"
                  >
                    <span>View URL</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </div>

              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
