import React, { useState } from 'react';
import { Activity, ChevronDown, ChevronRight, Terminal, Cpu } from 'lucide-react';

export default function TimelineFeed({ timeline }) {
  const [expandedEvents, setExpandedEvents] = useState({});

  const toggleExpand = (id) => {
    setExpandedEvents((prev) => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const getStageBadgeColor = (stage) => {
    switch (stage) {
      case 'planning': return 'bg-cyan-950/50 text-cyan-400 border-cyan-800/60';
      case 'retrieving': return 'bg-blue-950/50 text-blue-400 border-blue-800/60';
      case 'extracting_evidence': return 'bg-sky-950/50 text-sky-400 border-sky-800/60';
      case 'analyzing_conflicts': return 'bg-amber-950/50 text-amber-400 border-amber-800/60';
      case 'verifying': return 'bg-emerald-950/50 text-emerald-400 border-emerald-800/60';
      case 'synthesizing': return 'bg-sky-900/40 text-sky-300 border-sky-700/60';
      case 'completed': return 'bg-emerald-900/60 text-emerald-300 border-emerald-700';
      case 'failed': return 'bg-rose-950/50 text-rose-400 border-rose-800/60';
      default: return 'bg-slate-900 text-slate-400 border-slate-800';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-md">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-sky-400" />
          <h3 className="text-sm font-semibold text-slate-200">
            Agent Activity Timeline
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          {timeline.length} events logged
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
        {timeline.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-xs">
            Awaiting agent execution events...
          </div>
        ) : (
          timeline.map((event, index) => {
            const hasData = event.data && Object.keys(event.data).length > 0;
            const isExpanded = expandedEvents[event.id];

            return (
              <div
                key={event.id || index}
                className="relative pl-6 pb-2 border-l border-slate-800 last:border-l-0"
              >
                {/* Timeline node dot */}
                <div className="absolute -left-1.5 top-1.5 w-3 h-3 rounded-full bg-slate-950 border-2 border-sky-400"></div>

                <div className="bg-slate-900/60 hover:bg-slate-900/90 border border-slate-800/70 rounded-xl p-3 transition-colors">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${getStageBadgeColor(event.stage)}`}>
                      {event.stage?.replace('_', ' ')}
                    </span>
                    <span className="font-mono text-[10px] text-slate-500">
                      {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''}
                    </span>
                  </div>

                  <p className="text-xs text-slate-200 leading-relaxed font-sans mt-1">
                    {event.message}
                  </p>

                  {/* Expandable JSON details if available */}
                  {hasData && (
                    <div className="mt-2 pt-2 border-t border-slate-800/50">
                      <button
                        onClick={() => toggleExpand(event.id)}
                        className="flex items-center space-x-1 text-[10px] text-slate-400 hover:text-slate-200 font-mono transition-colors"
                      >
                        {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                        <span>Inspection Payload</span>
                      </button>

                      {isExpanded && (
                        <pre className="mt-1.5 p-2 rounded-lg bg-slate-950 border border-slate-800 text-[10px] text-sky-300 font-mono overflow-x-auto">
                          {JSON.stringify(event.data, null, 2)}
                        </pre>
                      )}
                    </div>
                  )}

                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
