"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Layers,
  FileText,
  Plus,
  Trash2,
  Sparkles,
  Trophy,
  Target,
  CheckCircle2,
  XCircle,
  Zap,
  ArrowRight,
  Briefcase,
  AlertCircle,
  FileUp,
} from "lucide-react";
import api from "@/lib/api";
import { Navbar } from "@/components/ui/Navbar";
import SpecularButton from "@/components/ui/SpecularButton";

interface JDCardInput {
  id: string;
  title: string;
  company: string;
  text: string;
}

export default function MultiJDAnalysisPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [documents, setDocuments] = useState<any[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");

  const [jds, setJds] = useState<JDCardInput[]>([
    {
      id: "1",
      title: "Senior Backend Engineer",
      company: "Stripe",
      text: "We are looking for a Senior Backend Engineer proficient in Python, FastAPI, Docker, and PostgreSQL. Experience building distributed microservices, REST APIs, and event-driven architectures with Kafka is required.",
    },
    {
      id: "2",
      title: "Full Stack Engineer",
      company: "Linear",
      text: "Seeking a Full Stack Engineer with strong TypeScript, Next.js, and Node.js skills. Must have experience with PostgreSQL, GraphQL, Docker, and building delightful user experiences.",
    },
    {
      id: "3",
      title: "Cloud Platform / DevOps Engineer",
      company: "Vercel",
      text: "Looking for an engineer experienced in Kubernetes, AWS, Terraform, CI/CD pipelines, Docker, Linux systems, and observability with Prometheus/Grafana.",
    },
  ]);

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.replace("/login");
      return;
    }
    loadUserDocs();
  }, [router]);

  async function loadUserDocs() {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
      if (docs.length > 0) {
        setSelectedDocId(docs[0].id);
      }
    } catch {
      // ignore
    } finally {
      setLoadingDocs(false);
    }
  }

  function handleAddJD() {
    if (jds.length >= 5) {
      alert("You can compare up to 5 job descriptions simultaneously.");
      return;
    }
    setJds([
      ...jds,
      {
        id: Date.now().toString(),
        title: `Job Target ${jds.length + 1}`,
        company: "Target Company",
        text: "",
      },
    ]);
  }

  function handleRemoveJD(idToRemove: string) {
    if (jds.length <= 2) {
      alert("Multi-JD comparison requires at least 2 job descriptions.");
      return;
    }
    setJds(jds.filter((j) => j.id !== idToRemove));
  }

  function handleUpdateJD(id: string, field: keyof JDCardInput, value: string) {
    setJds(jds.map((j) => (j.id === id ? { ...j, [field]: value } : j)));
  }

  async function handleRunComparison(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    for (const jd of jds) {
      if (!jd.title.trim() || jd.text.trim().length < 30) {
        setError(
          `Please provide a title and at least 30 characters of text for "${jd.title || 'each job'}"`
        );
        return;
      }
    }

    setAnalyzing(true);
    try {
      let docId = selectedDocId;

      if (file) {
        const uploadRes = await api.uploadDocument(file);
        docId = uploadRes.document_id || uploadRes.id;
      }

      if (!docId) {
        setError("Please upload or select an existing CV document to compare.");
        setAnalyzing(false);
        return;
      }

      const res = await api.createMultiJDAnalysis({
        document_id: docId,
        job_descriptions: jds.map((j) => ({
          title: j.title,
          company: j.company,
          text: j.text,
        })),
      });

      setResults(res);
    } catch (err: any) {
      setError(err.message || "Failed to compare multiple job descriptions.");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950 relative overflow-x-hidden">
      {/* Background Glows */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10 space-y-10">
        {/* Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/60 border border-amber-500/30 text-amber-300 text-xs font-semibold tracking-wider uppercase mb-3 shadow-inner">
            <Layers className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            Simultaneous Market Alignment
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Multi-JD Comparison & Fit Ranker
          </h1>
          <p className="mt-2 text-sm text-slate-300 font-normal">
            Benchmark one CV across 2 to 5 opportunities in parallel. Pinpoint your highest-yield vacancy and uncover market-wide skill overlaps.
          </p>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2.5 bg-red-500/10 border border-red-500/30 rounded-2xl p-4 text-red-200 text-xs sm:text-sm"
          >
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <span>{error}</span>
          </motion.div>
        )}

        {/* Input Form */}
        <form onSubmit={handleRunComparison} className="space-y-8">
          {/* 1. CV Selection Card */}
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 sm:p-7 shadow-xl shadow-slate-950/40">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
                <FileUp className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Candidate Resume Selection
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Existing documents */}
              {documents.length > 0 && (
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Use Stored Document
                  </label>
                  <select
                    value={selectedDocId}
                    onChange={(e) => {
                      setSelectedDocId(e.target.value);
                      setFile(null);
                    }}
                    className="w-full bg-slate-950/70 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white focus:outline-none focus:border-cyan-400"
                  >
                    {documents.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.filename || d.original_filename || "Candidate CV"} ({new Date(d.created_at).toLocaleDateString()})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Upload new file */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Or Upload New Resume (PDF / DOCX)
                </label>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".pdf,.docx"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setFile(e.target.files[0]);
                      setSelectedDocId("");
                    }
                  }}
                  className="w-full text-xs text-slate-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-white hover:file:bg-slate-700 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* 2. Job Descriptions Grid */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-amber-400" />
                <h3 className="text-base font-bold text-white tracking-tight">
                  Target Vacancies ({jds.length} of 5 max)
                </h3>
              </div>
              {jds.length < 5 && (
                <button
                  type="button"
                  onClick={handleAddJD}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 text-amber-300 text-xs font-semibold transition-all shadow-sm"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Target Role</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {jds.map((jd, idx) => (
                <div
                  key={jd.id}
                  className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 rounded-2xl p-5 shadow-xl shadow-slate-950/40 flex flex-col justify-between space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-950/60 border border-amber-500/30 text-amber-400 text-[10px] font-mono font-bold uppercase">
                      Target 0{idx + 1}
                    </span>
                    {jds.length > 2 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveJD(jd.id)}
                        className="p-1 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                        title="Remove role"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  <div className="space-y-2">
                    <input
                      type="text"
                      value={jd.title}
                      onChange={(e) => handleUpdateJD(jd.id, "title", e.target.value)}
                      placeholder="Job Title (e.g. Senior Backend Engineer)"
                      className="w-full bg-slate-950/70 border border-slate-800 focus:border-amber-400 rounded-xl px-3 py-2 text-xs font-bold text-white focus:outline-none"
                    />
                    <input
                      type="text"
                      value={jd.company}
                      onChange={(e) => handleUpdateJD(jd.id, "company", e.target.value)}
                      placeholder="Company (e.g. Stripe)"
                      className="w-full bg-slate-950/70 border border-slate-800 focus:border-amber-400 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none"
                    />
                  </div>

                  <textarea
                    rows={6}
                    value={jd.text}
                    onChange={(e) => handleUpdateJD(jd.id, "text", e.target.value)}
                    placeholder="Paste job description requirements, responsibilities, and qualifications..."
                    className="w-full bg-slate-950/70 border border-slate-800 focus:border-amber-400 rounded-xl p-3 text-xs text-slate-300 leading-relaxed focus:outline-none resize-none"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Action Trigger */}
          <div className="text-center pt-2">
            <SpecularButton
              type="submit"
              size="lg"
              radius={16}
              tint="#ffffff"
              tintOpacity={0.96}
              textColor="#020617"
              lineColor="#ffffff"
              baseColor="#e2e8f0"
              intensity={1.25}
              shineSize={16}
              shineFade={45}
              thickness={1.4}
              disabled={analyzing}
              className="shadow-2xl shadow-amber-500/15"
            >
              <span className="font-extrabold text-sm sm:text-base flex items-center gap-2 px-4 py-1">
                {analyzing ? (
                  <>
                    <Zap className="w-4 h-4 animate-spin text-amber-500" />
                    Computing Cross-Role Heuristics...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4 text-amber-500" />
                    Benchmark Across All {jds.length} Vacancies
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </>
                )}
              </span>
            </SpecularButton>
          </div>
        </form>

        {/* ── RESULTS SECTION ── */}
        {results && (
          <div className="space-y-8 pt-8 border-t border-slate-800/80">
            {/* 1. Best Fit Hero Card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative backdrop-blur-2xl bg-gradient-to-br from-emerald-950/40 via-slate-900 to-slate-950 border border-emerald-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 relative z-10">
                <div>
                  <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs font-mono font-bold uppercase mb-3">
                    <Trophy className="w-3.5 h-3.5 text-amber-400" />
                    Top Market Match (#1 Ranked)
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                    {results.best_fit?.job_title}
                  </h2>
                  <p className="text-xs text-slate-400 font-semibold mt-0.5">
                    Target Enterprise: {results.best_fit?.company}
                  </p>
                  <p className="text-xs sm:text-sm text-slate-300 mt-3 max-w-2xl leading-relaxed font-normal">
                    {results.best_fit?.explanation}
                  </p>
                </div>

                <div className="text-center sm:text-right shrink-0 bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl">
                  <span className="text-[10px] font-mono font-bold uppercase text-slate-400 block tracking-wider">
                    Role Congruence
                  </span>
                  <div className="text-4xl font-extrabold text-emerald-400 font-mono tracking-tight my-1">
                    {Math.round(results.best_fit?.job_match_score)}%
                  </div>
                  <span className="text-xs font-semibold text-cyan-300">
                    ATS {Math.round(results.best_fit?.ats_score)}% Compatibility
                  </span>
                </div>
              </div>
            </motion.div>

            {/* 2. Ranked Job Cards Grid */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <Target className="w-5 h-5 text-cyan-400" />
                Ranked Vacancy Comparison
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {results.ranked_jobs.map((job: any, idx: number) => {
                  const medal = idx === 0 ? "🥇 1st Rank" : idx === 1 ? "🥈 2nd Rank" : "🥉 3rd Rank";
                  return (
                    <motion.div
                      key={job.job_id}
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className={`backdrop-blur-2xl rounded-2xl p-5 border transition-all ${
                        idx === 0
                          ? "border-emerald-500/50 bg-emerald-950/15 shadow-xl shadow-emerald-950/30"
                          : "border-slate-800 bg-slate-900/80"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-[10px] font-mono font-bold text-slate-300 border border-slate-700">
                          {medal}
                        </span>
                        <span className="text-xl font-extrabold text-emerald-400 font-mono">
                          {Math.round(job.job_match_score)}%
                        </span>
                      </div>

                      <h4 className="text-base font-bold text-white">{job.job_title}</h4>
                      <p className="text-xs text-slate-400 mb-3">{job.company}</p>

                      <p className="text-xs text-slate-300 mb-4 leading-relaxed font-normal">{job.summary}</p>

                      {/* Matched Skills */}
                      {job.matched_skills.length > 0 && (
                        <div className="mb-3">
                          <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1.5 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            Covered in CV ({job.matched_skills.length})
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {job.matched_skills.map((s: string, sIdx: number) => (
                              <span
                                key={sIdx}
                                className="px-2 py-0.5 rounded-md text-[11px] bg-emerald-500/15 text-emerald-300 font-mono border border-emerald-500/20"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Missing Gaps */}
                      {job.missing_skills.length > 0 && (
                        <div>
                          <span className="text-[10px] uppercase font-bold text-rose-400 block mb-1.5 flex items-center gap-1">
                            <XCircle className="w-3 h-3" />
                            Missing Skill Gaps ({job.missing_skills.length})
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {job.missing_skills.map((s: string, sIdx: number) => (
                              <span
                                key={sIdx}
                                className="px-2 py-0.5 rounded-md text-[11px] bg-rose-500/15 text-rose-300 font-mono border border-rose-500/20"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* 3. Cross-JD Intelligence Matrix */}
            <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl space-y-6">
              <div>
                <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-indigo-950/60 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-bold uppercase mb-2">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  Synthesized Market Intelligence
                </div>
                <h3 className="text-xl font-bold text-white tracking-tight">
                  Recurring Requirements vs Unique Differentiators
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Common Requirements */}
                <div className="bg-slate-950/60 rounded-2xl p-5 border border-slate-800">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-2 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Shared Across Multiple Roles
                  </h4>
                  <p className="text-xs text-slate-400 mb-4 leading-relaxed">
                    These technologies recurred across vacancies. Ensure they are prominently featured in your Master CV:
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {results.cross_jd_analysis?.common_requirements.length > 0 ? (
                      results.cross_jd_analysis.common_requirements.map((req: string, rIdx: number) => (
                        <span
                          key={rIdx}
                          className="px-2.5 py-1 rounded-lg text-xs bg-emerald-500/15 text-emerald-300 font-mono border border-emerald-500/30"
                        >
                          {req}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">No common skills detected across the selected roles.</span>
                    )}
                  </div>
                </div>

                {/* Unique Differentiators */}
                <div className="bg-slate-950/60 rounded-2xl p-5 border border-slate-800">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2 flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    Role-Specific Nuances
                  </h4>
                  <p className="text-xs text-slate-400 mb-4 leading-relaxed">
                    Skills unique to single positions. Tailor customized versions when submitting applications:
                  </p>
                  <div className="space-y-3">
                    {Object.entries(results.cross_jd_analysis?.unique_requirements || {}).map(
                      ([title, skills]: [string, any], uIdx: number) => (
                        <div key={uIdx} className="text-xs">
                          <span className="font-bold text-white block mb-1">{title}:</span>
                          <div className="flex flex-wrap gap-1">
                            {skills.map((s: string, sIdx: number) => (
                              <span
                                key={sIdx}
                                className="px-2 py-0.5 rounded-md text-[11px] bg-slate-800 text-slate-300 font-mono border border-slate-700"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
