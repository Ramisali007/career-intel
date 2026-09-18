"use client";

import { useEffect, useState, useTransition } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart3,
  FileText,
  Target,
  Key,
  Sparkles,
  Zap,
  DownloadCloud,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Check,
  X,
  Layers,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import api from "@/lib/api";
import { Navbar } from "@/components/ui/Navbar";
import { ScoreCard } from "@/components/ui/ScoreCard";
import { MatchBadge } from "@/components/ui/Badge";
import { VisualDiff } from "@/components/ui/VisualDiff";
import { ProcessingStatus } from "@/components/analysis/ProcessingStatus";
import { RecommendationCard } from "@/components/analysis/RecommendationCard";
import SpecularButton from "@/components/ui/SpecularButton";

export default function AnalysisResultsPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  const [analysis, setAnalysis] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [gapData, setGapData] = useState<any>(null);
  const [gapFilter, setGapFilter] = useState<string>("all");
  const [diffData, setDiffData] = useState<any>(null);
  const [optimizing, setOptimizing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [error, setError] = useState("");
  const [, startTransition] = useTransition();

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.replace("/login");
      return;
    }
    loadData();
  }, [analysisId, router]);

  async function loadData() {
    try {
      const data = await api.getAnalysis(analysisId);
      setAnalysis(data);

      if (data.status === "waiting_for_approval" || data.status === "completed") {
        const recs = await api.getRecommendations(analysisId);
        setRecommendations(recs);
      }

      try {
        const gaps = await api.getGapAnalysis(analysisId);
        setGapData(gaps);
      } catch (e) {
        console.warn("Gap analysis data unavailable:", e);
      }

      if (data.latest_version_id) {
        try {
          const diff = await api.getCVVersionDiff(data.latest_version_id);
          setDiffData(diff);
        } catch (e) {
          console.warn("Version diff unavailable:", e);
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRecommendationAction(recId: string, action: string, editedText?: string) {
    try {
      await api.recommendationAction(recId, action, editedText);
      setRecommendations((prev) =>
        prev.map((r) =>
          r.id === recId
            ? {
                ...r,
                status: action === "edit" ? "edited" : action === "approve" ? "approved" : action === "reject" ? "rejected" : "ignored",
                user_edited_text: editedText !== undefined ? editedText : r.user_edited_text,
              }
            : r
        )
      );
    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to update recommendation");
    }
  }

  async function handleApproveAllSafe() {
    try {
      const result = await api.approveAllSafe(analysisId);
      await loadData();
      alert(`Approved ${result.approved_count} safe recommendations. ${result.remaining_count} require manual review.`);
    } catch (err: any) {
      console.error(err);
    }
  }

  async function handleOptimizeAndRescore() {
    const approved = recommendations.filter((r) => r.status === "approved" || r.status === "edited");
    if (approved.length === 0) {
      alert("Please approve at least one recommendation first before generating the optimized version.");
      return;
    }

    setOptimizing(true);
    try {
      const res = await api.optimizeAnalysis(analysisId);
      await loadData();
      if (res.version_id) {
        const diff = await api.getCVVersionDiff(res.version_id);
        setDiffData(diff);
      }
      startTransition(() => {
        setActiveTab("diff");
      });
    } catch (err: any) {
      alert(err.message || "Failed to generate optimized CV.");
    } finally {
      setOptimizing(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-slate-400 font-medium">Computing deterministic career intelligence...</p>
        </div>
      </div>
    );
  }

  const isRunning = analysis && !["completed", "waiting_for_approval", "failed"].includes(analysis.status);
  if (isRunning) {
    return <ProcessingStatus analysisId={analysisId} onComplete={loadData} />;
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 text-white font-sans">
        <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-8 text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-rose-400 mx-auto mb-3" />
          <h2 className="text-xl font-bold text-white">Analysis Not Found</h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-300">{error || "Unable to load analysis results."}</p>
          <button
            onClick={() => router.push("/analyze")}
            className="mt-6 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold px-6 py-2.5 rounded-full text-xs hover:opacity-95 transition-all"
          >
            Start New Analysis
          </button>
        </div>
      </div>
    );
  }

  const scores = analysis.scores || {};
  const origScores = analysis.original_scores || scores;
  const optScores = analysis.optimized_scores;
  const activeScores = optScores || scores;
  const hasOptimizedVersion = !!optScores || !!analysis.latest_version_id || !!analysis.optimized_cv_version_id;

  const tabs = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "requirements", label: "Requirements", icon: FileText },
    { id: "gap_analysis", label: "Gap Matrix", icon: Target },
    { id: "keywords", label: "Keywords", icon: Key },
    { id: "recommendations", label: "Actionable Fixes", icon: Sparkles },
    { id: "diff", label: "Compare & Rescore", icon: Zap },
  ];

  const allGapTiers = gapData?.tiers || {
    already_have: [],
    need_better_evidence: [],
    missing: [],
    nice_to_have: [],
  };

  const filteredGapItems = () => {
    if (gapFilter === "all") {
      return [
        ...allGapTiers.already_have.map((i: any) => ({ ...i, tier: "already_have" })),
        ...allGapTiers.need_better_evidence.map((i: any) => ({ ...i, tier: "need_better_evidence" })),
        ...allGapTiers.missing.map((i: any) => ({ ...i, tier: "missing" })),
        ...allGapTiers.nice_to_have.map((i: any) => ({ ...i, tier: "nice_to_have" })),
      ];
    }
    return (allGapTiers[gapFilter] || []).map((i: any) => ({ ...i, tier: gapFilter }));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950 relative overflow-x-hidden">
      {/* Dynamic Ambient Background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10 space-y-8">
        {/* Header Hero */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2.5 flex-wrap mb-2">
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider ${
                analysis.status === "completed"
                  ? "bg-emerald-950/80 text-emerald-300 border border-emerald-500/40"
                  : "bg-cyan-950/80 text-cyan-300 border border-cyan-500/40"
              }`}>
                {analysis.status.replace(/_/g, " ")}
              </span>
              <span className="text-xs text-slate-400 font-mono">
                ID: {analysisId.slice(0, 8)}
              </span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              {analysis.job_description?.job_title || "Role Alignment Report"}
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 font-normal">
              {analysis.job_description?.company && `Target: ${analysis.job_description.company} • `}
              Candidate CV: {analysis.document?.filename || "Uploaded Resume"}
            </p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <Link
              href={`/export/${analysisId}`}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-full backdrop-blur-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-white border border-slate-700 shadow-lg transition-all"
            >
              <DownloadCloud className="w-4 h-4 text-cyan-400" />
              <span>Export PDF / DOCX</span>
            </Link>

            {recommendations.some((r) => r.status === "approved" || r.status === "edited") && (
              <SpecularButton
                size="md"
                radius={14}
                tint="#ffffff"
                tintOpacity={0.96}
                textColor="#020617"
                lineColor="#ffffff"
                baseColor="#e2e8f0"
                intensity={1.2}
                shineSize={14}
                shineFade={45}
                thickness={1.3}
                disabled={optimizing}
                onClick={handleOptimizeAndRescore}
                className="shadow-xl shadow-cyan-500/15"
              >
                <span className="font-bold flex items-center gap-2">
                  <Zap className="w-4 h-4 text-indigo-600" />
                  {optimizing ? "Generating Version 2..." : "Apply Fixes & Rescore"}
                </span>
              </SpecularButton>
            )}
          </div>
        </div>

        {/* ── Tri-Scoring KPI Hero Grid ── */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <ScoreCard
            label="Job Match Score"
            score={activeScores.job_match_score || 0}
            subtitle={activeScores.job_match_confidence ? `${activeScores.job_match_confidence.toUpperCase()} CONFIDENCE` : "Factual Skill Alignment"}
            tooltip="Measures factual alignment between evidenced skills and requirements. Computed deterministically by the scoring engine."
            breakdown={activeScores.job_match_breakdown}
          />
          <ScoreCard
            label="ATS Compatibility"
            score={activeScores.ats_score || 0}
            subtitle="Format & Parser Ready"
            tooltip="Checks format readability, standard section headers, font safety, and parsability by automated applicant tracking systems."
            breakdown={activeScores.ats_breakdown}
          />
          <ScoreCard
            label="CV Quality Score"
            score={activeScores.quality_score || 0}
            subtitle="Impact & Action Verbs"
            tooltip="Measures clarity, action verbs, quantified achievements (ATTI framework), and professional structural presentation."
            breakdown={activeScores.quality_breakdown}
          />
        </div>

        {/* Triple Engine Callout Banner */}
        <div className="backdrop-blur-2xl bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4.5 flex items-start gap-3 text-xs sm:text-sm">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center flex-shrink-0 mt-0.5">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <p className="text-white font-bold">Deterministic Tri-Scoring Architecture</p>
            <p className="text-slate-300 text-xs mt-0.5 font-normal leading-relaxed">
              These three metrics calculate separate dimensions independently. A resume can score 95% on ATS format compatibility while simultaneously holding a 45% Job Match score if domain experience differs.
            </p>
          </div>
        </div>

        {/* ── Tabs Navigation Bar ── */}
        <div className="flex gap-1.5 overflow-x-auto pb-2 border-b border-slate-800/80">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all flex-shrink-0 ${
                  isActive
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-inner"
                    : "text-slate-400 hover:text-white bg-slate-900/60 border border-slate-800 hover:border-slate-700"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
                {tab.id === "recommendations" && recommendations.length > 0 && (
                  <span className="px-1.5 py-0.2 rounded-full bg-cyan-500/30 text-cyan-300 text-[10px] font-mono">
                    {recommendations.length}
                  </span>
                )}
                {tab.id === "diff" && hasOptimizedVersion && (
                  <span className="px-1.5 py-0.2 rounded-full bg-emerald-500/30 text-emerald-300 text-[10px] font-mono">
                    V{analysis.latest_version_number || 2}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* ── Tab Content Container ── */}
        <div>
          {/* 1. OVERVIEW TAB */}
          {activeTab === "overview" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Strengths */}
              <div className="backdrop-blur-2xl bg-slate-900/80 border border-emerald-500/30 rounded-3xl p-6 sm:p-7 shadow-xl">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  Key Evidenced Strengths
                </h3>
                <div className="space-y-3">
                  {(analysis.strengths || []).length > 0 ? (
                    analysis.strengths.map((s: string, i: number) => (
                      <div key={i} className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
                        <Check className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        <span>{s}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400">No strengths data indexed.</p>
                  )}
                </div>
              </div>

              {/* Critical Gaps */}
              <div className="backdrop-blur-2xl bg-slate-900/80 border border-rose-500/30 rounded-3xl p-6 sm:p-7 shadow-xl">
                <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-rose-400" />
                  Critical Skill Gaps to Bridge
                </h3>
                <div className="space-y-3">
                  {(analysis.critical_gaps || []).length > 0 ? (
                    analysis.critical_gaps.map((g: string, i: number) => (
                      <div key={i} className="flex items-start gap-3 text-xs sm:text-sm text-slate-200">
                        <X className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                        <span>{g}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400">No critical gaps identified.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 2. REQUIREMENTS TAB */}
          {activeTab === "requirements" && (
            <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
              <div className="overflow-x-auto">
                <table className="w-full text-xs sm:text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-950/60">
                      <th className="text-left py-4 px-6 text-xs font-bold uppercase tracking-wider text-slate-400">Requirement</th>
                      <th className="text-left py-4 px-6 text-xs font-bold uppercase tracking-wider text-slate-400">Match Level</th>
                      <th className="text-left py-4 px-6 text-xs font-bold uppercase tracking-wider text-slate-400">Score</th>
                      <th className="text-left py-4 px-6 text-xs font-bold uppercase tracking-wider text-slate-400">CV Evidence / Heuristics</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {(analysis.requirement_matches || []).map((req: any, i: number) => (
                      <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-4 px-6">
                          <span className="font-bold text-white block">{req.requirement_name}</span>
                          <span className="text-[10px] font-mono text-slate-400 uppercase">{req.requirement_priority}</span>
                        </td>
                        <td className="py-4 px-6">
                          <MatchBadge classification={req.classification} />
                        </td>
                        <td className="py-4 px-6 font-mono font-bold text-cyan-300">
                          {Math.round(req.match_score)}%
                        </td>
                        <td className="py-4 px-6 max-w-md">
                          <p className="text-xs text-slate-300 mb-1 leading-relaxed">{req.explanation || "No explanation recorded."}</p>
                          {req.cv_evidence && req.cv_evidence.length > 0 && (
                            <div className="text-[11px] text-emerald-300 font-mono bg-emerald-950/40 rounded-lg p-2 border border-emerald-500/20">
                              Quote: &ldquo;{req.cv_evidence[0].evidence_text}&rdquo;
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 3. GAP ANALYSIS TAB */}
          {activeTab === "gap_analysis" && (
            <div className="space-y-6">
              {/* 4-Tier Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { key: "already_have", label: "Already Have", count: gapData?.summary?.already_have_count || 0, sub: "Evidenced in CV", color: "emerald" },
                  { key: "need_better_evidence", label: "Need Evidence", count: gapData?.summary?.need_better_evidence_count || 0, sub: "Vague or unquantified", color: "amber" },
                  { key: "missing", label: "Missing Must-Have", count: gapData?.summary?.missing_count || 0, sub: "Critical gap", color: "rose" },
                  { key: "nice_to_have", label: "Nice To Have", count: gapData?.summary?.nice_to_have_count || 0, sub: "Bonus skills", color: "cyan" },
                ].map((tier) => (
                  <button
                    key={tier.key}
                    onClick={() => setGapFilter(tier.key)}
                    className={`backdrop-blur-2xl rounded-2xl p-4 text-left border transition-all ${
                      gapFilter === tier.key
                        ? "bg-slate-800 border-cyan-400 shadow-lg"
                        : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-1">
                      {tier.label}
                    </span>
                    <div className="text-3xl font-extrabold text-white font-mono">
                      {tier.count}
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">{tier.sub}</p>
                  </button>
                ))}
              </div>

              {/* Requirement Gap Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {filteredGapItems().map((item: any, idx: number) => (
                  <div
                    key={idx}
                    className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-[10px] uppercase font-mono font-bold text-slate-400 block">
                          {item.category}
                        </span>
                        <h4 className="text-base font-bold text-white">{item.name}</h4>
                      </div>
                      <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                        {item.tier.replace(/_/g, " ")}
                      </span>
                    </div>

                    <div>
                      <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                        <span>Evidence Match</span>
                        <span className="font-mono font-bold text-white">{Math.round(item.match_score)}%</span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                        <div
                          className="h-full rounded-full bg-cyan-400 transition-all"
                          style={{ width: `${Math.max(5, item.match_score)}%` }}
                        />
                      </div>
                    </div>

                    {item.evidence_summary && (
                      <div className="text-xs bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-slate-300 leading-relaxed font-mono">
                        &ldquo;{item.evidence_summary}&rdquo;
                      </div>
                    )}

                    {item.remediation_advice && (
                      <div className="text-xs bg-cyan-950/30 p-3 rounded-xl border border-cyan-500/20 text-cyan-200 flex items-start gap-2">
                        <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                        <span>{item.remediation_advice}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 4. KEYWORDS TAB */}
          {activeTab === "keywords" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {["FOUND", "PARTIAL", "MISSING"].map((status) => {
                const filtered = (analysis.keyword_intelligence || []).filter(
                  (k: any) => (k.status || "").toUpperCase() === status
                );
                return (
                  <div key={status} className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
                    <h3 className="text-sm font-bold text-white mb-4 flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <span className={`w-2.5 h-2.5 rounded-full ${
                          status === "FOUND" ? "bg-emerald-400" : status === "PARTIAL" ? "bg-amber-400" : "bg-rose-400"
                        }`} />
                        {status} ({filtered.length})
                      </span>
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {filtered.map((k: any, i: number) => (
                        <span
                          key={i}
                          className="px-3 py-1.5 rounded-xl text-xs font-mono font-semibold bg-slate-950/80 border border-slate-800 text-slate-200"
                        >
                          {k.keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* 5. RECOMMENDATIONS TAB */}
          {activeTab === "recommendations" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between flex-wrap gap-4 backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                <button
                  onClick={handleApproveAllSafe}
                  className="bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 px-4 py-2 rounded-xl text-xs font-bold hover:bg-emerald-500/25 transition-colors flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Approve All Safe Recommendations
                </button>
                <span className="text-xs text-slate-400">
                  {recommendations.filter((r) => r.status === "pending").length} pending human review
                </span>
              </div>

              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <RecommendationCard
                    key={rec.id}
                    rec={rec}
                    onAction={handleRecommendationAction}
                  />
                ))}
              </div>
            </div>
          )}

          {/* 6. COMPARE & DIFF TAB */}
          {activeTab === "diff" && (
            <div className="space-y-6">
              {hasOptimizedVersion ? (
                <>
                  <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xl space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-base font-bold text-white flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-emerald-400" />
                        Before & After Score Improvements
                      </h3>
                      <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40">
                        Version 2 (Optimized)
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                      <div className="bg-slate-950/70 rounded-2xl p-4 border border-slate-800">
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Job Match</span>
                        <div className="flex items-baseline gap-3 mt-2 font-mono flex-wrap">
                          <span className="text-base text-slate-400 line-through">
                            {Math.round(origScores.job_match_score || 0)}%
                          </span>
                          <span className="text-2xl font-bold text-emerald-400">
                            {Math.round(optScores?.job_match_score || activeScores.job_match_score || 0)}%
                          </span>
                          {optScores && (() => {
                            const delta = Math.round((optScores.job_match_score || 0) - (origScores.job_match_score || 0));
                            return (
                              <span className={`text-xs font-bold px-2 py-0.5 rounded-md border ${
                                delta >= 0
                                  ? "text-emerald-400 bg-emerald-950/80 border-emerald-500/40"
                                  : "text-rose-400 bg-rose-950/80 border-rose-500/40"
                              }`}>
                                {delta >= 0 ? `+${delta}%` : `${delta}%`}
                              </span>
                            );
                          })()}
                        </div>
                      </div>

                      <div className="bg-slate-950/70 rounded-2xl p-4 border border-slate-800">
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">ATS Score</span>
                        <div className="flex items-baseline gap-3 mt-2 font-mono flex-wrap">
                          <span className="text-base text-slate-400 line-through">
                            {Math.round(origScores.ats_score || 0)}%
                          </span>
                          <span className="text-2xl font-bold text-cyan-400">
                            {Math.round(optScores?.ats_score || activeScores.ats_score || 0)}%
                          </span>
                          {optScores && (() => {
                            const delta = Math.round((optScores.ats_score || 0) - (origScores.ats_score || 0));
                            return (
                              <span className={`text-xs font-bold px-2 py-0.5 rounded-md border ${
                                delta >= 0
                                  ? "text-cyan-400 bg-cyan-950/80 border-cyan-500/40"
                                  : "text-rose-400 bg-rose-950/80 border-rose-500/40"
                              }`}>
                                {delta >= 0 ? `+${delta}%` : `${delta}%`}
                              </span>
                            );
                          })()}
                        </div>
                      </div>

                      <div className="bg-slate-950/70 rounded-2xl p-4 border border-slate-800">
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Quality</span>
                        <div className="flex items-baseline gap-3 mt-2 font-mono flex-wrap">
                          <span className="text-base text-slate-400 line-through">
                            {Math.round(origScores.quality_score || 0)}%
                          </span>
                          <span className="text-2xl font-bold text-purple-400">
                            {Math.round(optScores?.quality_score || activeScores.quality_score || 0)}%
                          </span>
                          {optScores && (() => {
                            const delta = Math.round((optScores.quality_score || 0) - (origScores.quality_score || 0));
                            return (
                              <span className={`text-xs font-bold px-2 py-0.5 rounded-md border ${
                                delta >= 0
                                  ? "text-purple-400 bg-purple-950/80 border-purple-500/40"
                                  : "text-rose-400 bg-rose-950/80 border-rose-500/40"
                              }`}>
                                {delta >= 0 ? `+${delta}%` : `${delta}%`}
                              </span>
                            );
                          })()}
                        </div>
                      </div>
                    </div>
                  </div>

                  {diffData?.diff && (
                    <VisualDiff diff={diffData.diff} versionNumber={diffData.version_number || 2} />
                  )}
                </>
              ) : (
                <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-10 text-center">
                  <Zap className="w-12 h-12 text-cyan-400 mx-auto mb-3" />
                  <h3 className="text-lg font-bold text-white">No Optimized Version Created Yet</h3>
                  <p className="mt-2 text-xs sm:text-sm text-slate-300 max-w-md mx-auto">
                    Review suggestions in Actionable Fixes, then apply changes to generate Version 2 and inspect visual diffs.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
