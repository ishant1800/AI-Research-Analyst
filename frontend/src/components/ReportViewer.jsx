import React, { useState } from 'react';
import {
  FileText,
  Download,
  Copy,
  Check,
  ExternalLink,
  BookOpen,
  Table,
  Split,
  AlertTriangle,
  BookmarkCheck,
  Printer
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function ReportViewer({ report }) {
  const [copied, setCopied] = useState(false);

  if (!report) return null;

  // Render markdown with citations styled as clickable pills
  const renderWithCitations = (text) => {
    if (!text) return null;
    // Replace citation tags like [1] or [2] with styled anchor tags
    return (
      <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
        {text}
      </div>
    );
  };

  const handleCopyMarkdown = () => {
    let md = `# ${report.title}\n\n`;
    md += `## Executive Summary\n${report.executive_summary}\n\n`;
    md += `## Methodology\n${report.research_methodology}\n\n`;
    md += `## Key Findings\n`;
    report.key_findings?.forEach((kf) => {
      md += `### ${kf.headline} (Confidence: ${kf.confidence})\n${kf.detailed_explanation}\n\n`;
    });
    if (report.comparison_tables?.length > 0) {
      md += `## Comparative Matrices\n`;
      report.comparison_tables.forEach((t) => {
        md += `### ${t.title}\n`;
        md += `| ${t.headers.join(' | ')} |\n`;
        md += `| ${t.headers.map(() => '---').join(' | ')} |\n`;
        t.rows?.forEach((r) => {
          const rowVals = t.headers.slice(1).map((h) => r.values[h] || '-');
          md += `| ${r.dimension} | ${rowVals.join(' | ')} |\n`;
        });
        md += `\n`;
      });
    }
    if (report.conflicting_information?.length > 0) {
      md += `## Conflicting Information & Nuance\n`;
      report.conflicting_information.forEach((c) => {
        md += `- **${c.topic}**: ${c.claim_a} (${c.source_a_title}) vs ${c.claim_b} (${c.source_b_title}). *Root cause: ${c.possible_reason}*\n`;
      });
      md += `\n`;
    }
    md += `## Limitations\n`;
    report.limitations?.forEach((lim) => {
      md += `- ${lim}\n`;
    });
    md += `\n## Conclusion\n${report.conclusion}\n\n`;
    md += `## References\n`;
    report.references?.forEach((ref) => {
      md += `[${ref.citation_index}] ${ref.title} - ${ref.url}\n`;
    });

    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `research-report-${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <article className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 shadow-2xl space-y-8 bg-slate-950/90 text-slate-100">
      
      {/* Report Header Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center space-x-2 text-sky-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <BookOpen className="w-4 h-4" />
            <span>Structured Intelligence Report</span>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400 font-mono text-[10px]">
              Generated {new Date(report.generated_at || Date.now()).toLocaleDateString()}
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
            {report.title}
          </h2>
        </div>

        {/* Action buttons */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <button
            onClick={handleCopyMarkdown}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-850 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white transition-colors"
            title="Copy as Markdown"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy MD'}</span>
          </button>
          <button
            onClick={handleDownloadJson}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-850 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white transition-colors"
            title="Download JSON Report"
          >
            <Download className="w-3.5 h-3.5" />
            <span>JSON</span>
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-xs font-bold text-slate-950 transition-colors shadow-sm shadow-sky-500/25 border border-sky-300/40"
            title="Print or Save PDF"
          >
            <Printer className="w-3.5 h-3.5" />
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* 1. Executive Summary */}
      <section className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6">
        <h3 className="text-xs font-bold uppercase tracking-wider text-sky-300 mb-3 flex items-center gap-2">
          <BookmarkCheck className="w-4 h-4 text-sky-400" />
          Executive Summary
        </h3>
        <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">
          {report.executive_summary}
        </p>
      </section>

      {/* 2. Research Methodology */}
      <section>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
          Methodology & Provenance Architecture
        </h3>
        <p className="text-slate-300 text-xs leading-relaxed bg-slate-900/60 p-4 rounded-xl border border-slate-800">
          {report.research_methodology}
        </p>
      </section>

      {/* 3. Key Findings */}
      <section className="space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Key Findings & Attributed Evidence ({report.key_findings?.length || 0})
        </h3>

        <div className="space-y-4">
          {report.key_findings?.map((kf, idx) => (
            <div
              key={idx}
              className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-sky-950 text-sky-300 border border-sky-800 text-[11px] font-mono flex items-center justify-center">
                    {idx + 1}
                  </span>
                  {kf.headline}
                </h4>
                <div className="flex items-center space-x-2">
                  <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${
                    kf.confidence === 'high'
                      ? 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60'
                      : 'bg-amber-950/60 text-amber-300 border-amber-800/60'
                  }`}>
                    {kf.confidence} confidence
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mt-2 pl-7">
                {kf.detailed_explanation}
              </p>

              {kf.source_citations && kf.source_citations.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center space-x-2 pl-7">
                  <span className="text-[10px] text-slate-500 font-medium">Source Citations:</span>
                  <div className="flex gap-1">
                    {kf.source_citations.map((cite, cIdx) => (
                      <span
                        key={cIdx}
                        className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-sky-950 text-sky-300 border border-sky-800"
                      >
                        {cite}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 4. Comparison Tables */}
      {report.comparison_tables && report.comparison_tables.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Table className="w-4 h-4 text-cyan-400" />
            Structured Comparative Matrices
          </h3>

          {report.comparison_tables.map((tbl, tIdx) => (
            <div key={tIdx} className="overflow-x-auto border border-slate-800 rounded-xl bg-slate-900/60 p-4">
              <h4 className="text-xs font-semibold text-white mb-3">{tbl.title}</h4>
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950">
                    {tbl.headers?.map((header, hIdx) => (
                      <th key={hIdx} className="p-3 text-slate-400 font-semibold tracking-wider">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {tbl.rows?.map((row, rIdx) => (
                    <tr key={rIdx} className="hover:bg-slate-850/50 transition-colors">
                      <td className="p-3 font-medium text-white">{row.dimension}</td>
                      {tbl.headers.slice(1).map((h, valIdx) => (
                        <td key={valIdx} className="p-3 text-slate-300 font-mono">
                          {row.values[h] || '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </section>
      )}

      {/* 5. Conflicting Information */}
      {report.conflicting_information && report.conflicting_information.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
            <Split className="w-4 h-4 text-amber-400" />
            Synthesized Disagreements & Divergence
          </h3>
          <div className="space-y-3">
            {report.conflicting_information.map((cf) => (
              <div key={cf.id} className="bg-slate-900/70 border border-amber-900/40 rounded-xl p-4 text-xs">
                <div className="font-semibold text-amber-300 mb-1">{cf.topic}</div>
                <div className="text-slate-300 space-y-1 mb-2">
                  <div><span className="text-sky-400 font-medium">Claim A:</span> {cf.claim_a}</div>
                  <div><span className="text-cyan-400 font-medium">Claim B:</span> {cf.claim_b}</div>
                </div>
                <div className="text-[11px] text-slate-400 italic">
                  <span className="font-semibold text-slate-300">Reconciliation:</span> {cf.possible_reason}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 6. Limitations */}
      {report.limitations && report.limitations.length > 0 && (
        <section>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            Identified Research Limitations & Data Gaps
          </h3>
          <ul className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-1.5 text-xs text-slate-300">
            {report.limitations.map((lim, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-amber-400 font-bold">•</span>
                <span>{lim}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* 7. Conclusion */}
      <section className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-6">
        <h3 className="text-xs font-bold uppercase tracking-wider text-sky-400 mb-2">
          Strategic Conclusion
        </h3>
        <p className="text-slate-200 text-sm leading-relaxed">
          {report.conclusion}
        </p>
      </section>

      {/* 8. Sources & References */}
      <section id="references-section" className="pt-4 border-t border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
          Cited References & Source Directory ({report.references?.length || 0})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {report.references?.map((ref) => (
            <div
              key={ref.citation_index}
              className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 flex items-start space-x-3 text-xs"
            >
              <span className="px-2 py-0.5 rounded bg-sky-950 text-sky-300 font-mono font-bold border border-sky-800">
                [{ref.citation_index}]
              </span>
              <div className="flex-1 min-w-0">
                <a
                  href={ref.url}
                  target="_blank"
                  rel="noreferrer"
                  className="font-medium text-slate-200 hover:text-sky-400 transition-colors flex items-center gap-1 line-clamp-1"
                >
                  <span className="truncate">{ref.title}</span>
                  <ExternalLink className="w-3 h-3 flex-shrink-0" />
                </a>
                <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                  {ref.key_contribution}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

    </article>
  );
}
