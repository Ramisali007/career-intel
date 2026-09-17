"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  LayoutDashboard, 
  Plus, 
  Layers, 
  History, 
  User, 
  LogOut,
  Sparkles,
  Menu,
  X
} from "lucide-react";
import api from "@/lib/api";

interface NavbarProps {
  currentPath?: string;
  children?: React.ReactNode;
}

export function Navbar({ currentPath, children }: NavbarProps) {
  const pathname = usePathname();
  const activePath = currentPath || pathname || "";
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsLoggedIn(!!localStorage.getItem("token"));
    }
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    if (confirm("Are you sure you want to sign out?")) {
      api.logout();
    }
  };

  const logoHref = "/";

  const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/analyze", label: "New Audit", icon: Plus, highlight: true },
    { href: "/analyze/multi", label: "Multi-JD", icon: Layers },
    { href: "/history", label: "History", icon: History },
    { href: "/profile", label: "Profile", icon: User },
  ];

  return (
    <nav className="sticky top-0 z-40 w-full backdrop-blur-2xl bg-slate-950/85 border-b border-slate-800/80 transition-all">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link
          href={logoHref}
          className="flex items-center gap-2 sm:gap-2.5 group flex-shrink-0"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 via-indigo-500 to-fuchsia-500 flex items-center justify-center p-[1.5px] shadow-lg shadow-cyan-500/25 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-full flex items-center justify-center">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-fuchsia-300 font-black text-xs">
                CI
              </span>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-sm sm:text-base tracking-tight text-white group-hover:text-cyan-300 transition-colors">
              Career<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-indigo-400">Intel</span>
            </span>
            <span className="text-[8px] sm:text-[9px] text-cyan-400/90 font-mono tracking-widest uppercase -mt-0.5">
              AI ATS Intelligence
            </span>
          </div>
        </Link>

        {/* Center Nav Links (Desktop md+) */}
        {isLoggedIn && (
          <div className="hidden md:flex items-center gap-1.5 p-1 rounded-full bg-slate-900/90 border border-slate-800/90 shadow-inner">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = activePath === link.href || activePath.startsWith(link.href + "/");
              
              if (link.highlight) {
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition-all ${
                      isActive
                        ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/25"
                        : "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/25"
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{link.label}</span>
                  </Link>
                );
              }

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-slate-800 text-white shadow-sm border border-slate-700"
                      : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5 text-slate-400" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </div>
        )}

        {/* Right Actions & Hamburger */}
        <div className="flex items-center gap-1.5 sm:gap-3">
          {children}

          {/* Desktop Logout Button */}
          {isLoggedIn && (
            <button
              onClick={handleLogout}
              title="Sign out of your account"
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-slate-400 hover:text-rose-300 bg-slate-900/60 hover:bg-rose-500/10 border border-slate-800 hover:border-rose-500/30 transition-all group"
            >
              <LogOut className="w-3.5 h-3.5 group-hover:rotate-12 transition-transform text-slate-400 group-hover:text-rose-400" />
              <span>Sign Out</span>
            </button>
          )}

          {/* Mobile Hamburger Toggle (md:hidden) */}
          {isLoggedIn && (
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-slate-300 hover:text-white bg-slate-900/80 border border-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-400/50"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          )}
        </div>
      </div>

      {/* ── Mobile Navigation Drawer ── */}
      <AnimatePresence>
        {mobileMenuOpen && isLoggedIn && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="md:hidden border-b border-slate-800 bg-slate-950/95 backdrop-blur-2xl px-4 py-4 space-y-2 overflow-hidden shadow-2xl"
          >
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = activePath === link.href || activePath.startsWith(link.href + "/");
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between p-3 rounded-xl text-sm font-semibold transition-all ${
                    isActive
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                      : "text-slate-300 hover:bg-slate-900 hover:text-white border border-transparent"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                    <span>{link.label}</span>
                  </div>
                  {link.highlight && (
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-cyan-400 text-slate-950">
                      Audit
                    </span>
                  )}
                </Link>
              );
            })}

            <div className="pt-2 border-t border-slate-800/80">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="w-full flex items-center gap-3 p-3 rounded-xl text-sm font-semibold text-rose-300 hover:bg-rose-500/10 transition-colors"
              >
                <LogOut className="w-4 h-4 text-rose-400" />
                <span>Sign Out</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
