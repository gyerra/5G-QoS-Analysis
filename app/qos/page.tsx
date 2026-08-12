"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  LineChart, Line, Legend, Cell,
} from "recharts";
import { ChartCard } from "@/components/ChartCard";
import { KPICard } from "@/components/KPICard";
import { Wifi, Timer, Download, Upload, Zap, Signal } from "lucide-react";

interface CarrierRow { Carrier: string; "Download Speed (Mbps)": number; "Upload Speed (Mbps)": number; "Latency (ms)": number; "Jitter (ms)": number; "Signal Strength (dBm)": number; }
interface TechRow { "Network Type": string; "Download Speed (Mbps)": number; "Upload Speed (Mbps)": number; "Latency (ms)": number; "Jitter (ms)": number; "Signal Strength (dBm)"?: number; }
interface TemporalData { hourly: { labels: number[]; download_speed: number[]; latency: number[]; jitter: number[]; signal_strength: number[] }; }
interface CorrData { columns: string[]; pearson: Record<string, Record<string, number>>; }

const CARRIER_COLORS = ["#06b6d4", "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"];
const TECH_COLORS = { "4G": "#f59e0b", "5G NSA": "#3b82f6", "5G SA": "#06b6d4" };

const fnum = (v?: number | null, d = 2) => (v != null ? v.toFixed(d) : "—");

const PageHeader = ({ title, subtitle }: { title: string; subtitle: string }) => (
  <div style={{ marginBottom: "28px" }}>
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
      <div style={{ width: "3px", height: "24px", borderRadius: "2px", background: "linear-gradient(to bottom, #06b6d4, #3b82f6)" }} />
      <h1 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>{title}</h1>
    </div>
    <p style={{ fontSize: "13px", color: "var(--text-secondary)", paddingLeft: "13px" }}>{subtitle}</p>
  </div>
);

