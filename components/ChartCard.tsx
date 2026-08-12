"use client";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  badge?: string;
  badgeColor?: "cyan" | "blue" | "violet" | "green" | "amber";
  height?: number;
}

const BADGE_COLORS = {
  cyan:   { bg: "rgba(6,182,212,0.12)",  color: "#06b6d4", border: "rgba(6,182,212,0.25)" },
  blue:   { bg: "rgba(59,130,246,0.12)", color: "#3b82f6", border: "rgba(59,130,246,0.25)" },
  violet: { bg: "rgba(139,92,246,0.12)", color: "#8b5cf6", border: "rgba(139,92,246,0.25)" },
  green:  { bg: "rgba(16,185,129,0.12)", color: "#10b981", border: "rgba(16,185,129,0.25)" },
  amber:  { bg: "rgba(245,158,11,0.12)", color: "#f59e0b", border: "rgba(245,158,11,0.25)" },
};

export function ChartCard({ title, subtitle, children, badge, badgeColor = "cyan", height = 280 }: ChartCardProps) {
  const bc = BADGE_COLORS[badgeColor];

  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--border)",
        borderRadius: "12px",
        padding: "20px",
        transition: "border-color 0.2s",
      }}
      onMouseEnter={e => (e.currentTarget as HTMLElement).style.borderColor = "var(--border-bright)"}
      onMouseLeave={e => (e.currentTarget as HTMLElement).style.borderColor = "var(--border)"}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "16px" }}>
        <div>
          <div style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>{title}</div>
          {subtitle && (
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "2px" }}>{subtitle}</div>
          )}
        </div>
        {badge && (
          <span
            style={{
              fontSize: "10px",
              fontWeight: 600,
              padding: "3px 8px",
              borderRadius: "20px",
              background: bc.bg,
              color: bc.color,
              border: `1px solid ${bc.border}`,
              letterSpacing: "0.05em",
              textTransform: "uppercase",
              whiteSpace: "nowrap",
            }}
          >
            {badge}
          </span>
        )}
      </div>
      <div style={{ height: `${height}px` }}>{children}</div>
    </div>
  );
}
