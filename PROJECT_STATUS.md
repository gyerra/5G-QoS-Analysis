# 5G QoS Analysis Dashboard — Project Status

> **Audited:** 2026-08-12

---

## Component Status Table

| Component | Status | Existing Files | What Needs To Be Done |
|---|---|---|---|
| **Dataset** | ✅ Complete | `5g_network_data.csv` (50,000 rows × 21 cols) | Nothing — dataset is ready |
| **Data Loading** | ✅ Complete | `python/load_data.py`, raw copy in `python/data/raw/` | Nothing |
| **Data Cleaning** | ✅ Complete | `python/preprocessing/clean_data.py`, `python/data/processed/cleaned_dataset.csv` | Nothing |
| **EDA** | ✅ Complete | `python/visualization/eda.py`, 14 plots in `python/output/plots/` | Nothing |
| **Statistics** | ✅ Complete | `python/statistical_analysis.py`, `descriptive_statistics.json`, `correlations.json` | Nothing |
| **QoS Analysis** | ✅ Complete | `python/qos_analysis.py`, carrier/technology/location/temporal JSON outputs | Nothing |
| **Machine Learning** | ✅ Complete (exceeds spec) | `python/ml/train_model.py`, 5 models trained, best selected | Dashboard should highlight LR results |
| **Output Generation** | ✅ Complete | `python/generate_outputs.py`, all JSONs + plots copied to `public/` | Nothing |
| **Pipeline Runner** | ✅ Complete | `python/run_pipeline.py` | Nothing |
| **Big Data (PySpark)** | ❌ Missing | — | Create `big_data/big_data_analysis.py` |
| **Dashboard (Frontend)** | ❌ Missing | `package.json` + config files only — no `app/` directory | Build entire Next.js dashboard |
| **README** | ❌ Missing | — | Create `README.md` |

---

## Dataset Summary

| Property | Value |
|---|---|
| File | `5g_network_data.csv` |
| Rows | **50,000** |
| Columns | **21** |
| Duplicates | **0** |
| Missing Values | **None** |
| Date Range | June 2024 – May 2025 |

### All 21 Columns

| Column | Type | QoS Role |
|---|---|---|
| Timestamp | datetime | timestamp |
| Location | categorical (8 cities) | location |
| Signal Strength (dBm) | float64 | signal_strength |
| Download Speed (Mbps) | float64 | download_speed |
| Upload Speed (Mbps) | float64 | upload_speed |
| Latency (ms) | float64 | latency |
| Jitter (ms) | float64 | jitter |
| Network Type | categorical (4G, 5G NSA, 5G SA) | network_technology |
| Device Model | categorical (5 devices) | — |
| Carrier | categorical (7: AT&T, Airtel, BSNL, Jio, T-Mobile, Verizon, Vi) | carrier |
| Band | categorical (5 bands) | — |
| Battery Level (%) | int64 | — |
| Temperature (°C) | float64 | — |
| Connected Duration (min) | int64 | — |
| Handover Count | int64 | — |
| Data Usage (MB) | float64 | — |
| Video Streaming Quality | int64 | — |
| VoNR Enabled | bool | — |
| Network Congestion Level | categorical (Low/Medium/High) | — |
| Ping to Google (ms) | float64 | — |
| Dropped Connection | bool | dropped_connection |

### QoS Availability
- ✅ Download Speed, Upload Speed, Latency, Jitter, Signal Strength, Network Type, Carrier, Location, Timestamp
- ❌ Packet Loss % — only boolean `Dropped Connection` available
- ❌ GPS coordinates — city-level Location string only

---

## What Is Already Working

### Python Pipeline — Fully Functional
All 7 steps run end-to-end via `python run_pipeline.py`:

1. **`load_data.py`** — discovers CSV, copies to raw/, loads DataFrame
2. **`preprocessing/clean_data.py`** — timestamp parsing, missing value handling (median/mode), IQR outlier detection (retained), label encoding
3. **`statistical_analysis.py`** — descriptive stats (mean/median/min/max/std), Pearson + Spearman correlation
4. **`qos_analysis.py`** — grouped means by carrier, network type, location; hourly/daily/monthly temporal analysis
5. **`visualization/eda.py`** — histograms, box plots, KDE, scatter plots, correlation heatmap → 14 PNGs
6. **`ml/train_model.py`** — 5 models (LR, DT, RF, GB, XGB) trained for Download Speed + Latency
7. **`generate_outputs.py`** — copies all JSON results + plots to `public/data/` + `public/plots/`

