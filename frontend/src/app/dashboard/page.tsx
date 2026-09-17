"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  BarChart3,
  Target,
  FileCheck,
  Layers,
  Plus,
  Trash2,
  ChevronRight,
  Sparkles,
  Calendar,
  Clock,
  Briefcase,
  ArrowUpRight,
} from "lucide-react";
import api from "@/lib/api";
import { Navbar } from "@/components/ui/Navbar";
import SpecularButton from "@/components/ui/SpecularButton";

export default function DashboardPage() {
  const router = useRouter();
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.replace("/login");
      return;
    }
    loadData();
  }, [router]);

  async function loadData() {
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
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this analysis session?")) return;
    try {
      await api.deleteAnalysis(id);
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch (err: any) {
      alert(err.message || "Failed to delete analysis");
    }
  }

  function getScoreBadge(score: number | null) {
    if (score == null) return { color: "text-slate-400 bg-slate-900 border-slate-800", label: "N/A" };
    if (score >= 85) return { color: "text-emerald-300 bg-emerald-950/60 border-emerald-500/30", label: `${Math.round(score)}%` };
    if (score >= 70) return { color: "text-cyan-300 bg-cyan-950/60 border-cyan-500/30", label: `${Math.round(score)}%` };
    if (score >= 55) return { color: "text-amber-300 bg-amber-950/60 border-amber-500/30", label: `${Math.round(score)}%` };
    return { color: "text-rose-300 bg-rose-950/60 border-rose-500/30", label: `${Math.round(score)}%` };
  }

  const bestMatch =
    analyses.length > 0 && analyses.some((a) => a?.job_match_score != null)
      ? Math.max(...analyses.map((a) => a?.job_match_score || 0))
      : null;

  const validAtsScores = analyses.filter((a) => a?.ats_score != null);
  const avgAts =
    validAtsScores.length > 0
      ? Math.round(validAtsScores.reduce((s, a) => s + (a.ats_score || 0), 0) / validAtsScores.length)
      : null;

  const uniqueDocs =
    analyses.length > 0
      ? new Set(analyses.map((a) => a?.document_id).filter(Boolean)).size
      : 0;

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950 relative overflow-x-hidden">
      {/* Dynamic Ambient Backlight */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        {/* Header Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold tracking-wider uppercase mb-3 shadow-inner">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              Intelligence Command Center
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Executive Dashboard
            </h1>
            <p className="mt-1 text-sm text-slate-300 font-normal">
              Manage resume audits, match heuristics, and ATS scoring benchmarks.
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
                <Plus className="w-4 h-4" />
                New CV Audit
              </span>
            </SpecularButton>
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5 mb-12">
          {[
            {
              label: "Total Analyses",
              value: analyses.length,
              sub: "Executed audit runs",
              icon: BarChart3,
              glow: "from-cyan-500/20 to-blue-500/10",
              border: "border-cyan-500/20",
              iconBg: "bg-cyan-500/10 text-cyan-300",
            },
            {
              label: "Peak Job Match",
              value: bestMatch != null ? `${Math.round(bestMatch)}%` : "–",
              sub: "Highest role congruence",
              icon: Target,
              glow: "from-emerald-500/20 to-teal-500/10",
              border: "border-emerald-500/20",
              iconBg: "bg-emerald-500/10 text-emerald-300",
            },
            {
              label: "Average ATS Score",
              value: avgAts != null ? `${avgAts}%` : "–",
              sub: "Across all vacancies",
              icon: FileCheck,
              glow: "from-purple-500/20 to-indigo-500/10",
              border: "border-purple-500/20",
              iconBg: "bg-purple-500/10 text-purple-300",
            },
            {
              label: "Unique CVs Indexed",
              value: uniqueDocs,
              sub: "Parsed source files",
              icon: Layers,
              glow: "from-amber-500/20 to-orange-500/10",
              border: "border-amber-500/20",
              iconBg: "bg-amber-500/10 text-amber-300",
            },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className={`relative group rounded-2xl p-5 backdrop-blur-2xl bg-slate-900/80 border ${stat.border} shadow-xl shadow-slate-950/40 hover:border-slate-600 transition-all`}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    {stat.label}
                  </span>
                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${stat.iconBg} shadow-inner`}>
                    <Icon className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-3xl font-extrabold text-white tracking-tight">
                  {stat.value}
                </div>
                <p className="text-xs text-slate-400 mt-1 font-medium">{stat.sub}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Recent Analyses Section */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              Recent Audits
              <span className="px-2 py-0.5 rounded-full bg-slate-800 text-xs font-mono font-bold text-slate-300">
                {analyses.length}
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Click any report to view deep recommendations and live visual diffs</p>
          </div>

          <Link
            href="/history"
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors group"
          >
            <span>View Full Archive</span>
            <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>

        {loading ? (
          <div className="space-y-3.5">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="backdrop-blur-xl bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 h-28 animate-pulse"
              />
            ))}
          </div>
        ) : analyses.length > 0 ? (
          <div className="space-y-3.5">
            {analyses.map((analysis, i) => {
              const matchBadge = getScoreBadge(analysis.job_match_score);
              const atsBadge = getScoreBadge(analysis.ats_score);
              const qualityBadge = getScoreBadge(analysis.quality_score);

              return (
                <motion.div
                  key={analysis.id || i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.05 }}
                >
                  <Link
                    href={`/analysis/${analysis.id}`}
                    className="group relative block backdrop-blur-2xl bg-slate-900/75 border border-slate-800/90 hover:border-slate-600/90 rounded-2xl p-5 sm:p-6 shadow-lg shadow-slate-950/40 hover:shadow-2xl transition-all"
                  >
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                      {/* Left: Role Info */}
                      <div className="flex items-start gap-4">
                        <div className="w-11 h-11 rounded-xl bg-slate-800/90 border border-slate-700/80 flex items-center justify-center flex-shrink-0 group-hover:border-cyan-500/50 group-hover:bg-cyan-950/30 transition-colors">
                          <Briefcase className="w-5 h-5 text-cyan-400" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2.5 flex-wrap">
                            <h3 className="font-bold text-base text-white group-hover:text-cyan-300 transition-colors">
                              {analysis.job_title || "Target Role Analysis"}
                            </h3>
                            {analysis.status && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-slate-300 border border-slate-700">
                                {analysis.status.replace(/_/g, " ")}
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-3 text-xs text-slate-400 mt-1.5 flex-wrap">
                            {analysis.company && (
                              <span className="font-medium text-slate-300">{analysis.company}</span>
                            )}
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3.5 h-3.5 text-slate-400" />
                              {analysis.created_at
                                ? new Date(analysis.created_at).toLocaleDateString("en-US", {
                                    month: "short",
                                    day: "numeric",
                                    year: "numeric",
                                  })
                                : "Recently"}
                            </span>
                            {typeof analysis.processing_time === "number" && (
                              <span className="flex items-center gap-1">
                                <Clock className="w-3.5 h-3.5 text-slate-400" />
                                {analysis.processing_time.toFixed(1)}s
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Right: Scores & Actions */}
                      <div className="flex items-center gap-3 sm:gap-4 flex-wrap lg:flex-nowrap justify-between lg:justify-end pt-3 lg:pt-0 border-t lg:border-t-0 border-slate-800/80">
                        {analysis.job_match_score != null && (
                          <div className="text-center px-3 py-1.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                            <p className={`text-sm font-extrabold font-mono ${matchBadge.color.split(" ")[0]}`}>
                              {matchBadge.label}
                            </p>
                            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Match</p>
                          </div>
                        )}

                        {analysis.ats_score != null && (
                          <div className="text-center px-3 py-1.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                            <p className={`text-sm font-extrabold font-mono ${atsBadge.color.split(" ")[0]}`}>
                              {atsBadge.label}
                            </p>
                            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">ATS</p>
                          </div>
                        )}

                        {analysis.quality_score != null && (
                          <div className="text-center px-3 py-1.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                            <p className={`text-sm font-extrabold font-mono ${qualityBadge.color.split(" ")[0]}`}>
                              {qualityBadge.label}
                            </p>
                            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Quality</p>
                          </div>
                        )}

                        <button
                          onClick={(e) => handleDelete(analysis.id, e)}
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
                  </Link>
                </motion.div>
              );
            })}
          </div>
        ) : (
          <div className="backdrop-blur-2xl bg-slate-900/70 border border-slate-800 rounded-3xl p-12 text-center max-w-lg mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-500/10">
              <Sparkles className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-white">No CV Audits Yet</h3>
            <p className="mt-2 text-sm text-slate-300">
              Upload your resume and paste a target job description to generate deterministic ATS scoring and instant rewrites.
            </p>
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
          </div>
        )}
      </main>
    </div>
  );
}
