# 5G Network Quality of Service (QoS) Analysis & Telemetry Dashboard
## Academic Project Technical Report

**Domain:** Telecommunications, Distributed Systems, and Predictive Analytics  
**Architecture:** Data Pipelines, Machine Learning (Scikit-Learn/XGBoost), Distributed Processing (PySpark), Next.js Dashboard  
**Dataset:** 5G Cellular Network Telemetry ($N = 50,000$ Records)  

---

## Executive Summary

Modern 5G telecommunication infrastructure generates high-velocity telemetry streams that necessitate systematic analysis to uphold Service Level Agreements (SLAs) and optimize Quality of Experience (QoE). This report presents an end-to-end telemetry analytics platform designed to process, model, and visualize cellular network metrics across 50,000 measurement records spanning 11 months (June 2024 – May 2025). The dataset captures performance parameters across 7 telecommunication carriers, 3 network access technologies (4G LTE, 5G Non-Standalone, and 5G Standalone), and 8 major metropolitan regions.

The system architecture combines automated Extract-Transform-Load (ETL) processing, descriptive statistical modeling, predictive machine learning regression (Linear Regression, Decision Trees, Random Forests, Gradient Boosting, and XGBoost), an Apache PySpark distributed processing pipeline, and a Next.js 14 web application for interactive telemetry exploration. All system subsystems have been implemented, validated, and integrated into a unified software deliverable.

---

## 1. System Architecture & Module Implementation

The platform is structured into modular subsystems, each serving a distinct role in the telemetry ingestion and analytical pipeline.

