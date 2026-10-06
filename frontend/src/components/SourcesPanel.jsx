import React, { useState } from 'react';
import { Globe, ExternalLink, FileText, ChevronDown, ChevronUp, Link as LinkIcon } from 'lucide-react';

export default function SourcesPanel({ sources }) {
  const [selectedSource, setSelectedSource] = useState(null);

  const getDomain = (url) => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return 'web-source';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-md">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-slate-200">
            Discovered & Indexed Sources ({sources.length})
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          Source Provenance Active
        </span>
      </div>

      {sources.length === 0 ? (
        <div className="text-center py-8 text-slate-500 text-xs">
          No external sources indexed yet. Search tools will populate this panel.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {sources.map((src) => {
            const domain = getDomain(src.url);

            return (
              <div
                key={src.id}
                className="bg-slate-900/70 hover:bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between transition-all"
              >
                <div>
                  {/* Source metadata pill */}
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 font-semibold truncate max-w-[180px]">
                      {domain}
                    </span>
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-slate-400 hover:text-sky-300 transition-colors p-1"
                      title="Open external source"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>

                  <h4 className="text-xs font-semibold text-white mb-1.5 line-clamp-2">
                    {src.title}
                  </h4>

                  <p className="text-[11px] text-slate-400 line-clamp-3 mb-3 leading-relaxed">
                    {src.snippet}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-500">
                  <span className="truncate max-w-[200px] font-mono">
                    Query: "{src.query}"
                  </span>
                  {src.content && (
                    <button
                      onClick={() => setSelectedSource(src)}
                      className="text-sky-400 hover:text-sky-300 font-medium underline flex items-center gap-1"
                    >
                      <FileText className="w-3 h-3" />
                      View Text ({src.content.length} chars)
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Content modal */}
      {selectedSource && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full max-h-[80vh] flex flex-col shadow-2xl">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-white line-clamp-1">
                  {selectedSource.title}
                </h4>
                <a
                  href={selectedSource.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-sky-400 hover:underline flex items-center gap-1 mt-0.5"
                >
                  <LinkIcon className="w-3 h-3" />
                  {selectedSource.url}
                </a>
              </div>
              <button
                onClick={() => setSelectedSource(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800 text-xs px-2.5 py-1"
              >
                Close
              </button>
            </div>
            <div className="p-4 overflow-y-auto font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
              {selectedSource.content}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
