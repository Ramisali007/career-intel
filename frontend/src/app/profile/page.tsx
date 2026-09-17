"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  User,
  Briefcase,
  FileText,
  Sparkles,
  ShieldAlert,
  Trash2,
  Plus,
  Save,
  CheckCircle2,
  X,
  ShieldCheck,
} from "lucide-react";
import api from "@/lib/api";
import { Navbar } from "@/components/ui/Navbar";
import SpecularButton from "@/components/ui/SpecularButton";

export default function ProfilePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [purging, setPurging] = useState(false);
  const [savedMessage, setSavedMessage] = useState("");
  const [newSkill, setNewSkill] = useState("");
  const [newRole, setNewRole] = useState("");

  // Form states
  const [fullName, setFullName] = useState("");
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [targetRoles, setTargetRoles] = useState<string[]>([]);
  const [targetIndustries, setTargetIndustries] = useState<string[]>([]);
  const [skills, setSkills] = useState<string[]>([]);

  async function handlePurgeData() {
    if (!confirm("WARNING: This will permanently purge all your CVs, documents, job descriptions, analyses, and profile data. This cannot be undone. Are you sure?")) return;
    setPurging(true);
    try {
      const res = await api.purgeUserData();
      alert(res.message || "All user data purged successfully.");
      await loadProfile();
    } catch (err: any) {
      alert(err.message || "Failed to purge data");
    } finally {
      setPurging(false);
    }
  }

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.replace("/login");
      return;
    }
    loadProfile();
  }, [router]);

  async function loadProfile() {
    try {
      const data = await api.getProfile();
      setProfile(data);
      setFullName(data.full_name || "");
      setHeadline(data.headline || "");
      setSummary(data.professional_summary || "");
      setTargetRoles(data.target_roles || []);
      setTargetIndustries(data.target_industries || []);
      setSkills(data.skills || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSavedMessage("");
    try {
      await api.updateProfile({
        full_name: fullName,
        headline: headline,
        professional_summary: summary,
        target_roles: targetRoles,
        target_industries: targetIndustries,
        skills: skills,
      });
      setSavedMessage("Master career profile saved successfully!");
      setTimeout(() => setSavedMessage(""), 4000);
    } catch (err: any) {
      alert(err.message || "Failed to update profile");
    } finally {
      setSaving(false);
    }
  }

  function handleAddSkill() {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()]);
      setNewSkill("");
    }
  }

  function handleRemoveSkill(skillToRemove: string) {
    setSkills(skills.filter((s) => s !== skillToRemove));
  }

  function handleAddRole() {
    if (newRole.trim() && !targetRoles.includes(newRole.trim())) {
      setTargetRoles([...targetRoles, newRole.trim()]);
      setNewRole("");
    }
  }

  function handleRemoveRole(roleToRemove: string) {
    setTargetRoles(targetRoles.filter((r) => r !== roleToRemove));
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="mt-4 text-slate-400 font-medium">Loading Master Career Profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950 relative overflow-x-hidden">
      {/* Background ambient backlights */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 right-1/3 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl" />
      </div>

      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
        {/* Header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-semibold tracking-wider uppercase mb-3 shadow-inner">
              <User className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
              Master Career Evidence Graph
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Master Career Profile
            </h1>
            <p className="mt-1 text-sm text-slate-300 font-normal">
              Maintain your cumulative skill taxonomy, verified target roles, and professional foundation.
            </p>
          </div>

          <AnimatePresence>
            {savedMessage && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="px-4 py-2 bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 rounded-full text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-950/40"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>{savedMessage}</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <form onSubmit={handleSave} className="space-y-6">
          {/* Section 1: Identity & Target Roles */}
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 sm:p-7 shadow-xl shadow-slate-950/40 space-y-5">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
                <User className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Candidate Identity & Target Trajectory
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Jane Doe"
                  className="w-full bg-slate-950/70 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400 transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Professional Headline
                </label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  placeholder="e.g. Senior Distributed Systems Engineer"
                  className="w-full bg-slate-950/70 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400 transition-colors"
                />
              </div>
            </div>

            {/* Target Roles */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Target Roles (Roadmap Vacancies)
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddRole())}
                  placeholder="Add target role (e.g. Staff Backend Engineer) and press Enter"
                  className="flex-1 bg-slate-950/70 border border-slate-700/80 rounded-xl px-4 py-2 text-xs sm:text-sm text-white focus:outline-none focus:border-cyan-400 transition-colors"
                />
                <button
                  type="button"
                  onClick={handleAddRole}
                  className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-xl text-xs font-bold transition-colors"
                >
                  Add Role
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                {targetRoles.map((role, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 rounded-lg text-xs bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 flex items-center gap-1.5 font-semibold"
                  >
                    <span>{role}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveRole(role)}
                      className="text-cyan-400 hover:text-rose-400 transition-colors"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Section 2: Master Summary */}
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 sm:p-7 shadow-xl shadow-slate-950/40 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
                <FileText className="w-4 h-4" />
              </div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Master Professional Summary
              </h3>
            </div>
            <p className="text-xs text-slate-400">
              The overarching summary of your accomplishments, impact, and engineering philosophy used to anchor automated rewrites.
            </p>
            <textarea
              rows={4}
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="e.g. Results-driven engineer with 8+ years architecting scalable cloud-native architectures, low-latency microservices, and leading high-performing teams..."
              className="w-full bg-slate-950/70 border border-slate-700/80 rounded-2xl p-4 text-xs sm:text-sm text-slate-200 leading-relaxed focus:outline-none focus:border-cyan-400 transition-colors resize-none"
            />
          </div>

          {/* Section 3: Master Skills Inventory */}
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-3xl p-6 sm:p-7 shadow-xl shadow-slate-950/40 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white tracking-tight">
                    Master Skills Inventory
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Verified technical skills tracked across all versions
                  </p>
                </div>
              </div>
              <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-500/30">
                {skills.length} Skills Tracked
              </span>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSkill())}
                placeholder="Add skill (e.g. Kubernetes, Rust, GraphQL) and press Enter"
                className="flex-1 bg-slate-950/70 border border-slate-700/80 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white focus:outline-none focus:border-cyan-400 transition-colors"
              />
              <button
                type="button"
                onClick={handleAddSkill}
                className="bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 px-5 py-2.5 rounded-xl text-xs font-bold transition-colors"
              >
                + Add Skill
              </button>
            </div>

            <div className="flex flex-wrap gap-2 pt-2">
              {skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 rounded-xl text-xs bg-slate-950/80 text-slate-200 border border-slate-800 flex items-center gap-2 font-mono group hover:border-slate-600 transition-colors"
                >
                  <span>{skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill)}
                    className="text-slate-500 group-hover:text-rose-400 transition-colors font-bold"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Section 4: Data Privacy & Account Purge */}
          <div className="backdrop-blur-2xl bg-slate-900/80 border border-rose-500/30 rounded-3xl p-6 sm:p-7 shadow-xl shadow-slate-950/40 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center flex-shrink-0">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-rose-300">
                    Data Privacy & GDPR Data Erasure
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-xl leading-relaxed">
                    Permanently delete all uploaded resumes, documents, job descriptions, analysis histories, and recommendations.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={handlePurgeData}
                disabled={purging}
                className="bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 px-5 py-2.5 rounded-xl text-xs font-bold transition-colors shrink-0 disabled:opacity-50"
              >
                {purging ? "Purging Data..." : "Purge All My Data"}
              </button>
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex items-center justify-end gap-4 pt-4">
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
              disabled={saving}
              className="shadow-xl shadow-cyan-500/15"
            >
              <span className="font-bold flex items-center gap-2 px-3 py-0.5">
                <Save className="w-4 h-4 text-indigo-600" />
                {saving ? "Saving Profile..." : "Save Master Profile"}
              </span>
            </SpecularButton>
          </div>
        </form>
      </main>
    </div>
  );
}