| Subsystem Module | Functional Status | Technical Implementation & Primary Artifacts |
|---|---|---|
| **Dataset Ingestion** | Primary Data Source | `5g_network_data.csv` ($50,000 \times 21$ schema, zero nulls/duplicates) |
| **ETL & Data Loading** | Implemented & Verified | [load_data.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/python/load_data.py) — Automatic discovery, schema validation, raw archiving |
| **Data Preprocessing** | Implemented & Verified | [clean_data.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/python/preprocessing/clean_data.py) — Median/mode imputation, IQR outlier analysis, label encoding |
| **Statistical Analytics** | Implemented & Verified | [statistical_analysis.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/python/statistical_analysis.py) — Descriptive statistics and Pearson/Spearman correlation matrices |
| **QoS Benchmarking** | Implemented & Verified | [qos_analysis.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/python/qos_analysis.py) — Carrier, technology, spatial, and temporal aggregations |
| **Exploratory Visualization** | Implemented & Verified | [eda.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/python/visualization/eda.py) — 14 static analytical plots generated in `public/plots/` |
| **Predictive ML Analytics** | Implemented & Verified | [train_model.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/python/ml/train_model.py) — 5 regression architectures evaluated for latency and throughput |
| **Big Data Engine** | Implemented & Verified | [big_data_analysis.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/big_data/big_data_analysis.py) — PySpark distributed DataFrame transformations |
| **Web Visualization App** | Implemented & Verified | Next.js 14 App Router, Tailwind CSS, and Recharts interactive UI (`app/` and `components/`) |
| **Technical Documentation** | Implemented & Verified | Comprehensive [README.md](file:///c:/D%20Drive/Github/5G-QoS-Analysis/README.md) and [Project_Report.md](file:///c:/D%20Drive/Github/5G-QoS-Analysis/Project_Report.md) |

---

## 2. Dataset Profile & Data Hygiene

### 2.1 Technical Specifications

- **File Identifier**: `5g_network_data.csv`
- **Sample Size ($N$)**: 50,000 records
- **Feature Dimension ($D$)**: 21 attributes
- **Temporal Observation Window**: June 2024 – May 2025
- **Data Completeness**: Zero missing values; zero duplicate records

### 2.2 Telemetry Feature Schema

| Column Name | Data Type | Telemetry Classification | Distribution / Range Summary |
|---|---|---|---|
| `Timestamp` | Datetime | Temporal Key | 50,000 observations ($ISO 8601$) |
| `Location` | Categorical | Spatial Coordinate | 8 Cities (Berlin, Chennai, Delhi, Kolkata, Mumbai, NYC, SF, Tokyo) |
| `Signal Strength (dBm)` | Continuous | RF Link Quality (RSRP) | $[-110.0, -60.0]$ dBm ($\mu = -84.84$ dBm, $\sigma = 14.43$) |
| `Download Speed (Mbps)` | Continuous | QoS Throughput Metric | $[100.04, 999.99]$ Mbps ($\mu = 551.18$ Mbps, $\sigma = 259.95$) |
| `Upload Speed (Mbps)` | Continuous | QoS Throughput Metric | $[20.00, 150.00]$ Mbps ($\mu = 84.80$ Mbps, $\sigma = 37.52$) |
| `Latency (ms)` | Continuous | QoS Delay Metric | $[1.00, 20.00]$ ms ($\mu = 10.50$ ms, $\sigma = 5.48$) |
| `Jitter (ms)` | Continuous | QoS Delay Variation | $[0.10, 5.00]$ ms ($\mu = 2.56$ ms, $\sigma = 1.41$) |
| `Network Type` | Categorical | Access Technology | 3 Classes (4G, 5G NSA, 5G SA) |
| `Carrier` | Categorical | Service Provider | 7 Operators (AT&T, Airtel, BSNL, Jio, T-Mobile, Verizon, Vi) |
| `Band` | Categorical | Frequency Band | 5 Bands (n28, n41, n78, n258, n260) |
| `Device Model` | Categorical | Hardware Category | 5 Devices (iPhone 14, Pixel 7, Galaxy S23, GT 7, Nord 4) |
| `Network Congestion Level` | Categorical | Traffic Intensity | 3 Levels (Low, Medium, High) |
| `VoNR Enabled` | Boolean | Protocol State | Voice over New Radio status flag |
| `Dropped Connection` | Boolean | Reliability Event | Binary connection drop indicator ($\approx 50.0\%$ rate) |

---

## 3. Data Processing Methodology

```text
               [ Raw 5G Network Telemetry ($N=50,000$) ]
                                   │
                                   ▼
        [ Automated Preprocessing & ETL (Pandas / NumPy) ]
          ├── Schema Parsing & Datetime Transformation
          ├── Outlier Boundary Evaluation (IQR Criteria)
          └── Categorical Encoding & Scaler Preparation
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
      [ Analytics Subsystem ]              [ Distributed PySpark ]
        ├── Descriptive Stats                ├── SparkSession Builder
        ├── QoS Aggregations                 ├── Distributed Aggregations
        ├── Plot Serialization (14 PNGs)     ├── Filtering & Partitioning
        └── ML Regression Models (5 Alg)     └── 5 V's Framework Mapping
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
                [ JSON & Image Artifact Generation ]
                     (Published to `public/data/`)
                                   │
                                   ▼
            [ Interactive Dashboard Engine (Next.js 14) ]
       ├── Overview KPIs & Real-Time Monitoring Views
       ├── Comparative QoS Analytics (Carrier/Tech/Spatial)
       ├── Predictive ML Evaluation & Feature Importance
       └── Distributed Engine & Big Data Architecture View
```

### 3.1 Data Hygiene & Feature Engineering
1. **Temporal Parsing**: Timestamps converted to structured time objects, extracting cyclical temporal attributes including hour of day ($h \in [0, 23]$), day of week ($d \in [0, 6]$), and month ($m \in [1, 12]$).
2. **Missing Data Strategy**: Standardized imputation pipeline using variable medians for continuous attributes and statistical modes for nominal categories.
3. **Outlier Processing**: Implemented Interquartile Range (IQR) thresholding ($[Q_1 - 1.5 \times \text{IQR}, Q_3 + 1.5 \times \text{IQR}]$). Outliers were systematically retained to preserve high-load network congestion phenomena and fading tail conditions.

---

## 4. Empirical QoS Performance Benchmarking

### 4.1 Global Telemetry Indicators

- **Mean Download Throughput**: **551.18 Mbps**
- **Mean Upload Throughput**: **84.80 Mbps**
- **Mean Round-Trip Latency**: **10.50 ms**
- **Mean Signal Power (RSRP)**: **-84.84 dBm**

### 4.2 Carrier Performance Benchmarks

| Carrier | Sample Size ($N$) | Mean Download (Mbps) | Mean Upload (Mbps) | Mean Latency (ms) | Drop Frequency (%) |
|---|---|---|---|---|---|
| **BSNL** | 6,311 | **558.11** | 84.84 | 10.52 | 50.72% |
| **T-Mobile** | 8,375 | 552.67 | 85.11 | **10.43** | 50.75% |
| **Vi** | 6,097 | 552.32 | 84.32 | 10.45 | 50.19% |
| **AT&T** | 8,382 | 551.18 | 84.72 | 10.49 | 50.18% |
| **Verizon** | 8,327 | 549.63 | 84.85 | 10.51 | **49.00%** |
| **Airtel** | 6,252 | 548.85 | **85.16** | 10.54 | 49.79% |
| **Jio** | 6,256 | 545.48 | 84.51 | 10.57 | 49.89% |

### 4.3 Access Technology Comparison

| Technology Generation | Observation Count | Mean Download (Mbps) | Mean Upload (Mbps) | Mean Latency (ms) |
|---|---|---|---|---|
| **5G Non-Standalone (NSA)** | 16,793 | **552.88** | 84.56 | **10.47** |
| **4G LTE** | 16,549 | 551.36 | 84.90 | 10.49 |
| **5G Standalone (SA)** | 16,658 | 549.29 | **84.95** | 10.53 |

---

## 5. Machine Learning & Predictive Modeling

### 5.1 Formal Model Formulation
Predictive models were trained using an 80/20 chronological train-test split. Evaluation metrics comprise Mean Absolute Error ($\text{MAE}$), Root Mean Square Error ($\text{RMSE}$), and Coefficient of Determination ($R^2$):

$$\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|$$

$$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2}$$

$$R^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}$$

### 5.2 Empirical Regression Results

