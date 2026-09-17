"use client";

import { useEffect, useState, useRef } from "react";

interface Stage {
  id: string;
  label: string;
  icon: string;
}

const PIPELINE_STAGES: Stage[] = [
  { id: "parsing_cv", label: "Reading CV", icon: "📄" },
  { id: "parsing_jd", label: "Understanding JD", icon: "📋" },
  { id: "matching", label: "Comparing experience", icon: "🔍" },
  { id: "scoring", label: "Calculating scores", icon: "📊" },
  { id: "scoring_ats", label: "ATS compatibility", icon: "🛡️" },
  { id: "scoring_quality", label: "Quality analysis", icon: "✨" },
  { id: "recommendations", label: "Generating insights", icon: "💡" },
];

interface ProcessingStatusProps {
  analysisId: string;
  onComplete: () => void;
}

export function ProcessingStatus({ analysisId, onComplete }: ProcessingStatusProps) {
  const [status, setStatus] = useState<string>("queued");
  const [currentStep, setCurrentStep] = useState<string>("Starting analysis...");
  const [progress, setProgress] = useState<number>(0);
  const [stagesCompleted, setStagesCompleted] = useState<string[]>([]);
  const [error, setError] = useState<string>("");
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Poll every 2 seconds
    const poll = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/analyses/${analysisId}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        if (!res.ok) return;
        const data = await res.json();

        setStatus(data.status);
        setCurrentStep(data.current_step || "Processing...");
        setProgress(data.progress || 0);
        setStagesCompleted(data.stages_completed || []);

        // Terminal states
        if (
          data.status === "completed" ||
          data.status === "waiting_for_approval" ||
          data.status === "failed"
        ) {
          if (intervalRef.current) clearInterval(intervalRef.current);
          if (data.status === "failed") {
            setError(data.error || "Analysis failed");
          } else {
            onComplete();
          }
        }
      } catch {
        // Silently retry
      }
    };

    poll();
    intervalRef.current = setInterval(poll, 2000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [analysisId, onComplete]);

  function getStageStatus(stage: Stage): "done" | "active" | "pending" {
    if (stagesCompleted.includes(stage.id)) return "done";
    // If the current status name contains this stage's ID, it's active
    if (status.includes(stage.id.replace("_", "")) || status.includes(stage.id)) return "active";
    // Check progress-based estimation
    const stageIndex = PIPELINE_STAGES.findIndex((s) => s.id === stage.id);
    const doneCount = stagesCompleted.length;
    if (stageIndex === doneCount) return "active";
    if (stageIndex < doneCount) return "done";
    return "pending";
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <div className="max-w-lg w-full">
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center mx-auto mb-6 pulse-glow">
            <svg
              className="w-8 h-8 text-white animate-spin"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-white">Analyzing Your CV</h2>
          <p className="text-sm text-slate-400 mt-2">
            {currentStep}
          </p>
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>Progress</span>
            <span className="font-mono font-semibold text-white">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${Math.max(3, progress)}%` }}
            />
          </div>
        </div>

        {/* Pipeline stages */}
        <div className="glass rounded-2xl p-6 border border-slate-800 space-y-0">
          {PIPELINE_STAGES.map((stage, idx) => {
            const stageStatus = getStageStatus(stage);
            return (
              <div key={stage.id} className="flex items-center gap-4">
                {/* Line connector */}
                <div className="flex flex-col items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm transition-all duration-500 ${
                      stageStatus === "done"
                        ? "bg-emerald-500/20 border-2 border-emerald-500"
                        : stageStatus === "active"
                        ? "bg-cyan-500/20 border-2 border-cyan-400 animate-pulse"
                        : "bg-slate-800 border-2 border-slate-700"
                    }`}
                  >
                    {stageStatus === "done" ? (
                      <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <span className="text-xs">{stage.icon}</span>
                    )}
                  </div>
                  {idx < PIPELINE_STAGES.length - 1 && (
                    <div
                      className={`w-0.5 h-6 transition-all duration-500 ${
                        stageStatus === "done" ? "bg-emerald-500/40" : "bg-slate-700"
                      }`}
                    />
                  )}
                </div>

                {/* Label */}
                <span
                  className={`text-sm font-medium transition-colors ${
                    stageStatus === "done"
                      ? "text-emerald-400"
                      : stageStatus === "active"
                      ? "text-white"
                      : "text-slate-500"
                  }`}
                >
                  {stage.label}
                  {stageStatus === "active" && (
                    <span className="ml-2 text-xs text-cyan-400 animate-pulse">●</span>
                  )}
                </span>
              </div>
            );
          })}
        </div>

        {/* Error state */}
        {error && (
          <div className="mt-6 bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 text-sm text-rose-400">
            <p className="font-semibold mb-1">Analysis Failed</p>
            <p className="text-rose-400/80">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
