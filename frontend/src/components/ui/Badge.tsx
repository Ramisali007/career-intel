"use client";

interface BadgeProps {
  variant:
    | "exact_match"
    | "strong_match"
    | "partial_match"
    | "related_match"
    | "weak_match"
    | "missing"
    | "conflict"
    | "unknown"
    | "critical"
    | "high_impact"
    | "medium"
    | "optional"
    | "safe"
    | "low"
    | "high"
    | "blocked"
    | "approved"
    | "rejected"
    | "pending"
    | "found"
    | "overused";
  children: React.ReactNode;
  size?: "sm" | "md";
}

const BADGE_STYLES: Record<string, string> = {
  exact_match: "badge-exact-match",
  strong_match: "badge-strong-match",
  partial_match: "badge-partial-match",
  related_match: "badge-partial-match",
  weak_match: "badge-weak-match",
  missing: "badge-missing",
  conflict: "badge-missing",
  unknown: "bg-slate-700/50 text-slate-300 border border-slate-600/50",
  critical: "bg-red-500/15 text-red-400 border border-red-500/30",
  high_impact: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
  medium: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
  optional: "bg-slate-500/15 text-slate-400 border border-slate-500/30",
  safe: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
  low: "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20",
  high: "bg-red-500/15 text-red-400 border border-red-500/30",
  blocked: "bg-red-700/20 text-red-300 border border-red-600/30",
  approved: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
  rejected: "bg-red-500/15 text-red-400 border border-red-500/30",
  pending: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
  found: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
  overused: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
};

const BADGE_LABELS: Record<string, string> = {
  exact_match: "Exact Match",
  strong_match: "Strong Match",
  partial_match: "Partial Match",
  related_match: "Related",
  weak_match: "Weak Match",
  missing: "Missing",
  conflict: "Conflict",
};

export function Badge({ variant, children, size = "sm" }: BadgeProps) {
  const sizeClass = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${sizeClass} ${BADGE_STYLES[variant] || BADGE_STYLES.unknown}`}
    >
      {children || BADGE_LABELS[variant] || variant}
    </span>
  );
}

export function MatchBadge({ classification }: { classification: string }) {
  const variant = classification.toLowerCase().replace(/ /g, "_");
  return (
    <Badge variant={variant as BadgeProps["variant"]}>
      {BADGE_LABELS[variant] || classification.replace(/_/g, " ")}
    </Badge>
  );
}
