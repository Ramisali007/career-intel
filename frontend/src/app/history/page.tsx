"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  History,
  Search,
  BarChart3,
  CheckCircle2,
  Target,
  Trophy,
  Trash2,
  Calendar,
  Clock,
  Briefcase,
  ArrowUpRight,
  Sparkles,
  Layers,
} from "lucide-react";
import api from "@/lib/api";
import { Navbar } from "@/components/ui/Navbar";
import SpecularButton from "@/components/ui/SpecularButton";

interface AnalysisItem {
  id: string;
  status: string;
  job_title: string;
  company: string;
  job_match_score: number | null;
  ats_score: number | null;
  quality_score: number | null;
  created_at: string;
  processing_time: number | null;
}

function getScoreBadge(score: number | null) {
  if (score == null) return { color: "text-slate-400 bg-slate-900 border-slate-800", label: "—" };
  if (score >= 85) return { color: "text-emerald-300 bg-emerald-950/60 border-emerald-500/30", label: `${Math.round(score)}%` };
  if (score >= 70) return { color: "text-cyan-300 bg-cyan-950/60 border-cyan-500/30", label: `${Math.round(score)}%` };
  if (score >= 55) return { color: "text-amber-300 bg-amber-950/60 border-amber-500/30", label: `${Math.round(score)}%` };
  return { color: "text-rose-300 bg-rose-950/60 border-rose-500/30", label: `${Math.round(score)}%` };
}

