"use client";

import { LucideIcon } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: LucideIcon;
  color?: "cyan" | "blue" | "violet" | "green" | "amber";
  subtitle?: string;
  trend?: number; // positive = good
}

const COLOR_MAP = {
  cyan: { accent: "#06b6d4", glow: "rgba(6,182,212,0.15)", border: "rgba(6,182,212,0.25)", bg: "rgba(6,182,212,0.07)" },
  blue: { accent: "#3b82f6", glow: "rgba(59,130,246,0.15)", border: "rgba(59,130,246,0.25)", bg: "rgba(59,130,246,0.07)" },
  violet: { accent: "#8b5cf6", glow: "rgba(139,92,246,0.15)", border: "rgba(139,92,246,0.25)", bg: "rgba(139,92,246,0.07)" },
  green: { accent: "#10b981", glow: "rgba(16,185,129,0.15)", border: "rgba(16,185,129,0.25)", bg: "rgba(16,185,129,0.07)" },
  amber: { accent: "#f59e0b", glow: "rgba(245,158,11,0.15)", border: "rgba(245,158,11,0.25)", bg: "rgba(245,158,11,0.07)" },
};

export function KPICard({ title, value, unit, icon: Icon, color = "cyan", subtitle }: KPICardProps) {
  const c = COLOR_MAP[color];

  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: `1px solid ${c.border}`,
        borderRadius: "12px",
        padding: "20px",
        position: "relative",
        overflow: "hidden",
        transition: "box-shadow 0.2s, border-color 0.2s",
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.boxShadow = `0 0 24px ${c.glow}`;
        (e.currentTarget as HTMLElement).style.borderColor = c.accent;
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.boxShadow = "none";
        (e.currentTarget as HTMLElement).style.borderColor = c.border;
      }}
    >
      {/* Background glow orb */}
      <div
        style={{
          position: "absolute",
          top: "-20px",
          right: "-20px",
          width: "80px",
          height: "80px",
          borderRadius: "50%",
          background: c.glow,
          filter: "blur(20px)",
          pointerEvents: "none",
        }}
      />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
        <span style={{ fontSize: "12px", fontWeight: 500, color: "var(--text-secondary)", letterSpacing: "0.03em" }}>
          {title}
        </span>
        <div
          style={{
            width: "32px",
            height: "32px",
            borderRadius: "8px",
            background: c.bg,
            border: `1px solid ${c.border}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Icon size={16} color={c.accent} />
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: "4px" }}>
        <span
          style={{
            fontSize: "28px",
            fontWeight: 700,
            color: c.accent,
            lineHeight: 1,
            letterSpacing: "-0.02em",
            fontFamily: "'JetBrains Mono', monospace",
          }}
        >
          {typeof value === "number" ? value.toLocaleString() : value}
        </span>
        {unit && (
          <span style={{ fontSize: "13px", color: "var(--text-secondary)", fontWeight: 500 }}>
            {unit}
          </span>
        )}
      </div>

      {subtitle && (
        <div style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "6px" }}>
          {subtitle}
        </div>
      )}
    </div>
  );
}