export default function QoSPage() {
  const [carriers, setCarriers] = useState<CarrierRow[]>([]);
  const [tech, setTech] = useState<TechRow[]>([]);
  const [temporal, setTemporal] = useState<TemporalData | null>(null);
  const [corr, setCorr] = useState<CorrData | null>(null);
  const [tab, setTab] = useState<"carrier" | "technology" | "temporal">("carrier");

  useEffect(() => {
    fetch("/data/carrier_analysis.json").then(r => r.json()).then(setCarriers);
    fetch("/data/technology_analysis.json").then(r => r.json()).then(setTech);
    fetch("/data/temporal_analysis.json").then(r => r.json()).then(setTemporal);
    fetch("/data/correlations.json").then(r => r.json()).then(setCorr);
  }, []);

  const hourlyData = temporal
    ? temporal.hourly.labels.map((h, i) => ({
        hour: `${h}h`,
        download: temporal.hourly.download_speed[i],
        latency: temporal.hourly.latency[i],
        jitter: temporal.hourly.jitter[i],
      }))
    : [];

  // Correlation heatmap data
  const corrCols = corr?.columns ?? [];

  const colShortName = (c: string) =>
    c.replace("Download Speed (Mbps)", "DL")
     .replace("Upload Speed (Mbps)", "UL")
     .replace("Latency (ms)", "Latency")
     .replace("Jitter (ms)", "Jitter")
     .replace("Signal Strength (dBm)", "Signal")
     .replace("Ping to Google (ms)", "Ping");

  const tabStyle = (active: boolean) => ({
    padding: "7px 16px",
    borderRadius: "6px",
    fontSize: "13px",
    fontWeight: 500,
    cursor: "pointer",
    border: "1px solid",
    borderColor: active ? "rgba(6,182,212,0.4)" : "transparent",
    background: active ? "rgba(6,182,212,0.08)" : "transparent",
    color: active ? "var(--accent-cyan)" : "var(--text-secondary)",
    transition: "all 0.15s",
  });

  return (
    <div>
      <PageHeader title="QoS Analysis" subtitle="Network quality comparison by carrier, technology, and temporal patterns" />

      {/* KPI summary row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "24px" }}>
        <KPICard title="Carriers Compared" value={carriers.length} icon={Wifi} color="cyan" subtitle="AT&T, Airtel, BSNL, Jio, T-Mobile, Verizon, Vi" />
        <KPICard title="Network Types" value={tech.length} icon={Signal} color="blue" subtitle="4G, 5G NSA, 5G SA" />
        <KPICard title="Locations" value={8} icon={Zap} color="violet" subtitle="City-level measurement areas" />
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
        {(["carrier", "technology", "temporal"] as const).map(t => (
          <button key={t} style={tabStyle(tab === t)} onClick={() => setTab(t)}>
            {t === "carrier" ? "By Carrier" : t === "technology" ? "By Network Type" : "Temporal Trends"}
          </button>
        ))}
      </div>

      {/* Carrier Tab */}
      {tab === "carrier" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <ChartCard title="Avg Download Speed by Carrier" subtitle="Mean Mbps grouped by operator" badge="Download" height={280}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={carriers} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Average Download Speed (Mbps)", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <YAxis type="category" dataKey="Carrier" tick={{ fontSize: 11, fill: "#94a3b8" }} label={{ value: "Telecom Carrier", angle: -90, position: "insideLeft", offset: 10, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <Tooltip contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} itemStyle={{ color: "#06b6d4" }} labelStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                <Bar dataKey="Download Speed (Mbps)" radius={[0, 4, 4, 0]} name="Download (Mbps)">
                  {carriers.map((_, i) => <Cell key={i} fill={CARRIER_COLORS[i % CARRIER_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Avg Latency by Carrier" subtitle="Lower is better — mean ms per operator" badge="Latency" badgeColor="green" height={280}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={carriers} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#64748b" }} domain={[0, 'dataMax + 2']} label={{ value: "Average Latency (ms)", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <YAxis type="category" dataKey="Carrier" tick={{ fontSize: 11, fill: "#94a3b8" }} label={{ value: "Telecom Carrier", angle: -90, position: "insideLeft", offset: 10, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <Tooltip contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} itemStyle={{ color: "#10b981" }} labelStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                <Bar dataKey="Latency (ms)" radius={[0, 4, 4, 0]} name="Latency (ms)">
                  {carriers.map((_, i) => <Cell key={i} fill={CARRIER_COLORS[i % CARRIER_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Carrier table */}
          <div className="card" style={{ gridColumn: "1 / -1" }}>
            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "14px" }}>Carrier Performance Summary Table</div>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
                <thead>
                  <tr>
                    {["Carrier", "DL Speed (Mbps)", "UL Speed (Mbps)", "Latency (ms)", "Jitter (ms)", "Signal (dBm)"].map(h => (
                      <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-secondary)", fontWeight: 500, borderBottom: "1px solid var(--border)" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {carriers.map((c, i) => (
                    <tr key={c.Carrier} style={{ borderBottom: "1px solid rgba(6,182,212,0.04)" }}>
                      <td style={{ padding: "8px 12px" }}>
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
                          <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: CARRIER_COLORS[i % CARRIER_COLORS.length], display: "inline-block" }} />
                          <b>{c.Carrier}</b>
                        </span>
                      </td>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#06b6d4" }}>{fnum(c["Download Speed (Mbps)"])}</td>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#8b5cf6" }}>{fnum(c["Upload Speed (Mbps)"])}</td>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#10b981" }}>{fnum(c["Latency (ms)"])}</td>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{fnum(c["Jitter (ms)"])}</td>
                      <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{fnum(c["Signal Strength (dBm)"])}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Technology Tab */}
      {tab === "technology" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
          <ChartCard title="Download Speed by Network Type" subtitle="4G vs 5G NSA vs 5G SA comparison" badge="Network Type" height={280}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tech} margin={{ top: 10, right: 20, bottom: 20, left: 15 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
                <XAxis dataKey="Network Type" tick={{ fontSize: 12, fill: "#94a3b8" }} label={{ value: "Network Generation / Technology", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <YAxis tick={{ fontSize: 10, fill: "#64748b" }} domain={[0, 'dataMax + 50']} label={{ value: "Average Download (Mbps)", angle: -90, position: "insideLeft", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <Tooltip contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} labelStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                <Bar dataKey="Download Speed (Mbps)" radius={[6, 6, 0, 0]} name="Download (Mbps)">
                  {tech.map(row => <Cell key={row["Network Type"]} fill={(TECH_COLORS as Record<string, string>)[row["Network Type"]] || "#06b6d4"} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Multi-Metric Comparison by Network Type" subtitle="Upload, Latency, Jitter across generations" badge="Multi-Metric" badgeColor="violet" height={280}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tech} margin={{ top: 10, right: 20, bottom: 20, left: 15 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
                <XAxis dataKey="Network Type" tick={{ fontSize: 12, fill: "#94a3b8" }} label={{ value: "Network Generation / Technology", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <YAxis tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Metric Value (Mbps / ms)", angle: -90, position: "insideLeft", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <Tooltip contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} labelStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                <Legend wrapperStyle={{ fontSize: "11px", color: "#64748b" }} />
                <Bar dataKey="Upload Speed (Mbps)" fill="#8b5cf6" radius={[3, 3, 0, 0]} name="Upload (Mbps)" />
                <Bar dataKey="Latency (ms)" fill="#10b981" radius={[3, 3, 0, 0]} name="Latency (ms)" />
                <Bar dataKey="Jitter (ms)" fill="#f59e0b" radius={[3, 3, 0, 0]} name="Jitter (ms)" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <div className="card" style={{ gridColumn: "1 / -1" }}>
            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "14px" }}>Network Technology Performance Table</div>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
              <thead>
                <tr>
                  {["Network Type", "DL Speed (Mbps)", "UL Speed (Mbps)", "Latency (ms)", "Jitter (ms)", "Signal (dBm)"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-secondary)", fontWeight: 500, borderBottom: "1px solid var(--border)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tech.map(row => (
                  <tr key={row["Network Type"]} style={{ borderBottom: "1px solid rgba(6,182,212,0.04)" }}>
                    <td style={{ padding: "8px 12px" }}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: "6px" }}>
                        <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: (TECH_COLORS as Record<string, string>)[row["Network Type"]] || "#06b6d4", display: "inline-block" }} />
                        <b>{row["Network Type"]}</b>
                      </span>
                    </td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#06b6d4" }}>{fnum(row["Download Speed (Mbps)"])}</td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#8b5cf6" }}>{fnum(row["Upload Speed (Mbps)"])}</td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace", color: "#10b981" }}>{fnum(row["Latency (ms)"])}</td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{fnum(row["Jitter (ms)"])}</td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{fnum(row["Signal Strength (dBm)"])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Temporal Tab */}
      {tab === "temporal" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "16px" }}>
          <ChartCard title="Hourly Download & Latency Trends" subtitle="Average QoS metrics across 24 hours" badge="24-Hour" height={300}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourlyData} margin={{ top: 10, right: 30, bottom: 20, left: 15 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
                <XAxis dataKey="hour" tick={{ fontSize: 10, fill: "#64748b" }} interval={2} label={{ value: "Hour of Day (24-Hour Clock)", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <YAxis yAxisId="dl" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Speed / Jitter (Mbps / ms)", angle: -90, position: "insideLeft", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <YAxis yAxisId="lat" orientation="right" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Latency (ms)", angle: 90, position: "insideRight", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <Tooltip contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} labelStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                <Legend wrapperStyle={{ fontSize: "11px", color: "#64748b" }} />
                <Line yAxisId="dl" type="monotone" dataKey="download" stroke="#06b6d4" strokeWidth={2} dot={false} name="Download (Mbps)" />
                <Line yAxisId="dl" type="monotone" dataKey="jitter" stroke="#8b5cf6" strokeWidth={1.5} dot={false} name="Jitter (ms)" />
                <Line yAxisId="lat" type="monotone" dataKey="latency" stroke="#10b981" strokeWidth={1.5} dot={false} name="Latency (ms)" />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Correlation Heatmap (text-based) */}
          <div className="card">
            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "4px" }}>QoS Correlation Heatmap</div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginBottom: "14px" }}>
              Pearson correlation between numerical QoS metrics. Values near 0 indicate low linear dependency — characteristic of this dataset.
            </div>
            {corr && (
              <div style={{ overflowX: "auto" }}>
                <table style={{ borderCollapse: "collapse", fontSize: "12px", margin: "0 auto" }}>
                  <thead>
                    <tr>
                      <th style={{ padding: "6px 10px", color: "var(--text-muted)", fontWeight: 400 }}></th>
                      {corrCols.map(c => (
                        <th key={c} style={{ padding: "6px 8px", color: "var(--text-secondary)", fontWeight: 500, fontSize: "11px", textAlign: "center", whiteSpace: "nowrap" }}>
                          {colShortName(c)}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {corrCols.map(c1 => (
                      <tr key={c1}>
                        <td style={{ padding: "6px 10px", color: "var(--text-secondary)", fontWeight: 500, fontSize: "11px", whiteSpace: "nowrap" }}>
                          {colShortName(c1)}
                        </td>
                        {corrCols.map(c2 => {
                          const r = corr.pearson[c1]?.[c2] ?? 0;
                          const abs = Math.abs(r);
                          const bg = c1 === c2
                            ? "rgba(6,182,212,0.3)"
                            : abs > 0.3 ? `rgba(6,182,212,${abs * 0.7})` : `rgba(59,130,246,${abs * 0.3 + 0.03})`;
                          const textColor = c1 === c2 ? "#06b6d4" : abs > 0.1 ? "#e2e8f0" : "#64748b";
                          return (
                            <td key={c2} style={{ padding: "8px", textAlign: "center", background: bg, borderRadius: "4px", margin: "2px", fontFamily: "monospace", fontSize: "11px", color: textColor }}>
                              {r.toFixed(3)}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <div style={{ marginTop: "12px", padding: "10px 14px", background: "rgba(245,158,11,0.07)", border: "1px solid rgba(245,158,11,0.2)", borderRadius: "8px" }}>
              <p style={{ fontSize: "12px", color: "#f59e0b" }}>
                <strong>Note:</strong> All Pearson r values are near 0, indicating very low linear correlation between QoS features. This is consistent with synthetically generated datasets where features are independently randomized.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
