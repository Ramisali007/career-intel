"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowLeft,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import api from "@/lib/api";
import Lightfall from "@/components/ui/Lightfall";
import SpecularButton from "@/components/ui/SpecularButton";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && localStorage.getItem("token")) {
      router.replace("/dashboard");
    }
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.register(email, password, fullName);
      router.replace("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white relative flex items-center justify-center p-4 sm:p-6 overflow-hidden font-sans selection:bg-cyan-400 selection:text-slate-950">
      {/* ── Background Lightfall Canvas ── */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <Lightfall
          colors={["#A6C8FF", "#5227FF", "#FF9FFC", "#38BDF8", "#34D399"]}
          backgroundColor="#050B24"
          speed={0.65}
          streakCount={6}
          streakWidth={1.2}
          streakLength={1.3}
          glow={1.1}
          density={0.8}
          twinkle={0.8}
          zoom={2.4}
          backgroundGlow={0.6}
          opacity={0.85}
          mouseInteraction={true}
          mouseStrength={0.8}
          mouseRadius={0.7}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950/50 via-slate-950/20 to-slate-950/90 pointer-events-none" />
      </div>

      {/* Floating Back to Home Button */}
      <div className="fixed top-4 left-4 sm:top-6 sm:left-6 z-20">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full backdrop-blur-xl bg-slate-900/80 border border-slate-800 text-xs font-semibold text-slate-200 hover:text-white hover:border-slate-600 shadow-lg shadow-slate-950/40 transition-all group"
        >
          <ArrowLeft className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform text-cyan-400" />
          <span>Home</span>
        </Link>
      </div>

      {/* ── Form Card ── */}
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md relative z-10 my-8"
      >
        {/* Outer Glow Halo */}
        <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500/20 via-indigo-500/20 to-fuchsia-500/20 rounded-[32px] blur-xl opacity-70 pointer-events-none" />

        <div className="relative backdrop-blur-2xl bg-slate-900/85 border border-slate-800/90 rounded-3xl p-7 sm:p-9 shadow-2xl shadow-indigo-950/50 overflow-hidden">
          {/* Header Brand */}
          <div className="text-center mb-7">
            <Link href="/" className="inline-flex items-center gap-2.5 mb-4 group">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-cyan-400 via-indigo-500 to-fuchsia-500 flex items-center justify-center p-[1.5px] shadow-lg shadow-cyan-500/25 group-hover:scale-105 transition-transform">
                <div className="w-full h-full bg-slate-950 rounded-full flex items-center justify-center">
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-fuchsia-300 font-black text-xs">
                    CI
                  </span>
                </div>
              </div>
              <span className="text-xl font-extrabold text-white tracking-tight">
                Career<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">Intel</span>
              </span>
            </Link>

            <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-[11px] font-semibold tracking-wider uppercase mb-2 shadow-inner">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              Instant Free Access
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Create your account
            </h1>
            <p className="mt-1.5 text-xs sm:text-sm text-slate-300 font-normal">
              Unlock deterministic ATS scoring and AI resume audits
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-2.5 bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-xs text-red-200"
              >
                <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </motion.div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-200 uppercase tracking-wider mb-2">
                Full Name
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  className="w-full bg-slate-950/70 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all"
                  placeholder="John Doe"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-200 uppercase tracking-wider mb-2">
                Email Address
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full bg-slate-950/70 border border-slate-700/80 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all"
                  placeholder="name@company.com"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-xs font-semibold text-slate-200 uppercase tracking-wider">
                  Password
                </label>
                <span className="text-[11px] text-slate-400">Min 8 characters</span>
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-cyan-400 transition-colors">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full bg-slate-950/70 border border-slate-700/80 rounded-xl pl-10 pr-10 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 transition-all"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="pt-3">
              <SpecularButton
                type="submit"
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
                disabled={loading}
                className="w-full shadow-lg shadow-cyan-500/10"
              >
                <span className="font-bold flex items-center justify-center gap-2">
                  {loading ? "Creating account..." : "Create Free Account"}
                </span>
              </SpecularButton>
            </div>

            <div className="pt-2 text-center">
              <p className="text-xs text-slate-300">
                Already have an account?{" "}
                <Link
                  href="/login"
                  className="text-cyan-400 hover:text-cyan-300 font-semibold underline underline-offset-4 ml-1 transition-colors"
                >
                  Sign in
                </Link>
              </p>
            </div>
          </form>

          {/* Trust badges footer */}
          <div className="mt-6 pt-5 border-t border-slate-800/80 flex items-center justify-center gap-4 text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              No credit card required
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
              100% Free
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
