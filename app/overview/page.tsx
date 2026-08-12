"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, LineChart, Line,
} from "recharts";
import {
  Wifi, Download, Upload, Timer, Zap, Database, Server, TrendingUp,
} from "lucide-react";
import { KPICard } from "@/components/KPICard";
import { ChartCard } from "@/components/ChartCard";

// ---------- Types ----------
interface QosSummary {
  total_records: number;
  averages: {
    "Download Speed (Mbps)": number;
    "Upload Speed (Mbps)": number;
    "Latency (ms)": number;
    "Jitter (ms)": number;
    "Signal Strength (dBm)": number;
  };
  date_range: { start: string; end: string };
}

interface TemporalData {
  hourly: { labels: number[]; download_speed: number[]; latency: number[]; upload_speed: number[] };
  daily: { labels: string[]; download_speed: number[]; latency: number[] };
}

interface DatasetSummary {
  files: Array<{
    rows: number;
    columns: number;
    column_profiles: Array<{ column: string; dtype: string; missing_count: number }>;
  }>;
}

// ---------- Helpers ----------
const fnum = (v: number, d = 1) => v?.toFixed(d) ?? "—";

const PageHeader = ({ title, subtitle }: { title: string; subtitle: string }) => (
  <div style={{ marginBottom: "28px" }}>
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
      <div style={{
        width: "3px", height: "24px", borderRadius: "2px",
        background: "linear-gradient(to bottom, #06b6d4, #3b82f6)"
      }} />
      <h1 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>
        {title}
      </h1>
    </div>
    <p style={{ fontSize: "13px", color: "var(--text-secondary)", paddingLeft: "13px" }}>{subtitle}</p>
  </div>
);

const StatRow = ({ label, value }: { label: string; value: string | number }) => (
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 0", borderBottom: "1px solid rgba(6,182,212,0.06)" }}>
    <span style={{ fontSize: "13px", color: "var(--text-secondary)" }}>{label}</span>
    <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)", fontFamily: "'JetBrains Mono', monospace" }}>{value}</span>
  </div>
);

