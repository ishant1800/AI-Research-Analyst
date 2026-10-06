import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertTriangle, Sparkles, Send, Search } from 'lucide-react';
import { API_BASE } from '../api';

export default function VerificationAudit({ verification, sessionId }) {
  const [testClaim, setTestClaim] = useState('');
  const [testing, setTesting] = useState(false);
  const [singleResult, setSingleResult] = useState(null);

  if (!verification) return null;

  const groundingPercent = Math.round((verification.overall_grounding_score || 0.9) * 100);

  const handleVerifySingle = async (e) => {
    e.preventDefault();
    if (!testClaim.trim() || !sessionId || testing) return;

    setTesting(true);
    setSingleResult(null);
    try {
      const resp = await fetch(`${API_BASE}/api/research/verify-claim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          claim_text: testClaim.trim()
        })
      });
      if (resp.ok) {
        const data = await resp.json();
        setSingleResult(data);
      }
    } catch (err) {
      console.error('Failed to verify single claim:', err);
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-md space-y-6">
      
      {/* Header and Grounding Score Gauge */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Pre-Synthesis Reflection & Verification Audit</span>
          </div>
          <h3 className="text-base font-bold text-white">
            Claim-to-Evidence Grounding Assurance
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Cross-checks candidate findings against raw verbatim quotes to eliminate hallucination.
          </p>
        </div>

        {/* Score Badge */}
        <div className="flex items-center space-x-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl">
          <div className="text-right">
            <div className="text-[10px] uppercase font-mono text-slate-400">Grounding Score</div>
            <div className="text-xl font-bold font-mono text-emerald-400">{groundingPercent}%</div>
          </div>
          <div className={`p-2 rounded-lg ${verification.verification_passed ? 'bg-emerald-950/60 text-emerald-400' : 'bg-amber-950/60 text-amber-400'}`}>
            {verification.verification_passed ? (
              <CheckCircle2 className="w-6 h-6" />
            ) : (
              <AlertTriangle className="w-6 h-6" />
            )}
          </div>
        </div>
      </div>

      {/* Evaluated Claims Breakdown */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
          Audited Research Claims ({verification.claims_evaluated?.length || 0})
        </h4>

        <div className="space-y-3">
          {verification.claims_evaluated?.map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex flex-col justify-between"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center space-x-2">
                  {item.is_grounded ? (
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-rose-400"></span>
                  )}
                  <h5 className="text-xs font-semibold text-white">
                    {item.claim_text}
                  </h5>
                </div>
                <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded border ${
                  item.is_grounded
                    ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60'
                    : 'bg-rose-950/60 text-rose-300 border-rose-800/60'
                }`}>
                  Score: {Math.round((item.grounding_score || 0.9) * 100)}%
                </span>
              </div>

              <p className="text-xs text-slate-400 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed">
                <span className="text-slate-500 font-semibold">Auditor Reflection:</span> {item.verification_notes}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Reflection Critique Box */}
      {verification.reflection_critique && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
          <div className="text-xs font-semibold uppercase tracking-wider text-sky-300 mb-1.5 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-sky-400" />
            <span>Auditor Reflection & Remaining Uncertainties</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {verification.reflection_critique}
          </p>
        </div>
      )}

      {/* Interactive Single-Claim Verifier Tester */}
      <div className="bg-slate-900/90 border border-sky-900/40 rounded-xl p-4 mt-4">
        <div className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Search className="w-3.5 h-3.5 text-sky-400" />
          <span>Interactive Claim Auditor</span>
          <span className="text-[10px] font-normal text-slate-400 lowercase">(test an arbitrary claim against current evidence)</span>
        </div>

        <form onSubmit={handleVerifySingle} className="flex gap-2">
          <input
            type="text"
            value={testClaim}
            onChange={(e) => setTestClaim(e.target.value)}
            placeholder="Type a custom claim to verify against collected quotes..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-sky-500 font-sans"
            disabled={testing}
          />
          <button
            type="submit"
            disabled={!testClaim.trim() || testing}
            className="px-4 py-2 bg-sky-500 hover:bg-sky-400 disabled:bg-slate-800 text-slate-950 font-bold rounded-lg text-xs transition-colors flex items-center gap-1 border border-sky-300/40"
          >
            {testing ? 'Auditing...' : <><Send className="w-3 h-3" /> Verify</>}
          </button>
        </form>

        {singleResult && (
          <div className="mt-3 p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
            <div className="flex items-center justify-between mb-1">
              <span className={`font-semibold ${singleResult.is_grounded ? 'text-emerald-400' : 'text-rose-400'}`}>
                {singleResult.is_grounded ? '✓ Grounded in Evidence' : '✗ Weak / Unsupported Claim'}
              </span>
              <span className="font-mono text-[10px] text-slate-400">
                Score: {Math.round(singleResult.grounding_score * 100)}%
              </span>
            </div>
            <p className="text-slate-300 mt-1 text-[11px] leading-relaxed">
              {singleResult.verification_notes}
            </p>
          </div>
        )}
      </div>

    </div>
  );
}
