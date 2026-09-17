"use client";

import { useState } from "react";
import { Badge, MatchBadge } from "@/components/ui/Badge";

interface RecommendationCardProps {
  rec: {
    id: string;
    title: string;
    category: string;
    status: string;
    impact: string;
    reason: string;
    source_requirement: string;
    section: string;
    current_text: string;
    proposed_text: string;
    user_edited_text: string | null;
    evidence: string[];
    confidence: number;
    factual_risk: string;
    approval_required: boolean;
    jd_context: string;
    keyword_addressed: string | null;
  };
  onAction: (recId: string, action: string, editedText?: string) => Promise<void>;
}

export function RecommendationCard({ rec, onAction }: RecommendationCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(rec.proposed_text);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  async function handleAction(action: string) {
    setActionLoading(action);
    try {
      if (action === "edit") {
        await onAction(rec.id, "edit", editedText);
        setIsEditing(false);
      } else {
        await onAction(rec.id, action);
      }
    } finally {
      setActionLoading(null);
    }
  }

  const riskColors: Record<string, string> = {
    safe: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    low: "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
    medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    high: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    blocked: "bg-red-500/15 text-red-400 border-red-500/30",
  };

  const statusColors: Record<string, string> = {
    approved: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    rejected: "bg-rose-500/15 text-rose-400 border-rose-500/30",
    edited: "bg-violet-500/15 text-violet-400 border-violet-500/30",
    ignored: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  };

  return (
    <div className="glass rounded-2xl p-6 border border-slate-800 transition-all">
      {/* Header: Category + Risk + Status */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider border ${
              rec.category === "critical"
                ? "bg-rose-500/15 text-rose-400 border-rose-500/30"
                : rec.category === "high_impact"
                ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                : rec.category === "medium"
                ? "bg-cyan-500/15 text-cyan-400 border-cyan-500/30"
                : "bg-slate-500/15 text-slate-400 border-slate-500/30"
            }`}
          >
            {rec.category.replace(/_/g, " ")}
          </span>
          <span
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider border ${
              riskColors[rec.factual_risk] || riskColors.safe
            }`}
          >
            Risk: {rec.factual_risk}
          </span>
          {rec.status !== "pending" && (
            <span
              className={`px-2.5 py-1 rounded-lg text-xs font-semibold uppercase tracking-wider border ${
                statusColors[rec.status] || statusColors.ignored
              }`}
            >
              {rec.status}
            </span>
          )}
        </div>
        <span className="text-xs text-slate-500 shrink-0">
          Confidence: {Math.round(rec.confidence * 100)}%
        </span>
      </div>

      {/* Title + Reason */}
      <h4 className="text-base font-semibold text-white mb-2">{rec.title}</h4>
      <p className="text-sm text-slate-400 mb-4">{rec.reason}</p>

      {/* Current vs Proposed / Edit Mode */}
      {rec.current_text && (
        <div className="mb-4">
          {isEditing ? (
            /* Edit Mode */
            <div className="space-y-3">
              <div className="bg-rose-500/5 border border-rose-500/20 rounded-xl p-4">
                <p className="text-xs font-medium text-rose-400 mb-2 font-mono">
                  Current Text in CV
                </p>
                <p className="text-sm text-slate-300 font-mono">{rec.current_text}</p>
              </div>
              <div className="bg-violet-500/5 border border-violet-500/20 rounded-xl p-4">
                <p className="text-xs font-medium text-violet-400 mb-2 font-mono">
                  ✏️ Edit Proposed Text
                </p>
                <textarea
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  rows={4}
                  className="w-full bg-slate-900/80 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:ring-2 focus:ring-violet-500/50 resize-y"
                />
                <div className="flex items-center gap-2 mt-3">
                  <button
                    onClick={() => handleAction("edit")}
                    disabled={actionLoading === "edit"}
                    className="bg-violet-500/15 text-violet-400 border border-violet-500/30 px-4 py-2 rounded-lg text-sm font-medium hover:bg-violet-500/25 transition-colors disabled:opacity-50"
                  >
                    {actionLoading === "edit" ? "Saving..." : "💾 Save Edit & Approve"}
                  </button>
                  <button
                    onClick={() => {
                      setIsEditing(false);
                      setEditedText(rec.proposed_text);
                    }}
                    className="text-slate-400 px-3 py-2 rounded-lg text-sm hover:text-white transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* View Mode */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-rose-500/5 border border-rose-500/20 rounded-xl p-4">
                <p className="text-xs font-medium text-rose-400 mb-2 font-mono">
                  Current Text in CV
                </p>
                <p className="text-sm text-slate-300 font-mono">{rec.current_text}</p>
              </div>
              <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4">
                <p className="text-xs font-medium text-emerald-400 mb-2 font-mono">
                  {rec.user_edited_text ? "User-Edited Replacement" : "Proposed Optimized Replacement"}
                </p>
                <p className="text-sm text-slate-300 font-mono">
                  {rec.user_edited_text || rec.proposed_text}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Evidence */}
      {rec.evidence && rec.evidence.length > 0 && (
        <div className="mb-4 text-xs bg-slate-900/50 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-500 font-semibold block mb-1">SUPPORTING EVIDENCE:</span>
          <ul className="list-disc list-inside space-y-0.5 text-slate-400">
            {rec.evidence.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      {rec.status === "pending" && !isEditing && (
        <div className="flex items-center gap-2 pt-3 border-t border-slate-800/50 flex-wrap">
          <button
            onClick={() => handleAction("approve")}
            disabled={actionLoading === "approve"}
            className="bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-3.5 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium hover:bg-emerald-500/25 transition-colors disabled:opacity-50"
          >
            {actionLoading === "approve" ? "..." : "✅ Approve"}
          </button>
          <button
            onClick={() => setIsEditing(true)}
            className="bg-violet-500/10 text-violet-400 border border-violet-500/20 px-3.5 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium hover:bg-violet-500/20 transition-colors"
          >
            ✏️ Edit
          </button>
          <button
            onClick={() => handleAction("reject")}
            disabled={actionLoading === "reject"}
            className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-3.5 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium hover:bg-rose-500/20 transition-colors disabled:opacity-50"
          >
            {actionLoading === "reject" ? "..." : "❌ Reject"}
          </button>
          <button
            onClick={() => handleAction("ignore")}
            disabled={actionLoading === "ignore"}
            className="text-slate-400 px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm hover:text-slate-200 transition-colors disabled:opacity-50"
          >
            Skip
          </button>
        </div>
      )}
    </div>
  );
}
