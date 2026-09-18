"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  UploadCloud,
  FileText,
  Sparkles,
  CheckCircle2,
  Trash2,
  AlertCircle,
  Wand2,
  FileUp,
  Cpu,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import api from "@/lib/api";
import { Navbar } from "@/components/ui/Navbar";
import SpecularButton from "@/components/ui/SpecularButton";

const SAMPLE_JDS = [
  {
    title: "Senior Full-Stack Engineer",
    text: `Role: Senior Full-Stack Engineer
Location: Remote / Hybrid
Key Requirements:
- 5+ years of experience with modern TypeScript, React, Next.js, and Node.js.
- Deep expertise with PostgreSQL, Redis, Docker, and RESTful API architecture.
- Demonstrated experience designing scalable web services with automated CI/CD pipelines.
- Strong knowledge of web performance optimization, accessibility, and micro-frontend patterns.`,
  },
  {
    title: "AI Systems Engineer",
    text: `Role: AI / Machine Learning Engineer
Location: San Francisco, CA / Remote
Key Requirements:
- 4+ years building production ML & LLM applications with Python, FastAPI, and PyTorch.
- Experience with retrieval-augmented generation (RAG), vector databases (Pinecone, Qdrant), and prompt engineering.
- Solid background in containerized cloud deployments on AWS / GCP using Kubernetes.
- Excellent understanding of deterministic evaluation, latency reduction, and observability.`,
  },
];