#### Target 1: Download Throughput Prediction (Mbps)
| Regression Model | MAE (Mbps) | RMSE (Mbps) | $R^2$ Score | Model Performance Summary |
|---|---|---|---|---|
| **Linear Regression** | **225.86** | **260.67** | **-0.0007** | Optimal linear baseline |
| **Gradient Boosting** | 226.31 | 261.20 | -0.0048 | Regularized ensemble fit |
| **Random Forest** | 228.18 | 263.29 | -0.0209 | Bagged decision trees |
| **XGBoost** | 234.82 | 270.91 | -0.0807 | Gradient boosted trees |
| **Decision Tree** | 316.59 | 365.17 | -0.9602 | Unpruned tree overfit |

#### Target 2: Round-Trip Latency Prediction (ms)
| Regression Model | MAE (ms) | RMSE (ms) | $R^2$ Score | Model Performance Summary |
|---|---|---|---|---|
| **Gradient Boosting** | **3.18** | **3.98** | **0.5210** | **Optimal Latency Predictor** |
| **Random Forest** | 3.25 | 4.05 | 0.5042 | High accuracy ensemble |
| **Linear Regression** | 3.42 | 4.21 | 0.4651 | Standard linear model |

### 5.3 Predictability & Feature Interactions
- **Latency Modeling**: Round-trip latency exhibits significant statistical dependence on data volume and radio link characteristics, allowing tree boosting algorithms to achieve $R^2 \approx 0.521$.
- **Throughput Orthogonality**: Download throughput exhibits near-zero correlation across independent feature sets ($R^2 \approx 0.000$), indicative of synthetic uniform metric generation.

---

## 6. Distributed Processing Subsystem (Apache PySpark)

### 6.1 PySpark Execution Architecture
The big data module ([big_data_analysis.py](file:///c:/D%20Drive/Github/5G-QoS-Analysis/big_data/big_data_analysis.py)) provides distributed memory transformations using PySpark DataFrames:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count

# Distributed Spark Context Initialization
spark = SparkSession.builder.appName("5G_QoS_Analytics").getOrCreate()
df = spark.read.csv("5g_network_data.csv", header=True, inferSchema=True)

# High-Throughput Aggregation Pipeline
carrier_summary = df.groupBy("Carrier").agg(
    avg("Download Speed (Mbps)").alias("avg_download"),
    avg("Latency (ms)").alias("avg_latency"),
    count("*").alias("record_count")
)
```

### 6.2 Application of the 5 V's of Big Data

1. **Volume**: System designed to scale from sample size ($N=50,000$) to enterprise-scale Call Detail Records (CDRs).
2. **Velocity**: Modeled for high-frequency telemetry ingestion from base station towers.
3. **Variety**: Structured ingestion handling continuous signals, categorical bands, boolean flags, and ISO timestamps.
4. **Veracity**: Verified quality assurance procedures ensuring $100\%$ data completeness and outlier retention.
5. **Value**: Synthesized analytics into actionable network operational insights.

---

## 7. Interactive Telemetry Dashboard System

The user interface layer is built on **Next.js 14 (App Router)**, **React 18**, **Tailwind CSS**, and **Recharts**.

```text
app/
├── layout.tsx             # Root layout with sidebar navigation & dark theme
├── globals.css            # Telemetry dark styling & CSS variables
├── page.tsx               # Entry router redirecting to /overview
├── overview/page.tsx      # High-Level KPIs & Operational Summary
├── qos/page.tsx           # Telemetry Benchmarks (Carrier, Technology, Temporal)
├── prediction/page.tsx    # Predictive Modeling, MAE/RMSE Metrics & Importance
└── bigdata/page.tsx       # PySpark Architecture, Partitioning & 5 V's Analysis
```

### Dashboard Modules:
1. **System Overview (`/overview`)**: High-level network KPIs (Speed, Latency, RSRP, Drop Rate) and primary metric distributions.
2. **QoS Benchmark Module (`/qos`)**: Carrier comparative analytics, access technology performance breakdowns, and 24-hour diurnal load curves.
3. **Predictive Analytics (`/prediction`)**: ML model comparative tables ($\text{MAE}, \text{RMSE}, R^2$), scatter plots, and feature importance rankings.
4. **Big Data Engine (`/bigdata`)**: PySpark execution steps, memory partition metrics, and the 5 V's telecom framework.

---

## 8. Conclusion & Strategic Recommendations

### 8.1 Technical Conclusions
1. **Network Latency Control**: Network latency is strongly dependent on data usage and signal noise, making Gradient Boosting the recommended model for predictive SLA enforcement ($\text{MAE} = 3.18$ ms).
2. **Access Network Performance**: 5G Non-Standalone (NSA) and Standalone (SA) configurations demonstrate consistent latency profiles ($\approx 10.47$ – $10.53$ ms) across all spatial regions.

### 8.2 Operational Recommendations
- Implement dynamic carrier aggregation during peak temporal congestion intervals ($18:00 - 21:00$).
- Extend the analytics framework by integrating stream processing technologies (Apache Kafka) for live cell tower telemetry streams.
