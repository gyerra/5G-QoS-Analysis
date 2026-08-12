"use client";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";
import { KPICard } from "@/components/KPICard";
import { ChartCard } from "@/components/ChartCard";
import { Database, Cpu, Layers, CheckCircle2, Server, Share2 } from "lucide-react";

interface BigDataResults {
  pyspark_version: string;
  dataset: {
    filename: string;
    total_records: number;
    total_columns: number;
    missing_values: number;
    duplicates_removed: number;
    high_quality_records: number;
    high_quality_pct: number;
  };
  overall_qos: {
    avg_download_mbps: number;
    avg_upload_mbps: number;
    avg_latency_ms: number;
    avg_jitter_ms: number;
    avg_signal_dbm: number;
    record_count: number;
  };
  carrier_aggregation: Array<{
    Carrier: string;
    avg_download: number;
    avg_upload: number;
    avg_latency: number;
    avg_jitter: number;
    avg_signal: number;
    record_count: number;
  }>;
  technology_aggregation: Array<{
    "Network Type": string;
    avg_download: number;
    avg_upload: number;
    avg_latency: number;
    avg_jitter: number;
    avg_signal: number;
    record_count: number;
  }>;
  dropped_connection_by_carrier: Array<{
    Carrier: string;
    drop_rate_pct: number;
    total: number;
  }>;
  big_data_concepts: {
    Volume: string;
    Velocity: string;
    Variety: string;
    Veracity: string;
    Value: string;
  };
  spark_pipeline_steps: string[];
}

const CARRIER_COLORS = ["#06b6d4", "#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"];

const PageHeader = ({ title, subtitle }: { title: string; subtitle: string }) => (
  <div style={{ marginBottom: "28px" }}>
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
      <div style={{ width: "3px", height: "24px", borderRadius: "2px", background: "linear-gradient(to bottom, #10b981, #06b6d4)" }} />
      <h1 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>{title}</h1>
    </div>
    <p style={{ fontSize: "13px", color: "var(--text-secondary)", paddingLeft: "13px" }}>{subtitle}</p>
  </div>
);

export default function BigDataPage() {
  const [data, setData] = useState<BigDataResults | null>(null);

  useEffect(() => {
    fetch("/data/bigdata_results.json")
      .then((r) => r.json())
      .then(setData)
      .catch((err) => console.error("Error loading bigdata_results.json", err));
  }, []);

  const vs = data?.big_data_concepts;

  return (
    <div>
      <PageHeader
        title="Big Data Processing — Apache PySpark"
        subtitle="Distributed DataFrame analysis, high-scale aggregations, and fundamental 5 V's of Big Data"
      />

      {data && (
        <>
          {/* Top KPI Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "24px" }}>
            <KPICard
              title="Processed Volume"
              value={data.dataset.total_records.toLocaleString()}
              unit="rows"
              icon={Database}
              color="cyan"
              subtitle={`${data.dataset.total_columns} columns distributed`}
            />
            <KPICard
              title="Engine / Framework"
              value={data.pyspark_version.includes("N/A") ? "PySpark" : `Spark ${data.pyspark_version}`}
              icon={Cpu}
              color="green"
              subtitle="Distributed DataFrames"
            />
            <KPICard
              title="High Quality Records"
              value={`${data.dataset.high_quality_pct}%`}
              unit={`(${data.dataset.high_quality_records.toLocaleString()})`}
              icon={CheckCircle2}
              color="blue"
              subtitle="Signal > -80dBm & Latency < 5ms"
            />
            <KPICard
              title="Deduplication"
              value={data.dataset.duplicates_removed}
              unit="dups"
              icon={Layers}
              color="violet"
              subtitle="Cleaned in distributed memory"
            />
          </div>

          {/* 5 V's of Big Data Section */}
          <div style={{ marginBottom: "24px" }}>
            <div style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Server size={18} color="var(--accent-green)" />
              The 5 V's of Big Data in 5G Telecom Networks
            </div>
            {vs && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "12px" }}>
                {[
                  { name: "Volume", text: vs.Volume, color: "#06b6d4" },
                  { name: "Velocity", text: vs.Velocity, color: "#3b82f6" },
                  { name: "Variety", text: vs.Variety, color: "#8b5cf6" },
                  { name: "Veracity", text: vs.Veracity, color: "#10b981" },
                  { name: "Value", text: vs.Value, color: "#f59e0b" },
                ].map((v) => (
                  <div className="card" key={v.name} style={{ display: "flex", flexDirection: "column" }}>
                    <div style={{ fontSize: "14px", fontWeight: 700, color: v.color, marginBottom: "8px" }}>
                      {v.name}
                    </div>
                    <p style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5, flex: 1 }}>
                      {v.text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Charts Row */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "24px" }}>
            <ChartCard
              title="PySpark Carrier Aggregation — Avg Download"
              subtitle="Calculated across distributed partitions"
              badge="PySpark GroupBy"
              badgeColor="green"
              height={280}
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.carrier_aggregation} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Average Download Speed (Mbps)", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <YAxis type="category" dataKey="Carrier" tick={{ fontSize: 11, fill: "#94a3b8" }} label={{ value: "Telecom Carrier", angle: -90, position: "insideLeft", offset: 10, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <Tooltip
                    contentStyle={{ background: "#0a1929", border: "1px solid rgba(16,185,129,0.3)", borderRadius: "8px" }}
                    labelStyle={{ color: "#e2e8f0", fontWeight: 600 }}
                    itemStyle={{ color: "#10b981" }}
                  />
                  <Bar dataKey="avg_download" radius={[0, 4, 4, 0]} name="Avg DL Speed (Mbps)">
                    {data.carrier_aggregation.map((_, i) => (
                      <Cell key={i} fill={CARRIER_COLORS[i % CARRIER_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard
              title="Dropped Connection Rate by Carrier (%)"
              subtitle="Distributed boolean aggregation (Veracity check)"
              badge="Drop Rate"
              badgeColor="amber"
              height={280}
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.dropped_connection_by_carrier} margin={{ top: 10, right: 20, bottom: 20, left: 15 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
                  <XAxis dataKey="Carrier" tick={{ fontSize: 11, fill: "#94a3b8" }} label={{ value: "Telecom Carrier", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <YAxis tick={{ fontSize: 10, fill: "#64748b" }} unit="%" label={{ value: "Dropped Connections (%)", angle: -90, position: "insideLeft", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <Tooltip
                    contentStyle={{ background: "#0a1929", border: "1px solid rgba(245,158,11,0.3)", borderRadius: "8px" }}
                    labelStyle={{ color: "#e2e8f0", fontWeight: 600 }}
                    itemStyle={{ color: "#f59e0b" }}
                  />
                  <Bar dataKey="drop_rate_pct" fill="#f59e0b" radius={[4, 4, 0, 0]} name="Drop Rate (%)" />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Spark Pipeline Execution Flow */}
          <div className="card">
            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Share2 size={16} color="var(--accent-cyan)" />
              PySpark Distributed Pipeline Steps (`big_data/big_data_analysis.py`)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "10px" }}>
              {data.spark_pipeline_steps.map((step, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "10px 12px",
                    background: "rgba(6,182,212,0.03)",
                    border: "1px solid rgba(6,182,212,0.15)",
                    borderRadius: "8px",
                    fontSize: "12px",
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  <span style={{ color: "var(--accent-cyan)", fontWeight: 700, marginRight: "6px" }}>
                    0{idx + 1}.
                  </span>
                  <span style={{ color: "var(--text-primary)" }}>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