export default function AnalyzePage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.replace("/login");
    }
  }, [router]);

  const [step, setStep] = useState<"input" | "processing" | "error">("input");
  const [jdText, setJdText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState("");
  const [progressPct, setProgressPct] = useState(0);
  const [error, setError] = useState("");

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const ext = droppedFile.name.split(".").pop()?.toLowerCase();
      if (ext === "pdf" || ext === "docx") {
        setFile(droppedFile);
      } else {
        setError("Please upload a valid PDF or DOCX resume.");
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  };

  const startAnalysis = async () => {
    if (!file) {
      setError("Please upload your CV (.pdf or .docx) to analyze.");
      return;
    }
    if (!jdText.trim() || jdText.trim().length < 50) {
      setError("Please provide a detailed Job Description (at least 50 characters).");
      return;
    }

    setStep("processing");
    setError("");
    setProgress("Uploading and parsing CV structure...");
    setProgressPct(12);

    try {
      // Step 1: Upload document
      const uploadResult = await api.uploadDocument(file);
      setProgress("Analyzing Job Description skill taxonomy...");
      setProgressPct(30);

      // Step 2: Create JD
      const jdResult = await api.createJobDescription(jdText.trim());
      setProgress("Running multi-agent deterministic heuristics...");
      setProgressPct(55);

      // Step 3: Start analysis
      const analysisResult = await api.createAnalysis(
        uploadResult.document_id,
        jdResult.id
      );

      setProgress("Synthesizing tri-scores & actionable rewrites...");
      setProgressPct(90);

      setTimeout(() => {
        router.push(`/analysis/${analysisResult.analysis_id}`);
      }, 500);
    } catch (err: any) {
      setStep("error");
      setError(err.message || "Analysis execution failed. Please try again.");
    }
  };

  if (step === "processing") {
    return (
      <div className="min-h-screen bg-slate-950 text-white font-sans flex items-center justify-center p-6 relative overflow-hidden">
        {/* Dynamic Backlights */}
        <div className="absolute top-1/3 left-1/3 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/3 right-1/3 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full backdrop-blur-2xl bg-slate-900/85 border border-slate-800 rounded-3xl p-8 sm:p-10 shadow-2xl shadow-indigo-950/50 text-center relative z-10"
        >
          {/* Dual spinning halo */}
          <div className="relative w-28 h-28 mx-auto mb-8">
            <div className="absolute inset-0 rounded-full border-2 border-slate-800" />
            <div
              className="absolute inset-0 rounded-full border-2 border-transparent border-t-cyan-400 border-r-indigo-500 animate-spin"
              style={{ animationDuration: "1.2s" }}
            />
            <div
              className="absolute inset-3 rounded-full border-2 border-transparent border-t-fuchsia-400 border-b-cyan-400 animate-spin"
              style={{ animationDuration: "1.8s", animationDirection: "reverse" }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 rounded-2xl bg-slate-950/80 border border-slate-700/80 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Cpu className="w-6 h-6 text-cyan-400 animate-pulse" />
              </div>
            </div>
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-[11px] font-semibold tracking-wider uppercase mb-3">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            Neural Audit Pipeline
          </div>

          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            Auditing Your CV
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 mb-6 font-medium">
            {progress}
          </p>

          {/* Progress bar */}
          <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden mb-2 border border-slate-800/80 p-0.5">
            <motion.div
              className="h-full bg-gradient-to-r from-cyan-400 via-indigo-500 to-fuchsia-500 rounded-full shadow-lg shadow-cyan-500/50"
              initial={{ width: "0%" }}
              animate={{ width: `${progressPct}%` }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
            />
          </div>
          <p className="text-xs font-mono font-bold text-cyan-400 mb-6">{progressPct}%</p>

          {/* Stage indicators */}
          <div className="space-y-2.5 text-left border-t border-slate-800/80 pt-5">
            {[
              { name: "Document structural parsing", threshold: 15 },
              { name: "Job description skill taxonomy", threshold: 30 },
              { name: "Semantic requirement matching", threshold: 50 },
              { name: "Tri-scoring computation", threshold: 75 },
              { name: "Synthesizing ATS rewrites", threshold: 90 },
            ].map((stage) => {
              const isDone = progressPct >= stage.threshold;
              const isCurrent = progressPct < stage.threshold && progressPct >= stage.threshold - 20;

              return (
                <div key={stage.name} className="flex items-center gap-2.5 text-xs">
                  <div className="w-4 h-4 flex items-center justify-center flex-shrink-0">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : isCurrent ? (
                      <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    ) : (
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
                    )}
                  </div>
                  <span
                    className={
                      isDone
                        ? "text-emerald-300 font-medium"
                        : isCurrent
                        ? "text-cyan-200 font-semibold"
                        : "text-slate-500"
                    }
                  >
                    {stage.name}
                  </span>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950 relative overflow-x-hidden">
      {/* Dynamic Ambient Background */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/3 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <div className="inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold tracking-wider uppercase mb-3 shadow-inner">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            Deterministic CV Intelligence
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Launch New Resume Audit
          </h1>
          <p className="mt-2 text-sm sm:text-base text-slate-300 font-normal">
            Pair your CV with a target vacancy to calculate ATS parse confidence, keyword coverage, and automated bullet optimizations.
          </p>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 max-w-3xl mx-auto flex items-center justify-between bg-red-500/10 border border-red-500/30 rounded-2xl p-4 text-red-200 text-xs sm:text-sm"
          >
            <div className="flex items-center gap-2.5">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => {
                setError("");
                setStep("input");
              }}
              className="text-xs font-bold text-red-300 underline hover:text-white"
            >
              Reset
            </button>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 items-stretch">
          {/* ── Left Column: Job Description ── */}
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 sm:p-7 shadow-xl shadow-slate-950/40 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-white tracking-tight">
                      Target Job Description
                    </h2>
                    <p className="text-[11px] text-slate-400">Role specifications & qualifications</p>
                  </div>
                </div>

                {/* Sample JD loader dropdown / button */}
                <div className="flex items-center gap-1.5">
                  <button
                    type="button"
                    onClick={() => setJdText(SAMPLE_JDS[0].text)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-[11px] font-medium border border-slate-700 transition-colors"
                    title="Load sample Full Stack JD"
                  >
                    <Wand2 className="w-3 h-3 text-cyan-400" />
                    <span>Sample JD</span>
                  </button>
                </div>
              </div>

              <div className="relative">
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste the target job description here...&#10;&#10;Include requirements, responsibilities, technical stacks, qualifications, and preferred certifications."
                  className="w-full h-80 bg-slate-950/70 border border-slate-700/80 focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 rounded-2xl p-4 text-xs sm:text-sm text-white placeholder-slate-400 resize-none font-sans leading-relaxed transition-all"
                />
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between text-xs">
              <span className="text-slate-400 font-mono">
                {jdText.length.toLocaleString()} / 15,000 chars
              </span>
              {jdText.length >= 50 ? (
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  JD Ready
                </span>
              ) : (
                <span className="text-slate-400">Min 50 characters required</span>
              )}
            </div>
          </div>

          {/* ── Right Column: CV Upload ── */}
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 sm:p-7 shadow-xl shadow-slate-950/40 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
                  <FileUp className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-white tracking-tight">
                    Candidate Resume / CV
                  </h2>
                  <p className="text-[11px] text-slate-400">PDF or DOCX document</p>
                </div>
              </div>

              <div
                className={`relative rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center h-80 ${
                  isDragging
                    ? "border-cyan-400 bg-cyan-950/30 scale-[0.99]"
                    : file
                    ? "border-emerald-500/50 bg-emerald-950/20"
                    : "border-slate-700 hover:border-slate-500 bg-slate-950/50 hover:bg-slate-950/80"
                }`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                />

                {file ? (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                      <CheckCircle2 className="w-8 h-8" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white tracking-tight max-w-xs truncate">
                        {file.name}
                      </p>
                      <p className="text-xs text-slate-400 mt-1 font-mono">
                        {(file.size / 1024).toFixed(1)} KB • Ready for AST Parse
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setFile(null);
                      }}
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold transition-colors mt-2"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Remove Document</span>
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 rounded-2xl bg-slate-800/80 border border-slate-700/80 text-cyan-400 flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                      <UploadCloud className="w-8 h-8" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-white">
                        Drag & drop your CV here, or browse
                      </p>
                      <p className="text-xs text-slate-400 mt-1 font-medium">
                        Supports PDF and DOCX up to 10 MB
                      </p>
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[10px] font-mono font-bold text-slate-300 border border-slate-700">
                        PDF
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-[10px] font-mono font-bold text-slate-300 border border-slate-700">
                        DOCX
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                Zero external telemetry
              </span>
              <span>Local AST Tokenizer</span>
            </div>
          </div>
        </div>

        {/* Action Button Banner */}
        <div className="mt-10 text-center">
          <div className="inline-block">
            <SpecularButton
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
              disabled={jdText.length < 50 || !file}
              onClick={startAnalysis}
              className="shadow-2xl shadow-cyan-500/20 cursor-pointer"
            >
              <span className="font-extrabold text-base flex items-center gap-2 px-4 py-1">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                Execute Deterministic Audit
                <ArrowRight className="w-4 h-4 ml-1" />
              </span>
            </SpecularButton>
          </div>
          <p className="mt-3 text-xs text-slate-400">
            Automated tri-scoring and bullet optimizations typically compute in &lt; 4 seconds.
          </p>
        </div>
      </main>
    </div>
  );
}
