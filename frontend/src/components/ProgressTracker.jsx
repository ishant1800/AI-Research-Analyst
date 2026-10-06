import React from 'react';
import { CheckCircle2, Circle, Loader2, AlertCircle, Compass, Search, FileText, Split, ShieldCheck, FileCheck } from 'lucide-react';

const STAGES = [
  { key: 'planning', label: 'Planning & Decomposition', icon: Compass },
  { key: 'retrieving', label: 'Search & Tool Calling', icon: Search },
  { key: 'extracting_evidence', label: 'Evidence Mining', icon: FileText },
  { key: 'analyzing_conflicts', label: 'Conflict Arbitration', icon: Split },
  { key: 'verifying', label: 'Verification Audit', icon: ShieldCheck },
  { key: 'synthesizing', label: 'Report Synthesis', icon: FileCheck },
];

export default function ProgressTracker({ currentStage, progressPercentage, error }) {
  const getStageStatus = (stageKey) => {
    const stageOrder = ['planning', 'retrieving', 'extracting_evidence', 'analyzing_conflicts', 'verifying', 'synthesizing', 'completed'];
    const currentIndex = stageOrder.indexOf(currentStage);
    const stageIndex = stageOrder.indexOf(stageKey);

    if (error) return 'error';
    if (currentStage === 'completed') return 'completed';
    if (stageIndex < currentIndex) return 'completed';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-md">
      
      {/* Top Header & Percentage */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-sky-400">
            Agent Execution State
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-xs text-slate-300 capitalize font-medium">
            {currentStage?.replace('_', ' ') || 'Idle'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="font-mono text-sm font-bold text-sky-300">
            {progressPercentage}%
          </span>
        </div>
      </div>

      {/* Progress Bar Track */}
      <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden mb-6 border border-slate-800">
        <div
          className={`h-full transition-all duration-500 ease-out ${
            error
              ? 'bg-rose-500'
              : currentStage === 'completed'
              ? 'bg-emerald-500'
              : 'bg-gradient-to-r from-sky-500 via-sky-400 to-cyan-300'
          }`}
          style={{ width: `${Math.max(5, progressPercentage)}%` }}
        ></div>
      </div>

      {/* Stage Grid Steps */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
        {STAGES.map((s) => {
          const status = getStageStatus(s.key);
          const Icon = s.icon;

          return (
            <div
              key={s.key}
              className={`p-2.5 rounded-xl border flex flex-col items-center text-center transition-all ${
                status === 'completed'
                  ? 'bg-slate-900/60 border-slate-800 text-slate-300'
                  : status === 'active'
                  ? 'bg-sky-950/50 border-sky-500/50 text-sky-200 ring-1 ring-sky-500/30'
                  : status === 'error'
                  ? 'bg-rose-950/30 border-rose-800/50 text-rose-300'
                  : 'bg-slate-950/40 border-slate-900 text-slate-600'
              }`}
            >
              <div className="mb-1.5">
                {status === 'completed' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : status === 'active' ? (
                  <Loader2 className="w-4 h-4 text-sky-400 animate-spin" />
                ) : status === 'error' ? (
                  <AlertCircle className="w-4 h-4 text-rose-400" />
                ) : (
                  <Icon className="w-4 h-4 text-slate-600" />
                )}
              </div>
              <span className="text-[11px] font-medium leading-tight">
                {s.label}
              </span>
            </div>
          );
        })}
      </div>

    </div>
  );
}