// ---------- Page ----------
export default function OverviewPage() {
  const [qos, setQos] = useState<QosSummary | null>(null);
  const [temporal, setTemporal] = useState<TemporalData | null>(null);
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [insights, setInsights] = useState<Array<{ category: string; title: string; value: string }>>([]);

  useEffect(() => {
    fetch("/data/qos_summary.json").then(r => r.json()).then(setQos);
    fetch("/data/temporal_analysis.json").then(r => r.json()).then(setTemporal);
    fetch("/data/dataset_summary.json").then(r => r.json()).then(setSummary);
    fetch("/data/insights.json").then(r => r.json()).then(d => setInsights(d.insights || []));
  }, []);

  const hourlyData = temporal
    ? temporal.hourly.labels.map((h, i) => ({
      hour: `${h}:00`,
      download: temporal.hourly.download_speed[i],
      latency: temporal.hourly.latency[i],
      upload: temporal.hourly.upload_speed[i],
    }))
    : [];

  const dailyData = temporal
    ? temporal.daily.labels.map((d, i) => ({
      day: d,
      download: temporal.daily.download_speed[i],
      latency: temporal.daily.latency[i],
    }))
    : [];

  const fileInfo = summary?.files?.[0];

  return (
    <div>
      <PageHeader
        title="5G QoS Overview"
        subtitle="Summary statistics and key performance indicators from 50,000 network measurement records"
      />

      {/* KPI Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "16px", marginBottom: "28px" }}>
        <KPICard
          title="Total Records"
          value={qos ? (qos.total_records / 1000).toFixed(0) + "K" : "—"}
          icon={Database}
          color="cyan"
          subtitle="Network measurements"
        />
        <KPICard
          title="Avg Download"
          value={qos ? fnum(qos.averages["Download Speed (Mbps)"]) : "—"}
          unit="Mbps"
          icon={Download}
          color="blue"
          subtitle="Mean across all records"
        />
        <KPICard
          title="Avg Upload"
          value={qos ? fnum(qos.averages["Upload Speed (Mbps)"]) : "—"}
          unit="Mbps"
          icon={Upload}
          color="violet"
          subtitle="Mean upload throughput"
        />
        <KPICard
          title="Avg Latency"
          value={qos ? fnum(qos.averages["Latency (ms)"]) : "—"}
          unit="ms"
          icon={Timer}
          color="green"
          subtitle="Round-trip time"
        />
        <KPICard
          title="Avg Signal"
          value={qos ? fnum(qos.averages["Signal Strength (dBm)"]) : "—"}
          unit="dBm"
          icon={Wifi}
          color="amber"
          subtitle="Received signal strength"
        />
      </div>

      {/* Charts Row 1 */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "16px", marginBottom: "16px" }}>
        <ChartCard title="Download Speed by Hour of Day" subtitle="Average throughput across 24-hour period" badge="Temporal" height={270}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={hourlyData} margin={{ top: 10, right: 20, bottom: 20, left: 15 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
              <XAxis dataKey="hour" tick={{ fontSize: 10, fill: "#64748b" }} interval={3} label={{ value: "Hour of Day (24h)", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
              <YAxis tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Speed (Mbps)", angle: -90, position: "insideLeft", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
              <Tooltip
                contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }}
                labelStyle={{ color: "#e2e8f0", fontWeight: 600 }}
                itemStyle={{ color: "#06b6d4" }}
              />
              <Line type="monotone" dataKey="download" stroke="#06b6d4" strokeWidth={2} dot={false} name="Download (Mbps)" />
              <Line type="monotone" dataKey="upload" stroke="#8b5cf6" strokeWidth={1.5} dot={false} name="Upload (Mbps)" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Latency by Day of Week" subtitle="Average latency per weekday" badge="QoS" badgeColor="green" height={270}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyData} margin={{ top: 10, right: 10, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
              <XAxis dataKey="day" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Day of Week", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
              <YAxis tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Latency (ms)", angle: -90, position: "insideLeft", offset: 0, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
              <Tooltip
                contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }}
                labelStyle={{ color: "#e2e8f0", fontWeight: 600 }}
                itemStyle={{ color: "#10b981" }}
              />
              <Bar dataKey="latency" fill="#10b981" radius={[4, 4, 0, 0]} name="Latency (ms)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Bottom Row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
        {/* Dataset info card */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
            <Server size={15} color="var(--accent-cyan)" />
            <span style={{ fontWeight: 600, fontSize: "14px" }}>Dataset Profile</span>
          </div>
          {fileInfo && (
            <>
              <StatRow label="File" value="5g_network_data.csv" />
              <StatRow label="Total Rows" value={fileInfo.rows.toLocaleString()} />
              <StatRow label="Columns" value={fileInfo.columns} />
              <StatRow label="Missing Values" value={fileInfo.column_profiles.reduce((a, c) => a + c.missing_count, 0)} />
              <StatRow label="Duplicate Rows" value={0} />
              <StatRow label="Date Range" value={qos ? `${qos.date_range.start.slice(0, 10)} → ${qos.date_range.end.slice(0, 10)}` : "—"} />
            </>
          )}
        </div>

        {/* Insights card */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px" }}>
            <TrendingUp size={15} color="var(--accent-cyan)" />
            <span style={{ fontWeight: 600, fontSize: "14px" }}>Key Insights</span>
          </div>
          {insights.slice(0, 6).map((ins, i) => (
            <div key={i} style={{ padding: "8px 0", borderBottom: "1px solid rgba(6,182,212,0.06)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "2px" }}>
                <span className={`badge badge-${["cyan", "blue", "violet", "green", "amber", "cyan"][i % 6]}`}>{ins.category}</span>
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>{ins.title}:</div>
              <div style={{ fontSize: "12px", color: "var(--text-primary)", fontWeight: 500, marginTop: "2px" }}>{ins.value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
