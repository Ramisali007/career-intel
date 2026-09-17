"use client";

import { useState } from "react";

interface DiffSpan {
  type: "unchanged" | "added" | "removed";
  text: string;
}

interface BulletDiff {
  type: "unchanged" | "added" | "removed" | "modified";
  original_text: string;
  modified_text: string;
  highlighted_diff?: DiffSpan[];
}

interface ExperienceDiff {
  title: string;
  company: string;
  period: string;
  bullets: BulletDiff[];
}

interface DiffReport {
  summary?: BulletDiff | null;
  experience?: ExperienceDiff[];
  skills?: {
    added: string[];
    removed: string[];
    retained: string[];
  };
  stats?: {
    added_count: number;
    modified_count: number;
    removed_count: number;
    unchanged_count: number;
  };
}

interface VisualDiffProps {
  diff: DiffReport;
  versionNumber?: number;
}

export function VisualDiff({ diff, versionNumber = 2 }: VisualDiffProps) {
  const [viewMode, setViewMode] = useState<"split" | "unified">("unified");
  const stats = diff.stats || { added_count: 0, modified_count: 0, removed_count: 0, unchanged_count: 0 };

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Header & Controls */}
      <div className="glass rounded-xl p-5 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center gap-2">
            <span>🔍</span> Visual Document Diff (Original vs Version {versionNumber})
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Section-by-section comparison of approved enhancements without fabrication
          </p>
        </div>

        {/* Change Stats Chips */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            +{stats.added_count} Added
          </span>
          <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            ~{stats.modified_count} Modified
          </span>
          {stats.removed_count > 0 && (
            <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
              -{stats.removed_count} Removed
            </span>
          )}
          <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
            {stats.unchanged_count} Unchanged
          </span>

          {/* View Toggle */}
          <div className="ml-2 flex items-center bg-slate-900 border border-slate-800 rounded-lg p-0.5">
            <button
              onClick={() => setViewMode("unified")}
              className={`px-3 py-1 text-xs rounded-md font-medium transition-all ${
                viewMode === "unified" ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400 hover:text-white"
              }`}
            >
              Unified
            </button>
            <button
              onClick={() => setViewMode("split")}
              className={`px-3 py-1 text-xs rounded-md font-medium transition-all ${
                viewMode === "split" ? "bg-cyan-500/20 text-cyan-400" : "text-slate-400 hover:text-white"
              }`}
            >
              Split View
            </button>
          </div>
        </div>
      </div>

      {/* 1. Professional Summary Diff */}
      {diff.summary && (
        <div className="glass rounded-xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-white flex items-center gap-2">
              <span>📝</span> Professional Summary
            </h4>
            <span
              className={`text-xs px-2 py-0.5 rounded ${
                diff.summary.type === "modified"
                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  : diff.summary.type === "added"
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {diff.summary.type.toUpperCase()}
            </span>
          </div>

          {viewMode === "unified" ? (
            <div className="bg-slate-950/80 rounded-lg p-3 text-sm font-mono border border-slate-800/80 leading-relaxed">
              {diff.summary.type === "modified" && diff.summary.highlighted_diff ? (
                <div>
                  {diff.summary.highlighted_diff.map((span, idx) => (
                    <span
                      key={idx}
                      className={
                        span.type === "added"
                          ? "bg-emerald-500/20 text-emerald-300 px-1 rounded"
                          : span.type === "removed"
                          ? "bg-rose-500/20 text-rose-400 line-through px-1 rounded"
                          : "text-slate-300"
                      }
                    >
                      {span.text}{" "}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-slate-300">{diff.summary.modified_text || diff.summary.original_text}</p>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-mono">
              <div className="bg-rose-950/20 border border-rose-900/30 rounded-lg p-3">
                <div className="text-xs text-rose-400 mb-1 font-semibold">ORIGINAL</div>
                <p className="text-slate-300 leading-relaxed">{diff.summary.original_text || "(empty)"}</p>
              </div>
              <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-lg p-3">
                <div className="text-xs text-emerald-400 mb-1 font-semibold">OPTIMIZED</div>
                <p className="text-emerald-100 leading-relaxed">{diff.summary.modified_text}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 2. Experience Bullets Diff */}
      {diff.experience && diff.experience.length > 0 && (
        <div className="glass rounded-xl p-5 border border-slate-800 space-y-5">
          <h4 className="text-sm font-semibold text-white flex items-center gap-2">
            <span>💼</span> Work Experience Bullets
          </h4>

          {diff.experience.map((exp, expIdx) => (
            <div key={expIdx} className="bg-slate-900/60 rounded-xl p-4 border border-slate-800/80 space-y-3">
              <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-slate-800 pb-2">
                <div>
                  <span className="font-semibold text-white text-sm">{exp.title}</span>
                  <span className="text-slate-400 text-sm ml-2">@ {exp.company}</span>
                </div>
                <span className="text-xs text-slate-500 font-mono">{exp.period}</span>
              </div>

              <div className="space-y-3">
                {exp.bullets.map((b, bIdx) => (
                  <div key={bIdx}>
                    {viewMode === "unified" ? (
                      <div
                        className={`p-3 rounded-lg text-xs md:text-sm font-mono leading-relaxed border ${
                          b.type === "modified"
                            ? "bg-amber-950/15 border-amber-900/30"
                            : b.type === "added"
                            ? "bg-emerald-950/15 border-emerald-900/30"
                            : "bg-slate-950/50 border-slate-800/60 text-slate-400"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <span
                            className={`text-[10px] uppercase px-1.5 py-0.5 rounded font-bold ${
                              b.type === "modified"
                                ? "bg-amber-500/20 text-amber-400"
                                : b.type === "added"
                                ? "bg-emerald-500/20 text-emerald-400"
                                : "bg-slate-800 text-slate-500"
                            }`}
                          >
                            {b.type}
                          </span>
                        </div>

                        {b.type === "modified" && b.highlighted_diff ? (
                          <div>
                            {b.highlighted_diff.map((span, sIdx) => (
                              <span
                                key={sIdx}
                                className={
                                  span.type === "added"
                                    ? "bg-emerald-500/25 text-emerald-200 px-1 rounded"
                                    : span.type === "removed"
                                    ? "bg-rose-500/25 text-rose-400 line-through px-1 rounded"
                                    : "text-slate-300"
                                }
                              >
                                {span.text}{" "}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className={b.type === "added" ? "text-emerald-200" : "text-slate-400"}>
                            {b.modified_text || b.original_text}
                          </p>
                        )}
                      </div>
                    ) : (
                      /* Split View */
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs md:text-sm font-mono">
                        <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-2.5">
                          <div className="text-[10px] text-slate-500 mb-1">ORIGINAL</div>
                          <p className="text-slate-400">{b.original_text || "(none)"}</p>
                        </div>
                        <div
                          className={`rounded-lg p-2.5 border ${
                            b.type === "modified"
                              ? "bg-amber-950/20 border-amber-900/40 text-amber-100"
                              : b.type === "added"
                              ? "bg-emerald-950/20 border-emerald-900/40 text-emerald-100"
                              : "bg-slate-950/70 border-slate-800/80 text-slate-400"
                          }`}
                        >
                          <div className="text-[10px] text-emerald-400 mb-1">OPTIMIZED</div>
                          <p>{b.modified_text}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 3. Skills Diff */}
      {diff.skills && (
        <div className="glass rounded-xl p-5 border border-slate-800">
          <h4 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <span>⚡</span> Skills & Keyword Alignment
          </h4>
          <div className="space-y-3">
            {diff.skills.added.length > 0 && (
              <div>
                <span className="text-xs text-emerald-400 font-medium block mb-1.5">
                  Added Keywords & Targeted Technologies (+{diff.skills.added.length}):
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {diff.skills.added.map((s, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-md text-xs bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1 font-mono"
                    >
                      <span>+</span> {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div>
              <span className="text-xs text-slate-400 font-medium block mb-1.5">
                Retained Core Competencies ({diff.skills.retained.length}):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {diff.skills.retained.map((s, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 rounded text-xs bg-slate-900 text-slate-300 border border-slate-800"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