function getStatusBadge(status: string) {
  const statusMap: Record<string, { label: string; cls: string }> = {
    completed: { label: "Completed", cls: "bg-emerald-950/60 text-emerald-300 border-emerald-500/30" },
    waiting_for_approval: { label: "Review Required", cls: "bg-cyan-950/60 text-cyan-300 border-cyan-500/30" },
    failed: { label: "Failed", cls: "bg-rose-950/60 text-rose-300 border-rose-500/30" },
    queued: { label: "Queued", cls: "bg-slate-900 text-slate-400 border-slate-700" },
  };
  const fallback = { label: status.replace(/_/g, " "), cls: "bg-indigo-950/60 text-indigo-300 border-indigo-500/30" };
  const { label, cls } = statusMap[status] || fallback;
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider border ${cls}`}>
      {label}
    </span>
  );
}

export default function HistoryPage() {
  const router = useRouter();
  const [analyses, setAnalyses] = useState<AnalysisItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.replace("/login");
      return;
    }
    loadAnalyses();
  }, [router]);

  async function loadAnalyses() {
    try {
      const data = await api.listAnalyses();
      setAnalyses(Array.isArray(data) ? data : []);
    } catch {
      setAnalyses([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this analysis session?")) return;
    try {
      await api.deleteAnalysis(id);
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete analysis");
    }
  }

  const filteredAnalyses = analyses.filter((a) => {
    const matchesFilter = filter === "all" || a.status === filter;
    const matchesSearch =
      !searchQuery ||
      (a.job_title || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (a.company || "").toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const stats = {
    total: analyses.length,
    completed: analyses.filter((a) => a.status === "completed").length,
    avgJobMatch:
      analyses.filter((a) => a.job_match_score).length > 0
        ? Math.round(
            analyses
              .filter((a) => a.job_match_score)
              .reduce((sum, a) => sum + (a.job_match_score || 0), 0) /
              analyses.filter((a) => a.job_match_score).length
          )
        : 0,
    bestScore: Math.max(0, ...analyses.map((a) => a.job_match_score || 0)),
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950 relative overflow-x-hidden">
      {/* Background Backlights */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/3 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold tracking-wider uppercase mb-3 shadow-inner">
              <History className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              Audit Repository
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Analysis History & Archives
            </h1>
            <p className="mt-1 text-sm text-slate-300 font-normal">
              Review, filter, and compare all historical CV audits, triage runs, and benchmarked scores.
            </p>
          </div>

          <div className="flex-shrink-0">
            <SpecularButton
              size="md"
              radius={14}
              tint="#ffffff"
              tintOpacity={0.95}
              textColor="#020617"
              lineColor="#ffffff"
              baseColor="#e2e8f0"
              intensity={1.2}
              shineSize={14}
              shineFade={45}
              thickness={1.3}
              onClick={() => router.push("/analyze")}
              className="shadow-xl shadow-cyan-500/10"
            >
              <span className="font-bold flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-600" />
                Launch New Audit
              </span>
            </SpecularButton>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          {[
            { label: "Total Audits", value: stats.total, icon: BarChart3, color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20" },
            { label: "Completed Runs", value: stats.completed, icon: CheckCircle2, color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
            { label: "Avg Job Match", value: stats.avgJobMatch ? `${stats.avgJobMatch}%` : "—", icon: Target, color: "text-purple-400 bg-purple-500/10 border-purple-500/20" },
            { label: "Peak Score", value: stats.bestScore ? `${Math.round(stats.bestScore)}%` : "—", icon: Trophy, color: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
          ].map((s, i) => {
            const Icon = s.icon;
            return (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-2xl p-5 shadow-xl shadow-slate-950/40"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{s.label}</span>
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center border ${s.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-white tracking-tight font-sans">
                  {s.value}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Filters & Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
            {["all", "completed", "waiting_for_approval", "failed"].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all flex-shrink-0 ${
                  filter === f
                    ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-inner"
                    : "text-slate-400 hover:text-white bg-slate-900/60 border border-slate-800 hover:border-slate-700"
                }`}
              >
                {f === "all" ? "All Sessions" : f.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
              </button>
            ))}
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              type="text"
              placeholder="Search by job title or company..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950/80 border border-slate-700/80 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 rounded-full pl-10 pr-4 py-2 text-xs sm:text-sm text-white placeholder-slate-400 focus:outline-none transition-all"
            />
          </div>
        </div>

        {/* Results List */}
        {loading ? (
          <div className="space-y-3.5">
            {[1, 2, 3].map((i) => (
              <div key={i} className="backdrop-blur-xl bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 h-28 animate-pulse" />
            ))}
          </div>
        ) : filteredAnalyses.length === 0 ? (
          <div className="backdrop-blur-2xl bg-slate-900/70 border border-slate-800 rounded-3xl p-12 text-center max-w-lg mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-slate-800/80 border border-slate-700 text-slate-400 flex items-center justify-center mx-auto mb-4">
              <Layers className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white">
              {analyses.length === 0 ? "No Analyses Yet" : "No Matching Audits Found"}
            </h3>
            <p className="mt-2 text-xs sm:text-sm text-slate-300">
              {analyses.length === 0
                ? "Start your first CV audit to unlock comprehensive tri-scoring and actionable recommendations."
                : "Try adjusting your search criteria or switching filter tabs."}
            </p>
            {analyses.length === 0 && (
              <div className="mt-6 flex justify-center">
                <SpecularButton
                  size="md"
                  radius={14}
                  tint="#ffffff"
                  tintOpacity={0.95}
                  textColor="#020617"
                  lineColor="#ffffff"
                  baseColor="#e2e8f0"
                  intensity={1.2}
                  shineSize={14}
                  shineFade={45}
                  thickness={1.3}
                  onClick={() => router.push("/analyze")}
                >
                  <span className="font-bold">Start First Analysis</span>
                </SpecularButton>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-3.5">
            {filteredAnalyses.map((a, i) => {
              const matchBadge = getScoreBadge(a.job_match_score);
              const atsBadge = getScoreBadge(a.ats_score);
              const qualityBadge = getScoreBadge(a.quality_score);

              return (
                <motion.div
                  key={a.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => router.push(`/analysis/${a.id}`)}
                  className="group relative backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-600 rounded-2xl p-5 sm:p-6 shadow-lg shadow-slate-950/40 hover:shadow-2xl transition-all cursor-pointer"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    {/* Left: Role and Metadata */}
                    <div className="flex items-start gap-4">
                      <div className="w-11 h-11 rounded-xl bg-slate-800/90 border border-slate-700/80 flex items-center justify-center flex-shrink-0 group-hover:border-cyan-500/50 group-hover:bg-cyan-950/30 transition-colors">
                        <Briefcase className="w-5 h-5 text-cyan-400" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <h3 className="font-bold text-base text-white group-hover:text-cyan-300 transition-colors">
                            {a.job_title || "Untitled Analysis"}
                          </h3>
                          {getStatusBadge(a.status)}
                        </div>

                        <div className="flex items-center gap-3 text-xs text-slate-400 mt-1.5 flex-wrap">
                          {a.company && (
                            <span className="font-medium text-slate-300">{a.company}</span>
                          )}
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5 text-slate-400" />
                            {new Date(a.created_at).toLocaleDateString("en-US", {
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                            })}
                          </span>
                          {a.processing_time && (
                            <span className="flex items-center gap-1">
                              <Clock className="w-3.5 h-3.5 text-slate-400" />
                              {Math.round(a.processing_time)}s
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Right: Scores & Actions */}
                    <div className="flex items-center gap-3 sm:gap-4 flex-wrap lg:flex-nowrap justify-between lg:justify-end pt-3 lg:pt-0 border-t lg:border-t-0 border-slate-800/80">
                      {a.job_match_score != null && (
                        <div className="text-center px-3 py-1.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                          <p className={`text-sm font-extrabold font-mono ${matchBadge.color.split(" ")[0]}`}>
                            {matchBadge.label}
                          </p>
                          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Match</p>
                        </div>
                      )}

                      {a.ats_score != null && (
                        <div className="text-center px-3 py-1.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                          <p className={`text-sm font-extrabold font-mono ${atsBadge.color.split(" ")[0]}`}>
                            {atsBadge.label}
                          </p>
                          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">ATS</p>
                        </div>
                      )}

                      {a.quality_score != null && (
                        <div className="text-center px-3 py-1.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                          <p className={`text-sm font-extrabold font-mono ${qualityBadge.color.split(" ")[0]}`}>
                            {qualityBadge.label}
                          </p>
                          <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Quality</p>
                        </div>
                      )}

                      <button
                        onClick={(e) => handleDelete(a.id, e)}
                        title="Delete Analysis"
                        className="p-2.5 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/30 transition-colors ml-1"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>

                      <div className="w-8 h-8 rounded-full bg-slate-800/80 group-hover:bg-cyan-500 text-slate-400 group-hover:text-slate-950 flex items-center justify-center transition-all">
                        <ArrowUpRight className="w-4 h-4" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
