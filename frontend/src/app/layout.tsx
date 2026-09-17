import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CV Analyzer | AI-Powered Career Intelligence Platform",
  description:
    "Analyze your CV against job descriptions with AI. Get transparent job match scores, ATS compatibility analysis, and evidence-backed optimization recommendations.",
  keywords: [
    "CV analyzer",
    "resume optimizer",
    "ATS checker",
    "job matching",
    "AI career intelligence",
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${poppins.variable} h-full antialiased dark`}>
      <body className="min-h-full flex flex-col bg-slate-950 text-white font-sans selection:bg-cyan-400 selection:text-slate-950">
        {children}
      </body>
    </html>
  );
}
