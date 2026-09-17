"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  DownloadCloud,
  FileText,
  ShieldCheck,
  Palette,
  CheckCircle2,
  ArrowLeft,
  Sparkles,
  Layers,
  Lock,
  FileCode,
  Check,
} from "lucide-react";
import api from "@/lib/api";
import { Navbar } from "@/components/ui/Navbar";
import SpecularButton from "@/components/ui/SpecularButton";

export default function ExportPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [loading, setLoading] = useState(true);
  const [downloadingFormat, setDownloadingFormat] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [version, setVersion] = useState<any>(null);
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState("ats_classic");
  const [error, setError] = useState("");

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.replace("/login");
      return;
    }
    loadExportData();
  }, [id, router]);

  async function loadExportData() {
    try {
      const tmpls = await api.getExportTemplates();
      setTemplates(tmpls);

      try {
        const analysisData = await api.getAnalysis(id);
        setAnalysis(analysisData);

        if (analysisData.latest_version_id) {
          const versionData = await api.getCVVersion(analysisData.latest_version_id);
          setVersion(versionData);
        }
      } catch {
        const versionData = await api.getCVVersion(id);
        setVersion(versionData);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load export details");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownload(format: "pdf" | "docx") {
    setDownloadingFormat(format);
    try {
      const targetVersionId = version?.id || analysis?.latest_version_id || id;
      await api.downloadExport(targetVersionId, format, selectedTemplate);
    } catch (err: any) {
      alert(err.message || `Failed to download ${format.toUpperCase()}`);
    } finally {
      setDownloadingFormat(null);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-slate-400 font-medium">Preparing export engine and ATS renderer...</p>
        </div>
      </div>
    );
  }

  if (error && !analysis && !version) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 text-white font-sans">
        <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-8 text-center max-w-md">
          <ShieldCheck className="w-12 h-12 text-rose-400 mx-auto mb-3" />
          <h2 className="text-xl font-bold text-white">Export Unavailable</h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-300">{error}</p>
          <button
            onClick={() => router.push("/dashboard")}
            className="mt-6 bg-cyan-500 text-slate-950 px-6 py-2.5 rounded-full font-bold text-xs hover:bg-cyan-400 transition-colors"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const cv = version?.parsed_cv || analysis?.document?.parsed_cv || {};
  const scores = version?.job_match_score ? {
    job_match: version.job_match_score,
    ats: version.ats_score,
    quality: version.quality_score,
  } : {
    job_match: analysis?.scores?.job_match_score || 0,
    ats: analysis?.scores?.ats_score || 0,
    quality: analysis?.scores?.quality_score || 0,
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950 relative overflow-x-hidden">
      {/* Background Glows */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-bold uppercase shadow-inner">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                Verified Recruiter Delivery
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Export & Delivery Center
            </h1>
            <p className="mt-1 text-xs sm:text-sm text-slate-300 font-normal">
              Download clean, ATS-compliant PDF and DOCX documents with verified facts and typography.
            </p>
          </div>

          {analysis && (
            <Link
              href={`/analysis/${analysis.id}`}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full backdrop-blur-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-semibold text-slate-300 hover:text-white border border-slate-700 transition-all self-start md:self-auto"
            >
              <ArrowLeft className="w-3.5 h-3.5 text-cyan-400" />
              <span>Back to Analysis</span>
            </Link>
          )}
        </div>

        {/* Pre-Download Quality & Score Audit */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-2xl p-4.5">
            <span className="text-[10px] text-slate-400 uppercase font-mono font-bold tracking-wider">Job Match</span>
            <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-1">
              {Math.round(scores.job_match)}%
            </div>
            <span className="text-[11px] text-slate-400 font-medium">Factually evidenced</span>
          </div>

          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-2xl p-4.5">
            <span className="text-[10px] text-slate-400 uppercase font-mono font-bold tracking-wider">ATS Score</span>
            <div className="text-3xl font-extrabold text-cyan-400 font-mono mt-1">
              {Math.round(scores.ats)}%
            </div>
            <span className="text-[11px] text-slate-400 font-medium">1-Column linear parser</span>
          </div>

          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800 rounded-2xl p-4.5">
            <span className="text-[10px] text-slate-400 uppercase font-mono font-bold tracking-wider">Quality Score</span>
            <div className="text-3xl font-extrabold text-purple-400 font-mono mt-1">
              {Math.round(scores.quality)}%
            </div>
            <span className="text-[11px] text-slate-400 font-medium">Action verbs & metrics</span>
          </div>

          <div className="backdrop-blur-2xl bg-slate-900/80 border border-emerald-500/30 rounded-2xl p-4.5">
            <span className="text-[10px] text-emerald-400 uppercase font-mono font-bold tracking-wider">Security State</span>
            <div className="text-base font-bold text-white flex items-center gap-1.5 mt-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>Certified ATS Safe</span>
            </div>
            <span className="text-[11px] text-slate-400 font-medium">Zero keyword stuffing</span>
          </div>
        </div>

        {/* Main 2-Column Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Template Gallery & Download Triggers (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
                  <Palette className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">
                    Select ATS Theme Template
                  </h3>
                  <p className="text-[11px] text-slate-400">Strict structural typography layouts</p>
                </div>
              </div>

              <div className="space-y-3">
                {templates.map((tmpl) => {
                  const isSelected = selectedTemplate === tmpl.id;
                  return (
                    <div
                      key={tmpl.id}
                      onClick={() => setSelectedTemplate(tmpl.id)}
                      className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                        isSelected
                          ? "bg-slate-800/90 border-cyan-400 shadow-lg shadow-cyan-950/40"
                          : "bg-slate-950/60 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-sm text-white flex items-center gap-2">
                          <span
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: tmpl.primary_color }}
                          />
                          {tmpl.name}
                        </span>
                        <span className="text-[10px] font-mono font-bold text-cyan-300 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-500/30">
                          ATS {tmpl.ats_score}%
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed mb-2 font-normal">{tmpl.description}</p>
                      <span className="text-[11px] text-slate-400 block font-medium">
                        <strong className="text-slate-300">Ideal for:</strong> {tmpl.best_for}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Export Actions Box */}
            <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
                  <DownloadCloud className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">
                    Instant Document Download
                  </h3>
                  <p className="text-[11px] text-slate-400">High-yield standard output</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1">
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
                  disabled={!!downloadingFormat}
                  onClick={() => handleDownload("pdf")}
                  className="shadow-lg shadow-cyan-500/10"
                >
                  <span className="font-bold flex items-center justify-center gap-1.5 text-xs sm:text-sm">
                    {downloadingFormat === "pdf" ? "Exporting..." : "Download PDF"}
                  </span>
                </SpecularButton>

                <button
                  onClick={() => handleDownload("docx")}
                  disabled={!!downloadingFormat}
                  className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-2.5 px-4 rounded-xl border border-slate-700 hover:border-slate-500 transition-all flex items-center justify-center gap-2 text-xs sm:text-sm shadow-md"
                >
                  {downloadingFormat === "docx" ? "Exporting..." : "Download DOCX"}
                </button>
              </div>

              <p className="text-[11px] text-slate-400 text-center pt-2 leading-relaxed">
                🔒 Output certified: single-column linear hierarchy, clean standard unicode, zero floating text frames.
              </p>
            </div>
          </div>

          {/* Right Column: Live Formatted Preview (7 cols) */}
          <div className="lg:col-span-7">
            <div className="backdrop-blur-2xl bg-slate-900/90 border border-slate-800 rounded-3xl p-4 sm:p-7 md:p-9 shadow-2xl space-y-6 text-slate-100">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4 gap-2 flex-wrap">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
                  <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 truncate">
                    Live Formatted Preview ({selectedTemplate.replace(/_/g, " ").toUpperCase()})
                  </span>
                </div>
                <span className="text-[11px] text-slate-400 font-mono shrink-0">Overleaf / LaTeX ATS Format</span>
              </div>

              {/* Candidate Info Header (Centered LaTeX Style) */}
              {(() => {
                const contact = cv.contact || cv.contact_info || {};
                const contactParts = [
                  contact.phone,
                  contact.email,
                  contact.linkedin ? contact.linkedin.replace(/^https?:\/\/(www\.)?/, "") : null,
                  contact.github ? contact.github.replace(/^https?:\/\/(www\.)?/, "") : null,
                  (contact.website || contact.portfolio) ? (contact.website || contact.portfolio).replace(/^https?:\/\/(www\.)?/, "") : null,
                  !contact.linkedin && !contact.github ? contact.location : null,
                ].filter(Boolean);

                return (
                  <div className="text-center space-y-1">
                    <h2 className="text-2xl sm:text-3xl font-extrabold uppercase tracking-wide text-white font-serif break-words">
                      {contact.name || "Candidate Name"}
                    </h2>
                    <p className="text-xs text-slate-300 font-serif break-words">
                      {contactParts.length > 0 ? contactParts.join(" • ") : "Career Profile"}
                    </p>
                  </div>
                );
              })()}

              {/* Professional Summary */}
              {cv.summary && (
                <div className="space-y-1.5 pt-1">
                  <div className="border-b border-slate-700 pb-1">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300 font-serif">
                      Professional Summary
                    </h4>
                  </div>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-serif pt-1 break-words">{cv.summary}</p>
                </div>
              )}

              {/* Work Experience (LaTeX 2x2 Meta Structure) */}
              {cv.experience && cv.experience.length > 0 && (
                <div className="space-y-4 pt-1">
                  <div className="border-b border-slate-700 pb-1">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300 font-serif">
                      Work Experience
                    </h4>
                  </div>
                  <div className="space-y-4 pt-1">
                    {cv.experience.map((exp: any, i: number) => (
                      <div key={i} className="space-y-1 font-serif">
                        <div className="flex flex-col xs:flex-row justify-between items-baseline gap-1 text-xs sm:text-sm">
                          <span className="font-bold text-white break-words">{exp.company || "Company"}</span>
                          <span className="font-bold text-slate-300 font-mono text-[11px] shrink-0">
                            {exp.start_date || ""} {exp.start_date && exp.end_date ? "--" : ""} {exp.end_date || "Present"}
                          </span>
                        </div>
                        <div className="flex flex-col xs:flex-row justify-between items-baseline gap-1 text-xs text-slate-400 italic">
                          <span className="break-words">{exp.job_title || exp.title || "Role"}</span>
                          <span className="shrink-0">{exp.location || "Remote"}</span>
                        </div>

                        {exp.bullets && exp.bullets.length > 0 ? (
                          <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 pt-1">
                            {exp.bullets.map((b: string, bIdx: number) => (
                              <li key={bIdx} className="leading-relaxed break-words">
                                {b}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="text-xs text-slate-300 pt-1 break-words">{exp.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Key Projects (LaTeX Project Layout) */}
              {cv.projects && cv.projects.length > 0 && (
                <div className="space-y-3 pt-1">
                  <div className="border-b border-slate-700 pb-1">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300 font-serif">
                      Projects
                    </h4>
                  </div>
                  <div className="space-y-3 pt-1">
                    {cv.projects.map((proj: any, pIdx: number) => (
                      <div key={pIdx} className="space-y-1 font-serif">
                        <div className="flex justify-between items-baseline text-xs sm:text-sm flex-wrap gap-2">
                          <span className="font-bold text-white break-words">{proj.name}</span>
                          {proj.technologies && proj.technologies.length > 0 && (
                            <span className="text-xs text-slate-400 italic break-words">
                              {proj.technologies.join(" • ")}
                            </span>
                          )}
                        </div>
                        {proj.highlights && proj.highlights.length > 0 ? (
                          <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                            {proj.highlights.map((h: string, hIdx: number) => (
                              <li key={hIdx} className="leading-relaxed break-words">{h}</li>
                            ))}
                          </ul>
                        ) : proj.description ? (
                          <p className="text-xs text-slate-300 leading-relaxed break-words">{proj.description}</p>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Technical Skills (Categorized Overleaf Rows) */}
              {cv.skills && cv.skills.length > 0 && (
                <div className="space-y-2 pt-1 font-serif">
                  <div className="border-b border-slate-700 pb-1">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300">
                      Technical Skills
                    </h4>
                  </div>
                  <div className="space-y-1.5 pt-1 text-xs leading-relaxed text-slate-300">
                    {cv.skill_categories && Object.keys(cv.skill_categories).length > 0 ? (
                      Object.entries(cv.skill_categories).map(([cat, items]: [string, any], idx) => (
                        <p key={idx} className="break-words">
                          <strong className="text-white capitalize">{cat}: </strong>
                          <span>{Array.isArray(items) ? items.join(", ") : String(items)}</span>
                        </p>
                      ))
                    ) : (
                      <p className="break-words">
                        <strong className="text-white">Core Technical Stack: </strong>
                        <span>
                          {cv.skills.map((s: any) => (typeof s === "string" ? s : s.name)).join(", ")}
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Education (2x2 Structure) */}
              {cv.education && cv.education.length > 0 && (
                <div className="space-y-2 pt-1 font-serif">
                  <div className="border-b border-slate-700 pb-1">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300">
                      Education
                    </h4>
                  </div>
                  {cv.education.map((edu: any, eIdx: number) => (
                    <div key={eIdx} className="space-y-0.5 text-xs pt-1">
                      <div className="flex flex-col xs:flex-row justify-between items-baseline gap-1 font-bold text-white">
                        <span className="break-words">{edu.institution || "University"}</span>
                        <span className="text-slate-300 font-mono text-[11px] shrink-0">
                          {edu.graduation_year || edu.end_date || ""}
                        </span>
                      </div>
                      <div className="flex flex-col xs:flex-row justify-between items-baseline gap-1 italic text-slate-400">
                        <span className="break-words">
                          {edu.degree} {edu.field && !edu.degree?.includes(edu.field) ? `in ${edu.field}` : ""}
                        </span>
                        <span className="shrink-0">{edu.location || ""}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Certifications */}
              {cv.certifications && cv.certifications.length > 0 && (
                <div className="space-y-2 pt-1 font-serif">
                  <div className="border-b border-slate-700 pb-1">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-300">
                      Certifications
                    </h4>
                  </div>
                  {cv.certifications.map((cert: any, cIdx: number) => (
                    <div key={cIdx} className="flex flex-col xs:flex-row justify-between items-baseline gap-1 text-xs text-slate-300 pt-1">
                      <span className="font-semibold text-white break-words">
                        {typeof cert === "string" ? cert : cert.name || "Certification"}
                        {typeof cert !== "string" && cert.issuer ? ` — ${cert.issuer}` : ""}
                      </span>
                      {typeof cert !== "string" && cert.date && (
                        <span className="text-slate-400 font-mono text-[11px] shrink-0">{cert.date}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
