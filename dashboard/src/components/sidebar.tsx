"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Analiticas", icon: "📊" },
  { href: "/leads", label: "Leads", icon: "👥" },
  { href: "/llamadas", label: "Llamadas", icon: "📞" },
  { href: "/configuracion", label: "Configuracion", icon: "⚙️" },
];

/**
 * Sidebar reads branding from data attributes set on <body> by the server layout,
 * but since these are static values we pass them via env at build time.
 * For simplicity, we read from env vars available at build.
 */

const agentName = process.env.NEXT_PUBLIC_AGENT_NAME || "Sofia";
const logoText = process.env.NEXT_PUBLIC_LOGO_TEXT || agentName;
const businessName = process.env.NEXT_PUBLIC_BUSINESS_NAME || "";
const brandColor = process.env.NEXT_PUBLIC_BRAND_COLOR || "#06b6d4";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-white/[0.06] bg-neutral-950">
      {/* Logo */}
      <div className="flex h-20 items-center gap-3 px-6 border-b border-white/[0.06]">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl text-lg font-bold text-black"
          style={{ background: `linear-gradient(135deg, ${brandColor}, ${brandColor}dd)` }}
        >
          {agentName.charAt(0)}
        </div>
        <div>
          <p className="font-heading text-lg font-semibold italic tracking-tight">
            {logoText}
          </p>
          <p className="text-[11px] uppercase tracking-[0.2em] text-neutral-500">
            Voice Agent
          </p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {nav.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                active
                  ? "bg-white/[0.08] text-white"
                  : "text-neutral-400 hover:bg-white/[0.04] hover:text-neutral-200"
              )}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/[0.06] px-6 py-4">
        <p className="text-[11px] text-neutral-600">{businessName}</p>
        <p className="text-[10px] text-neutral-700 mt-0.5">
          Powered by Horizontes IA
        </p>
      </div>
    </aside>
  );
}
