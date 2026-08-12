"use client";

import { useEffect, useState } from "react";
import {
  ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  BarChart, Bar, Cell,
} from "recharts";
import { KPICard } from "@/components/KPICard";
import { ChartCard } from "@/components/ChartCard";
import { BrainCircuit, AlertCircle } from "lucide-react";

interface ModelMetrics {
  model: string;
  MAE: number;
  RMSE: number;
  R2: number;
}

interface ModelComparison {
  target: string;
  best_model: string;
  best_metrics: ModelMetrics & { model: string };
  comparison: ModelMetrics[];
  feature_importance: Array<{ feature: string; importance: number }>;
  prediction_chart: { actual: number[]; predicted: number[] };
  train_size?: number;
  test_size?: number;
}

const PageHeader = ({ title, subtitle }: { title: string; subtitle: string }) => (
  <div style={{ marginBottom: "28px" }}>
    <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
      <div style={{ width: "3px", height: "24px", borderRadius: "2px", background: "linear-gradient(to bottom, #8b5cf6, #3b82f6)" }} />
      <h1 style={{ fontSize: "22px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.02em" }}>{title}</h1>
    </div>
    <p style={{ fontSize: "13px", color: "var(--text-secondary)", paddingLeft: "13px" }}>{subtitle}</p>
  </div>
);

const MetricBadge = ({ label, value, color }: { label: string; value: string | number; color: string }) => (
  <div style={{ textAlign: "center", padding: "12px 16px", background: "rgba(0,0,0,0.2)", borderRadius: "8px", border: "1px solid var(--border)" }}>
    <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginBottom: "4px", letterSpacing: "0.05em", textTransform: "uppercase" }}>{label}</div>
    <div style={{ fontSize: "22px", fontWeight: 700, color, fontFamily: "'JetBrains Mono', monospace" }}>{value}</div>
  </div>
);

