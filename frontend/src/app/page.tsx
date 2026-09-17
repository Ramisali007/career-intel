"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  UploadCloud,
  FileText,
  Sparkles,
  BarChart3,
  CheckCircle2,
  DownloadCloud,
} from "lucide-react";
import Lightfall from "@/components/ui/Lightfall";
import GooeyNav from "@/components/ui/GooeyNav";
import SpecularButton from "@/components/ui/SpecularButton";
import { GradientCard } from "@/components/ui/gradient-card";

export default function HomePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (typeof window !== "undefined" && localStorage.getItem("token")) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-x-hidden selection:bg-cyan-400 selection:text-slate-950 font-sans">
      {/* ── Lightfall Dynamic Canvas Background ── */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <Lightfall
          colors={["#A6C8FF", "#5227FF", "#FF9FFC", "#38BDF8", "#34D399"]}
          backgroundColor="#050B24"
          speed={0.75}
          streakCount={6}
          streakWidth={1.2}
          streakLength={1.3}
          glow={1.2}
          density={0.85}
          twinkle={0.85}
          zoom={2.4}
          backgroundGlow={0.65}
          opacity={0.88}
          mouseInteraction={true}
          mouseStrength={0.9}
          mouseRadius={0.75}
        />
        {/* Subtle dark vignette overlay to ensure text contrast */}
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950/40 via-transparent to-slate-950/90 pointer-events-none" />
      </div>

      {/* ── Content Container (z-10 ensures clicks and interactions work seamlessly) ── */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Floating Pill Navigation */}
        <header className="px-3 sm:px-6 pt-4 sm:pt-6 pb-2 w-full max-w-6xl mx-auto">
          <nav className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-full px-3.5 sm:px-6 py-2 sm:py-2.5 flex items-center justify-between shadow-2xl shadow-indigo-950/40 hover:border-slate-700/80 transition-all gap-2">
            {/* Brand / Logo */}
            <Link
              href={isLoggedIn ? "/dashboard" : "/"}
              className="flex items-center gap-2 sm:gap-2.5 group flex-shrink-0"
            >
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-br from-cyan-400 via-indigo-500 to-fuchsia-500 flex items-center justify-center p-[1.5px] shadow-lg shadow-cyan-500/25 group-hover:scale-105 transition-transform">
                <div className="w-full h-full bg-slate-950 rounded-full flex items-center justify-center">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-fuchsia-300 font-black text-[10px] sm:text-xs">
                    CI
                  </span>
                </div>
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-sm sm:text-base tracking-tight text-white group-hover:text-cyan-300 transition-colors">
                  Career<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">Intel</span>
                </span>
                <span className="hidden xs:block text-[8px] sm:text-[9px] text-cyan-400/90 font-mono tracking-widest uppercase -mt-0.5">
                  AI ATS Intelligence
                </span>
              </div>
            </Link>

            {/* GooeyNav Centerpiece */}
            <div className="hidden md:flex items-center justify-center flex-1 px-4">
              <GooeyNav
                items={
                  isLoggedIn
                    ? [
                        { label: "Dashboard", href: "/dashboard" },
                        { label: "History", href: "/history" },
                        { label: "Single JD", href: "/analyze" },
                        { label: "Multi-JD", href: "/analyze/multi" },
                      ]
                    : [
                        { label: "Overview", href: "#" },
                        { label: "Features", href: "#features" },
                        { label: "Workflow", href: "#workflow" },
                        { label: "Multi-JD", href: "/login" },
                      ]
                }
                initialActiveIndex={0}
                animationTime={550}
                particleCount={14}
                particleDistances={[75, 12]}
                particleR={90}
                timeVariance={250}
                colors={[1, 2, 3, 1, 2, 4]}
              />
            </div>

            {/* Actions on the right */}
            <div className="flex items-center gap-1.5 sm:gap-3 flex-shrink-0">
              {isLoggedIn ? (
                <>
                  <SpecularButton
                    size="sm"
                    radius={9999}
                    tint="#34d399"
                    tintOpacity={0.95}
                    textColor="#020617"
                    lineColor="#ffffff"
                    baseColor="#059669"
                    intensity={1.2}
                    shineSize={12}
                    shineFade={40}
                    thickness={1.2}
                    followMouse
                    onClick={() => router.push("/analyze")}
                  >
                    + Analyze
                  </SpecularButton>
                  <button
                    onClick={() => {
                      if (confirm("Are you sure you want to sign out?")) {
                        localStorage.removeItem("token");
                        setIsLoggedIn(false);
                      }
                    }}
                    title="Sign out of account"
                    className="text-xs text-slate-300 hover:text-rose-400 hover:bg-rose-500/10 border border-slate-800/80 hover:border-rose-500/30 px-2.5 sm:px-3.5 py-1.5 sm:py-2 rounded-full transition-all flex items-center gap-1.5 font-medium"
                  >
                    <span>Sign Out</span>
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-xs sm:text-sm font-medium text-slate-200 hover:text-white px-2.5 sm:px-3.5 py-1.5 sm:py-2 rounded-full hover:bg-slate-800/60 transition-colors"
                  >
                    Sign in
                  </Link>
                  <SpecularButton
                    size="sm"
                    radius={9999}
                    tint="#ffffff"
                    tintOpacity={0.95}
                    textColor="#020617"
                    lineColor="#ffffff"
                    baseColor="#cbd5e1"
                    intensity={1.1}
                    shineSize={12}
                    shineFade={40}
                    thickness={1.2}
                    followMouse
                    onClick={() => router.push("/register")}
                  >
                    Sign up
                  </SpecularButton>
                </>
              )}
            </div>
          </nav>
        </header>

        {/* ── Hero Section ── */}
        <main className="flex-1 flex flex-col items-center justify-center text-center px-4 sm:px-6 pt-8 sm:pt-12 lg:pt-20 pb-20 sm:pb-28 max-w-5xl mx-auto w-full">
          <div
            className={`transition-all duration-1000 transform ${
              mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
            }`}
          >
            {/* Pill Badge */}
            <div className="inline-flex items-center gap-2 sm:gap-2.5 backdrop-blur-xl bg-slate-900/70 border border-slate-700/60 rounded-full px-3 sm:px-4 py-1.5 mb-6 sm:mb-8 shadow-xl shadow-indigo-950/40 hover:border-slate-600 transition-colors max-w-full">
              <span className="bg-white text-slate-950 text-[10px] sm:text-[11px] font-extrabold px-2 sm:px-2.5 py-0.5 rounded-full uppercase tracking-wider shrink-0">
                NEW
              </span>
              <span className="text-[11px] sm:text-xs font-semibold text-white truncate">
                Deterministic Truth-First CV Intelligence
              </span>
            </div>

            {/* Headline */}
            <h1 className="text-3xl sm:text-5xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl leading-[1.15] mb-6 drop-shadow-sm break-words">
              Let the truth <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-cyan-300 via-indigo-100 to-fuchsia-300 bg-clip-text text-transparent">
                power your next career move
              </span>
            </h1>

            {/* Subtitle with bright, high-contrast white text */}
            <p className="text-sm sm:text-lg text-slate-100 max-w-2xl mx-auto leading-relaxed mb-8 sm:mb-10 font-normal px-2">
              Transparent, evidence-backed CV analysis and job matching. See your
              exact match score, ATS compatibility signals, and actionable recommendations —{" "}
              <strong className="text-white font-bold underline decoration-cyan-400 decoration-2 underline-offset-4">
                without fabricating a single qualification
              </strong>.
            </p>

            {/* Primary Action Buttons using SpecularButton */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 sm:gap-4 w-full max-w-md mx-auto px-2">
              <SpecularButton
                size="lg"
                radius={9999}
                tint="#ffffff"
                tintOpacity={0.96}
                textColor="#020617"
                lineColor="#ffffff"
                baseColor="#e2e8f0"
                intensity={1.25}
                shineSize={14}
                shineFade={45}
                thickness={1.5}
                speed={0.35}
                followMouse
                proximity={260}
                className="w-full sm:w-auto shadow-2xl shadow-white/15"
                onClick={() => router.push(isLoggedIn ? "/dashboard" : "/login")}
              >
                <span className="font-bold">{isLoggedIn ? "Go to Dashboard" : "Get started"}</span>
                <svg
                  className="w-4 h-4 ml-1 inline-block"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2.5"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </SpecularButton>

              <SpecularButton
                size="lg"
                radius={9999}
                tint="#0f172a"
                tintOpacity={0.7}
                blur={16}
                textColor="#ffffff"
                lineColor="#38bdf8"
                baseColor="#334155"
                intensity={1.1}
                shineSize={16}
                shineFade={50}
                thickness={1.3}
                speed={0.35}
                followMouse
                proximity={260}
                className="w-full sm:w-auto border border-slate-700/80 shadow-xl shadow-slate-950/40"
                onClick={() => router.push(isLoggedIn ? "/analyze" : "/register")}
              >
                <span className="font-semibold">{isLoggedIn ? "Analyze CV →" : "Create Account"}</span>
              </SpecularButton>
            </div>
          </div>

          {/* ── Interactive Triple Scores KPI Preview (Using GradientCard) ── */}
          <div
            className={`mt-20 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-5xl w-full text-left transition-all duration-1000 delay-200 ${
              mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
            }`}
          >
            <GradientCard
              badgeText="Semantic Alignment"
              badgeColor="#38BDF8"
              gradient="cyan"
              title="Job Match"
              score={84}
              icon="🎯"
              description="Evaluates your verified qualifications against mandatory and preferred job requirements."
              ctaText="Explore alignment details"
              ctaHref={isLoggedIn ? "/analyze" : "/login"}
            />
            <GradientCard
              badgeText="Parser Safety & Structure"
              badgeColor="#34D399"
              gradient="green"
              title="ATS Precision"
              score={93}
              icon="📄"
              description="Verifies multi-column safety, standard section headings, font compatibility, and zero-loss extraction."
              ctaText="Inspect ATS signals"
              ctaHref={isLoggedIn ? "/analyze" : "/login"}
            />
            <GradientCard
              badgeText="Writing & Impact"
              badgeColor="#A855F7"
              gradient="purple"
              title="CV Quality"
              score={88}
              icon="✨"
              description="Analyzes quantifiable metric density, active power verbs, clarity, conciseness, and professionalism."
              ctaText="View quality breakdown"
              ctaHref={isLoggedIn ? "/analyze" : "/login"}
            />
          </div>

          {/* ── Feature Highlights (Using GradientCard) ── */}
          <div
            id="features"
            className={`mt-28 grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-5xl w-full text-left transition-all duration-1000 delay-300 ${
              mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
            }`}
          >
            <GradientCard
              badgeText="Zero Hallucinations"
              badgeColor="#38BDF8"
              gradient="cyan"
              title="Evidence-Backed Matching"
              description="Every single match percentage directly cites the exact line in your CV. No vague generalities or black-box assertions."
              ctaText="Learn about evidence tracing"
              ctaHref={isLoggedIn ? "/analyze" : "/login"}
              icon="🔍"
            />
            <GradientCard
              badgeText="Ethical AI Guarantee"
              badgeColor="#34D399"
              gradient="green"
              title="Zero Qualification Fabrication"
              description="We strictly never invent skills, experience, or untrue credentials. Your professional reputation stays 100% honest."
              ctaText="Read truth-first policy"
              ctaHref={isLoggedIn ? "/analyze" : "/login"}
              icon="🛡️"
            />
            <GradientCard
              badgeText="Decoupled Metrics"
              badgeColor="#A855F7"
              gradient="purple"
              title="Deterministic Tri-Scoring"
              description="Job Match, ATS Parsing, and Writing Quality remain independent scores computed by deterministic algorithms."
              ctaText="Discover scoring dimensions"
              ctaHref={isLoggedIn ? "/analyze" : "/login"}
              icon="⚖️"
            />
            <GradientCard
              badgeText="Multi-Opportunity Audit"
              badgeColor="#F59E0B"
              gradient="orange"
              title="Multi-JD Comparison"
              description="Simultaneously benchmark your CV against multiple roles to discover which vacancy yields your highest natural match."
              ctaText="Try Multi-JD Comparison"
              ctaHref={isLoggedIn ? "/analyze/multi" : "/login"}
              icon="📑"
            />
          </div>

          {/* ── How It Works (Workflow) ── */}
          <div
            id="workflow"
            className={`mt-32 max-w-6xl w-full transition-all duration-1000 delay-500 pb-16 ${
              mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-12"
            }`}
          >
            <div className="text-center mb-14">
              <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold tracking-wider uppercase shadow-inner shadow-cyan-500/10 mb-3">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                Step by Step Pipeline
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                How CareerIntel Works
              </h2>
              <p className="text-sm sm:text-base text-slate-300 max-w-xl mx-auto mt-2 font-normal">
                Deterministic precision pipeline engineered from initial resume upload to ATS-compliant job delivery.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 sm:gap-5">
              {[
                {
                  step: "01",
                  label: "Upload CV",
                  desc: "PDF & DOCX structural AST extraction",
                  icon: UploadCloud,
                  accent: "from-cyan-400 via-sky-500 to-blue-500",
                  glow: "rgba(6, 182, 212, 0.25)",
                  badge: "text-cyan-300 bg-cyan-950/70 border-cyan-500/30",
                  iconColor: "text-cyan-300",
                  iconBg: "bg-cyan-500/10 border-cyan-500/20 shadow-cyan-500/20",
                  hoverBorder: "group-hover:border-cyan-500/50",
                },
                {
                  step: "02",
                  label: "Paste JD",
                  desc: "Target role criteria & skill taxonomy",
                  icon: FileText,
                  accent: "from-blue-400 via-indigo-500 to-violet-500",
                  glow: "rgba(99, 102, 241, 0.25)",
                  badge: "text-indigo-300 bg-indigo-950/70 border-indigo-500/30",
                  iconColor: "text-indigo-300",
                  iconBg: "bg-indigo-500/10 border-indigo-500/20 shadow-indigo-500/20",
                  hoverBorder: "group-hover:border-indigo-500/50",
                },
                {
                  step: "03",
                  label: "Deep AI Audit",
                  desc: "Multi-agent semantic tri-scoring",
                  icon: Sparkles,
                  accent: "from-purple-400 via-fuchsia-500 to-pink-500",
                  glow: "rgba(168, 85, 247, 0.25)",
                  badge: "text-purple-300 bg-purple-950/70 border-purple-500/30",
                  iconColor: "text-purple-300",
                  iconBg: "bg-purple-500/10 border-purple-500/20 shadow-purple-500/20",
                  hoverBorder: "group-hover:border-purple-500/50",
                },
                {
                  step: "04",
                  label: "Review Matrix",
                  desc: "Deterministic keyword & ATS gaps",
                  icon: BarChart3,
                  accent: "from-emerald-400 via-teal-500 to-cyan-500",
                  glow: "rgba(16, 185, 129, 0.25)",
                  badge: "text-emerald-300 bg-emerald-950/70 border-emerald-500/30",
                  iconColor: "text-emerald-300",
                  iconBg: "bg-emerald-500/10 border-emerald-500/20 shadow-emerald-500/20",
                  hoverBorder: "group-hover:border-emerald-500/50",
                },
                {
                  step: "05",
                  label: "Approve Fixes",
                  desc: "Human-in-the-loop granular rewrites",
                  icon: CheckCircle2,
                  accent: "from-amber-400 via-orange-500 to-rose-500",
                  glow: "rgba(245, 158, 11, 0.25)",
                  badge: "text-amber-300 bg-amber-950/70 border-amber-500/30",
                  iconColor: "text-amber-300",
                  iconBg: "bg-amber-500/10 border-amber-500/20 shadow-amber-500/20",
                  hoverBorder: "group-hover:border-amber-500/50",
                },
                {
                  step: "06",
                  label: "Export PDF",
                  desc: "High-yield ATS-optimized resume",
                  icon: DownloadCloud,
                  accent: "from-rose-400 via-pink-500 to-fuchsia-500",
                  glow: "rgba(244, 63, 94, 0.25)",
                  badge: "text-rose-300 bg-rose-950/70 border-rose-500/30",
                  iconColor: "text-rose-300",
                  iconBg: "bg-rose-500/10 border-rose-500/20 shadow-rose-500/20",
                  hoverBorder: "group-hover:border-rose-500/50",
                },
              ].map((s) => {
                const IconComponent = s.icon;
                return (
                  <motion.div
                    key={s.step}
                    whileHover={{ y: -6, scale: 1.025 }}
                    transition={{ type: "spring", stiffness: 350, damping: 22 }}
                    className="relative group h-full"
                  >
                    <div
                      className={`relative h-full backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-2xl p-5 flex flex-col items-center text-center shadow-xl shadow-slate-950/50 transition-all duration-300 overflow-hidden ${s.hoverBorder}`}
                    >
                      {/* Ambient Radial Spotlight */}
                      <div
                        className="absolute -top-12 left-1/2 -translate-x-1/2 w-32 h-32 rounded-full blur-2xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                        style={{ background: s.glow }}
                      />

                      {/* Step Badge */}
                      <div
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-[10px] font-mono font-bold tracking-widest mb-4 shadow-sm ${s.badge}`}
                      >
                        STEP {s.step}
                      </div>

                      {/* Icon Container with Glass Sheen */}
                      <div
                        className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-lg mb-3.5 group-hover:scale-110 transition-transform duration-300 relative z-10 ${s.iconBg}`}
                      >
                        <IconComponent className={`w-6 h-6 ${s.iconColor}`} />
                      </div>

                      {/* Title */}
                      <h3 className="text-sm font-bold text-white tracking-tight leading-snug group-hover:text-white transition-colors relative z-10">
                        {s.label}
                      </h3>

                      {/* Subtitle / Description */}
                      <p className="text-[11px] text-slate-300 mt-1.5 font-normal leading-relaxed relative z-10">
                        {s.desc}
                      </p>

                      {/* Bottom Glowing Border Flare on Hover */}
                      <div
                        className={`absolute bottom-0 inset-x-4 h-[2px] rounded-full bg-gradient-to-r ${s.accent} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
                      />
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
