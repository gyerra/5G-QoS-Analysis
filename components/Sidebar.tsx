"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  LayoutDashboard,
  Activity,
  BrainCircuit,
  Database,
  Signal,
} from "lucide-react";

const NAV = [
  { href: "/overview", label: "Overview", icon: LayoutDashboard },
  { href: "/qos", label: "QoS Analysis", icon: Activity },
  { href: "/prediction", label: "Prediction", icon: BrainCircuit },
  { href: "/bigdata", label: "Big Data", icon: Database },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "240px",
        height: "100vh",
        background: "var(--bg-secondary)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        zIndex: 100,
        overflowY: "auto",
      }}
    >
      {/* Logo */}
      <div
        style={{
          padding: "24px 20px 20px",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
          <div
            style={{
              width: "34px",
              height: "34px",
              borderRadius: "8px",
              background: "linear-gradient(135deg, #06b6d4, #3b82f6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 14px rgba(6,182,212,0.4)",
            }}
          >
            <Signal size={18} color="#fff" />
          </div>
          <div>
            <div style={{ fontSize: "13px", fontWeight: 700, color: "var(--text-primary)", lineHeight: 1.2 }}>
              5G QoS
            </div>
            <div style={{ fontSize: "11px", color: "var(--text-secondary)", lineHeight: 1.2 }}>
              Analysis Dashboard
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "10px" }}>
          <div
            style={{
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              background: "var(--accent-green)",
              boxShadow: "0 0 6px var(--accent-green)",
              animation: "pulse 2s infinite",
            }}
          />
          <span style={{ fontSize: "11px", color: "var(--accent-green)", fontWeight: 500 }}>
            50,000 Records Loaded
          </span>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "16px 12px" }}>
        <div style={{ marginBottom: "8px" }}>
          <span style={{ fontSize: "10px", fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase", paddingLeft: "8px" }}>
            Navigation
          </span>
        </div>
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`sidebar-link ${active ? "sidebar-link-active" : ""}`}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                padding: "10px 12px",
                borderRadius: "8px",
                marginBottom: "4px",
                fontSize: "14px",
                fontWeight: active ? 600 : 400,
                color: active ? "var(--accent-cyan)" : "var(--text-secondary)",
                background: active ? "rgba(6,182,212,0.08)" : "transparent",
                border: `1px solid ${active ? "rgba(6,182,212,0.2)" : "transparent"}`,
                textDecoration: "none",
                transition: "all 0.15s ease",
              }}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div
        style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border)",
          fontSize: "11px",
          color: "var(--text-muted)",
        }}
      >
        <div style={{ marginBottom: "4px" }}>Academic Project</div>
        <div>Data Analysis & Big Data</div>
        <div style={{ marginTop: "4px", color: "var(--accent-cyan)", fontWeight: 500 }}>
          5G / Mobile Networks
        </div>
      </div>
    </aside>
  );
}
