"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

import { cn } from "@/lib/utils";

// Define variants for the card's overall style using cva
const cardVariants = cva(
  "relative flex flex-col justify-between h-full w-full overflow-hidden rounded-3xl p-7 sm:p-8 shadow-xl transition-all duration-300 backdrop-blur-xl border border-white/10 hover:shadow-2xl hover:border-white/20 group",
  {
    variants: {
      gradient: {
        orange: "bg-gradient-to-br from-amber-500/20 via-orange-500/10 to-slate-900/80",
        gray: "bg-gradient-to-br from-slate-700/25 via-slate-800/20 to-slate-900/80",
        purple: "bg-gradient-to-br from-purple-500/20 via-indigo-500/10 to-slate-900/80",
        green: "bg-gradient-to-br from-emerald-500/20 via-teal-500/10 to-slate-900/80",
        cyan: "bg-gradient-to-br from-cyan-500/20 via-blue-500/10 to-slate-900/80",
      },
    },
    defaultVariants: {
      gradient: "gray",
    },
  }
);

// Define the props interface for type safety and reusability
export interface GradientCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  badgeText: string;
  badgeColor: string; // Expecting a hex color string, e.g., "#FF5733"
  title: string;
  description: string;
  ctaText?: string;
  ctaHref?: string;
  imageUrl?: string;
  score?: number | string;
  icon?: React.ReactNode;
}

const GradientCard = React.forwardRef<HTMLDivElement, GradientCardProps>(
  (
    {
      className,
      gradient,
      badgeText,
      badgeColor,
      title,
      description,
      ctaText,
      ctaHref,
      imageUrl,
      score,
      icon,
      ...props
    },
    ref
  ) => {
    // Animation variants for framer-motion
    const cardAnimation = {
      rest: { scale: 1, y: 0 },
      hover: { scale: 1.025, y: -4 },
    };

    const imageAnimation = {
      rest: { scale: 1, rotate: 0 },
      hover: { scale: 1.08, rotate: 2 },
    };

    return (
      <motion.div
        variants={cardAnimation}
        initial="rest"
        whileHover="hover"
        animate="rest"
        className="h-full"
        ref={ref}
      >
        <div className={cn(cardVariants({ gradient }), className)} {...props}>
          {/* Decorative background image or abstract graphic with animation */}
          {imageUrl && (
            <motion.img
              src={imageUrl}
              alt={`${title} background graphic`}
              variants={imageAnimation}
              transition={{ type: "spring", stiffness: 400, damping: 15 }}
              className="absolute -right-10 -bottom-10 w-44 sm:w-56 opacity-40 pointer-events-none group-hover:opacity-60 transition-opacity"
            />
          )}

          {/* Ambient light blur in corner */}
          <div
            className="absolute -top-12 -right-12 w-36 h-36 rounded-full blur-3xl pointer-events-none opacity-25"
            style={{ backgroundColor: badgeColor }}
          />

          {/* Card Content */}
          <div className="z-10 flex flex-col h-full relative">
            {/* Top row: Badge & optional icon */}
            <div className="flex items-center justify-between gap-2 mb-4">
              <div className="inline-flex items-center gap-2 rounded-full bg-slate-950/60 px-3.5 py-1 text-xs font-semibold text-white backdrop-blur-md border border-white/10 w-fit shadow-sm">
                <span
                  className="h-2 w-2 rounded-full animate-pulse"
                  style={{ backgroundColor: badgeColor }}
                />
                {badgeText}
              </div>
              {icon && (
                <div className="text-2xl p-2 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md">
                  {icon}
                </div>
              )}
            </div>

            {/* Title, Score & Description */}
            <div className="flex-grow my-1">
              <div className="flex items-baseline gap-2 mb-2">
                <h3 className="text-2xl font-extrabold text-white tracking-tight">{title}</h3>
                {score !== undefined && (
                  <span className="text-2xl font-black text-cyan-300 ml-auto">
                    {score}
                    <span className="text-xs text-slate-400 font-normal">/100</span>
                  </span>
                )}
              </div>
              <p className="text-slate-100 text-sm leading-relaxed max-w-sm font-normal">
                {description}
              </p>
            </div>

            {/* Call to Action Link */}
            {ctaText && ctaHref && (
              <a
                href={ctaHref}
                className="group/btn mt-6 inline-flex items-center gap-2 text-sm font-bold text-white hover:text-cyan-300 transition-colors w-fit"
              >
                <span>{ctaText}</span>
                <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover/btn:translate-x-1.5 text-cyan-400" />
              </a>
            )}
          </div>
        </div>
      </motion.div>
    );
  }
);
GradientCard.displayName = "GradientCard";

export { GradientCard, cardVariants };