export default function PredictionPage() {
  const [models, setModels] = useState<Record<string, ModelComparison>>({});
  const [activeTarget, setActiveTarget] = useState<string>("Download Speed (Mbps)");

  useEffect(() => {
    fetch("/data/model_comparison.json").then(r => r.json()).then(data => {
      setModels(data);
    });
  }, []);

  const m = models[activeTarget];
  const targets = Object.keys(models);

  // Scatter data: actual vs predicted (sample)
  const scatterData = m?.prediction_chart
    ? m.prediction_chart.actual.map((a, i) => ({ actual: a, predicted: m.prediction_chart.predicted[i] }))
    : [];

  // Feature importance data
  const fiData = m?.feature_importance?.slice(0, 10) ?? [];

  // Model comparison bar data
  const compData = m?.comparison?.map(c => ({ name: c.model.replace("Gradient Boosting", "GradBoost").replace("Random Forest", "RF"), MAE: c.MAE, R2: Math.max(c.R2, -0.2) })) ?? [];

  return (
    <div>
      <PageHeader
        title="Machine Learning Prediction"
        subtitle="QoS parameter prediction using regression models — evaluated with MAE, RMSE, and R²"
      />

      {/* Target selector */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "24px" }}>
        {targets.map(t => {
          const active = t === activeTarget;
          return (
            <button
              key={t}
              onClick={() => setActiveTarget(t)}
              style={{
                padding: "8px 18px",
                borderRadius: "8px",
                fontSize: "13px",
                fontWeight: 500,
                cursor: "pointer",
                border: `1px solid ${active ? "rgba(139,92,246,0.4)" : "var(--border)"}`,
                background: active ? "rgba(139,92,246,0.1)" : "transparent",
                color: active ? "var(--accent-violet)" : "var(--text-secondary)",
                transition: "all 0.15s",
              }}
            >
              Predict: {t}
            </button>
          );
        })}
      </div>

      {m && (
        <>
          {/* Best model banner */}
          <div style={{ background: "linear-gradient(135deg, rgba(139,92,246,0.08), rgba(59,130,246,0.08))", border: "1px solid rgba(139,92,246,0.2)", borderRadius: "12px", padding: "16px 20px", marginBottom: "20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                <BrainCircuit size={16} color="var(--accent-violet)" />
                <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--text-primary)" }}>Best Model: {m.best_model}</span>
              </div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                Target: <strong style={{ color: "var(--accent-violet)" }}>{activeTarget}</strong> &nbsp;·&nbsp;
                Split: Chronological 80/20 &nbsp;·&nbsp;
                Training samples: {m.train_size?.toLocaleString() ?? "40,000"} &nbsp;·&nbsp;
                Test samples: {m.test_size?.toLocaleString() ?? "10,000"}
              </div>
            </div>
            <div style={{ display: "flex", gap: "12px" }}>
              <MetricBadge label="MAE" value={m.best_metrics.MAE} color="#06b6d4" />
              <MetricBadge label="RMSE" value={m.best_metrics.RMSE} color="#3b82f6" />
              <MetricBadge label="R²" value={m.best_metrics.R2} color="#8b5cf6" />
            </div>
          </div>

          {/* Metric explanations */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px", marginBottom: "20px" }}>
            <div className="card">
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--accent-cyan)", marginBottom: "4px" }}>MAE = {m.best_metrics.MAE}</div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                <strong>Mean Absolute Error.</strong> On average, the model prediction differs from the actual value by {m.best_metrics.MAE} units.
              </div>
            </div>
            <div className="card">
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--accent-blue)", marginBottom: "4px" }}>RMSE = {m.best_metrics.RMSE}</div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                <strong>Root Mean Square Error.</strong> Penalises large errors more heavily. Higher than MAE when large deviations exist.
              </div>
            </div>
            <div className="card">
              <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--accent-violet)", marginBottom: "4px" }}>R² = {m.best_metrics.R2}</div>
              <div style={{ fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                <strong>R-squared.</strong> Measures how well the model explains variation in the target. R²≈0 means the selected features do not linearly predict {activeTarget}.
              </div>
            </div>
          </div>

          {/* R² note */}
          {Math.abs(m.best_metrics.R2) < 0.1 && (
            <div style={{ padding: "12px 16px", background: "rgba(245,158,11,0.07)", border: "1px solid rgba(245,158,11,0.2)", borderRadius: "8px", marginBottom: "20px", display: "flex", gap: "10px", alignItems: "flex-start" }}>
              <AlertCircle size={15} color="#f59e0b" style={{ marginTop: "1px", flexShrink: 0 }} />
              <p style={{ fontSize: "12px", color: "#f59e0b", lineHeight: 1.5 }}>
                <strong>Dataset Note:</strong> All model R² values are near 0 for this target. This is consistent with synthetically generated data where QoS metrics are independently randomised. In real network data, signal strength, congestion level, and handover count would show stronger predictive relationships.
              </p>
            </div>
          )}

          {/* Charts row */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>
            <ChartCard title="Actual vs Predicted" subtitle="Sample of 500 test set predictions vs ground truth" badge="Test Set" badgeColor="violet" height={280}>
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 15 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
                  <XAxis dataKey="actual" name="Actual" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: `Actual ${activeTarget}`, position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <YAxis dataKey="predicted" name="Predicted" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: `Predicted ${activeTarget}`, angle: -90, position: "insideLeft", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <Tooltip cursor={{ strokeDasharray: "3 3" }} contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} labelStyle={{ color: "#e2e8f0" }} />
                  <Scatter data={scatterData} fill="#06b6d4" opacity={0.4} />
                </ScatterChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Feature Importance" subtitle="Top 10 features ranked by model weight / importance" badge="Features" badgeColor="blue" height={280}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={fiData} layout="vertical" margin={{ left: 10, right: 20, top: 10, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#64748b" }} label={{ value: "Feature Importance Score", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <YAxis type="category" dataKey="feature" tick={{ fontSize: 10, fill: "#94a3b8" }} width={100} label={{ value: "Feature Name", angle: -90, position: "insideLeft", offset: 10, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                  <Tooltip contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} itemStyle={{ color: "#3b82f6" }} labelStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                  <Bar dataKey="importance" radius={[0, 4, 4, 0]} name="Importance">
                    {fiData.map((_, i) => <Cell key={i} fill={`hsl(${200 + i * 15}, 70%, 55%)`} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* All model comparison */}
          <ChartCard title="All Models Comparison — MAE" subtitle="Lower MAE = better average prediction accuracy" badge="Model Selection" height={250}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={compData} margin={{ top: 10, right: 20, bottom: 20, left: 15 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(6,182,212,0.06)" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#94a3b8" }} label={{ value: "Machine Learning Regression Model", position: "insideBottom", offset: -12, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <YAxis tick={{ fontSize: 10, fill: "#64748b" }} domain={[0, 'dataMax + 10']} label={{ value: "Mean Absolute Error (MAE)", angle: -90, position: "insideLeft", offset: -5, fill: "#94a3b8", fontSize: 11, fontWeight: 500 }} />
                <Tooltip contentStyle={{ background: "#0a1929", border: "1px solid rgba(6,182,212,0.3)", borderRadius: "8px" }} labelStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                <Bar dataKey="MAE" radius={[6, 6, 0, 0]} name="MAE">
                  {compData.map((entry, i) => (
                    <Cell key={i} fill={entry.name === m.best_model.replace("Gradient Boosting", "GradBoost").replace("Random Forest", "RF") ? "#06b6d4" : "#1e3a5f"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Full comparison table */}
          <div className="card" style={{ marginTop: "16px" }}>
            <div style={{ fontWeight: 600, fontSize: "14px", marginBottom: "14px" }}>Complete Model Comparison Table</div>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
              <thead>
                <tr>
                  {["Model", "MAE", "RMSE", "R²", "Selection"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-secondary)", fontWeight: 500, borderBottom: "1px solid var(--border)" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {m.comparison.map(c => (
                  <tr key={c.model} style={{
                    borderBottom: "1px solid rgba(6,182,212,0.04)",
                    background: c.model === m.best_model ? "rgba(6,182,212,0.04)" : "transparent",
                  }}>
                    <td style={{ padding: "8px 12px", fontWeight: c.model === m.best_model ? 600 : 400, color: c.model === m.best_model ? "var(--accent-cyan)" : "var(--text-primary)" }}>{c.model}</td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{c.MAE}</td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{c.RMSE}</td>
                    <td style={{ padding: "8px 12px", fontFamily: "monospace" }}>{c.R2}</td>
                    <td style={{ padding: "8px 12px" }}>
                      {c.model === m.best_model && <span className="badge badge-cyan">Best</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
