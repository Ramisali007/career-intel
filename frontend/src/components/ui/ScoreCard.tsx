"use client";

import { useEffect, useRef } from "react";
import { Info } from "lucide-react";

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label: string;
  sublabel?: string;
  color?: string;
}

function getScoreColor(score: number): string {
  if (score >= 85) return "#34D399"; // emerald-400
  if (score >= 70) return "#38BDF8"; // sky-400
  if (score >= 55) return "#FBBF24"; // amber-400
  if (score >= 40) return "#FB923C"; // orange-400
  return "#F87171"; // red-400
}

function getScoreLabel(score: number): string {
  if (score >= 85) return "Excellent Match";
  if (score >= 70) return "Strong Profile";
  if (score >= 55) return "Moderate Fit";
  if (score >= 40) return "Needs Optimization";
  return "Critical Gaps";
}

export function ScoreRing({
  score,
  size = 160,
  strokeWidth = 10,
  label,
  sublabel,
  color,
}: ScoreRingProps) {
  const circleRef = useRef<SVGCircleElement>(null);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const scoreColor = color || getScoreColor(score);

  useEffect(() => {
    if (circleRef.current) {
      circleRef.current.style.setProperty("--score-offset", String(offset));
    }
  }, [offset]);

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(30, 41, 59, 0.8)"
            strokeWidth={strokeWidth}
          />
          {/* Score circle */}
          <circle
            ref={circleRef}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={scoreColor}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference}
            className="score-ring-animate transition-all duration-1000"
            style={
              { filter: `drop-shadow(0 0 12px ${scoreColor}60)` } as React.CSSProperties
            }
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-extrabold tracking-tight font-sans" style={{ color: scoreColor }}>
            {Math.round(score)}
          </span>
          <span className="text-[10px] font-bold text-slate-400 font-mono uppercase tracking-wider">/ 100</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-sm font-bold text-white tracking-tight">{label}</p>
        <p className="text-xs text-slate-400 mt-0.5 font-medium">
          {sublabel || getScoreLabel(score)}
        </p>
      </div>
    </div>
  );
}

interface ScoreCardProps {
  score: number;
  label: string;
  subtitle?: string;
  tooltip?: string;
  breakdown?: { dimension: string; score: number; weight: number }[];
  className?: string;
}

export function ScoreCard({
  score,
  label,
  subtitle,
  tooltip,
  breakdown,
  className = "",
}: ScoreCardProps) {
  const scoreColor = getScoreColor(score);

  return (
    <div
      className={`relative group/card backdrop-blur-2xl bg-slate-900/80 border border-slate-800/90 rounded-2xl p-6 shadow-xl shadow-slate-950/40 hover:border-slate-700 transition-all ${className}`}
    >
      {/* Top ambient glow */}
      <div
        className="absolute -top-10 left-1/2 -translate-x-1/2 w-28 h-28 rounded-full blur-2xl pointer-events-none opacity-20 group-hover/card:opacity-40 transition-opacity"
        style={{ background: scoreColor }}
      />

      {tooltip && (
        <div className="absolute top-4 right-4 z-20">
          <div className="relative group/tooltip">
            <span
              className="w-6 h-6 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white text-xs flex items-center justify-center cursor-help border border-slate-700/60 transition-colors"
              aria-label={`About ${label}`}
            >
              <Info className="w-3.5 h-3.5" />
            </span>
            <div className="absolute right-0 bottom-full mb-2 w-64 p-3 bg-slate-900/95 backdrop-blur-2xl border border-slate-700/80 rounded-xl text-xs text-slate-300 shadow-2xl opacity-0 pointer-events-none group-hover/tooltip:opacity-100 group-hover/tooltip:pointer-events-auto transition-all duration-200 z-50">
              <p className="font-bold text-white mb-1">{label}</p>
              <p className="leading-relaxed text-slate-300">{tooltip}</p>
            </div>
          </div>
        </div>
      )}

      <ScoreRing score={score} label={label} sublabel={subtitle} />

      {breakdown && breakdown.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-800/80 space-y-2.5">
          {breakdown.slice(0, 5).map((dim) => {
            const dimColor = getScoreColor(dim.score);
            return (
              <div key={dim.dimension} className="flex items-center gap-2 sm:gap-2.5">
                <span className="text-xs text-slate-300 w-24 sm:w-28 truncate font-medium" title={dim.dimension}>
                  {dim.dimension}
                </span>
                <div className="flex-1 h-2 bg-slate-950/80 border border-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${Math.min(100, Math.max(0, dim.score))}%`,
                      backgroundColor: dimColor,
                      boxShadow: `0 0 8px ${dimColor}60`,
                    }}
                  />
                </div>
                <span
                  className="text-xs font-bold font-mono w-7 sm:w-8 text-right shrink-0"
                  style={{ color: dimColor }}
                >
                  {Math.round(dim.score)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