### All Generated Outputs Are Present

| Output File | Location |
|---|---|
| `cleaned_dataset.csv` (50,000 rows) | `python/data/processed/` |
| `dataset_summary.json` | `public/data/` |
| `descriptive_statistics.json` | `public/data/` |
| `correlations.json` | `public/data/` |
| `qos_summary.json` | `public/data/` |
| `carrier_analysis.json` | `public/data/` |
| `technology_analysis.json` | `public/data/` |
| `temporal_analysis.json` | `public/data/` |
| `location_analysis.json` | `public/data/` |
| `model_comparison.json` | `public/data/` |
| `feature_importance.json` | `public/data/` |
| `prediction_models.json` | `public/data/` |
| `insights.json` | `public/data/` |
| `sample_records.csv/json` (5,000 rows) | `public/data/` |
| 14 EDA/ML plots (PNG) | `public/plots/` |
| Trained .joblib model files | `python/output/models/` |

---

## ML Results Summary

### Download Speed (Mbps) — Best: Linear Regression
| Metric | Value |
|---|---|
| MAE | 225.86 |
| RMSE | 260.67 |
| R² | −0.0007 (≈ 0) |

### Latency (ms) — Best: Gradient Boosting
| Metric | Value |
|---|---|
| MAE | ~3.18 |
| RMSE | ~3.98 |
| R² | ~0.52 |

> **Academic note:** Download Speed has near-zero correlations with all features (dataset appears synthetic). The Latency model is the stronger result. The dashboard should present **both** but emphasize Latency as the better-performing prediction.

---

## What Is Missing

### 1. 🔴 Big Data Component — `big_data/big_data_analysis.py`
No PySpark script exists anywhere in the project.

Must demonstrate:
- Loading CSV with SparkSession
- Schema display + record/column count
- Missing value handling + duplicate removal
- Average QoS metric aggregation
- GroupBy Carrier aggregation
- GroupBy Network Type aggregation
- Export results to `public/data/bigdata_results.json` for the dashboard

### 2. 🔴 Next.js Dashboard — Entire `app/` directory
`node_modules/` is not installed. No `app/`, `pages/`, `src/`, or `components/` directory exists.

The `package.json` is correctly configured for:
- Next.js 14 (App Router)
- React 18
- Tailwind CSS 3
- Recharts
- Lucide Icons
- framer-motion

**Must build:**

```
app/
  layout.tsx          ← root layout (dark theme, font)
  globals.css         ← CSS variables
  page.tsx            ← redirects to /overview
  overview/page.tsx   ← KPI cards + summary
  qos/page.tsx        ← carrier/tech/temporal charts
  prediction/page.tsx ← model results + feature chart
  bigdata/page.tsx    ← PySpark results + 5V explanation

components/
  Sidebar.tsx
  KPICard.tsx
  CarrierChart.tsx
  TechChart.tsx
  TemporalChart.tsx
  CorrelationHeatmap.tsx
  PredictionChart.tsx
  FeatureImportanceChart.tsx
  BigDataSection.tsx
  StatsTable.tsx
```

### 3. 🟡 README.md
Create academic README covering objectives, dataset, tools, methodology, results, how to run.

### 4. 🟢 `pyspark` in requirements.txt
Add `pyspark` to `requirements.txt`.

---

## Gap Analysis — Priority Order

| # | Task | Priority | Effort |
|---|---|---|---|
| 1 | Create `big_data/big_data_analysis.py` | 🔴 HIGH | ~1 hr |
| 2 | Add `pyspark` to `requirements.txt` | 🔴 HIGH | Trivial |
| 3 | Run `npm install` | 🔴 HIGH | Trivial |
| 4 | Build Next.js dashboard (4 pages + components) | 🔴 HIGH | ~4–6 hrs |
| 5 | Create `README.md` | 🟡 MEDIUM | ~30 min |

---

## Installation Checklist

```bash
# Python dependencies
pip install -r requirements.txt
pip install pyspark    # Not yet in requirements.txt

# Verify Java for PySpark
java -version          # Must be Java 8, 11, or 17

# Frontend
npm install            # node_modules/ does not exist yet
npm run dev            # Start dashboard at http://localhost:3000
```
