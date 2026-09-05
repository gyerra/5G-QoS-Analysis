# 5G Network Quality of Service (QoS) Analysis Dashboard

Academic Project for **Data Analysis & Visualization** and **Big Data Fundamentals**.

----

## Practical Purpose & Business Use Case of the Dashboard

### Why Build This Dashboard?
In modern telecommunications, **5G Quality of Service (QoS)** directly dictates user experience, network reliability, and operator competitiveness. Network telemetry data is generated constantly across thousands of cell towers and millions of user devices. Without central analytics, telecom engineers cannot quickly pinpoint coverage gaps, cell congestion, or performance degradation.

This interactive dashboard serves as an **end-to-end Telemetry & Analytics Platform** designed for:

1. **Network Performance Monitoring & SLA Compliance**:
   - Enables operators to track **Download Speed (Mbps)**, **Upload Speed (Mbps)**, **Latency (ms)**, **Jitter (ms)**, and **Signal Strength (dBm)** against strict Service Level Agreements (SLAs).
   - Identifies which network generations (**4G**, **5G NSA**, **5G SA**) deliver expected throughput under real-world conditions.

2. **Carrier Benchmarking**:
   - Compares performance metrics across major operators (**AT&T, Airtel, BSNL, Jio, T-Mobile, Verizon, Vi**).
   - Identifies which carrier provides the lowest latency or highest download speed in target regions.

3. **Infrastructure Planning & Congestion Analysis**:
   - Evaluates 24-hour temporal trends to highlight peak congestion hours (e.g., evening rush hours).
   - Allows network planners to allocate spectrum and upgrade cell towers where dropped connection rates spike.

4. **Predictive Quality Assurance (Machine Learning)**:
   - Forecasts expected throughput and latency before network degradation impacts consumers.

5. **Big Data Operations (Apache PySpark)**:
   - Demonstrates how distributed memory processing handles high-velocity telemetry streams that exceed standard database capacities.

---

## Project Overview

This project presents a comprehensive Quality of Service (QoS) analysis pipeline and interactive web dashboard for 5G mobile communication networks.

The application domain focuses on **5G telecom analytics**, processing **50,000 network measurement records** collected across multiple carriers (AT&T, Airtel, BSNL, Jio, T-Mobile, Verizon, Vi), network technologies (4G, 5G NSA, 5G SA), and geographic locations.

---

## Objectives

1. **Data Preprocessing & Cleaning**: Detect missing values, impute numeric/categorical columns, identify outliers (IQR), and format timestamps.
2. **Exploratory Data Analysis (EDA)**: Generate statistical summaries (Mean, Median, Std, Min, Max) and visualization plots with explicit X & Y axis labeling (Histograms, Box plots, Scatter plots, Correlation Heatmap).
3. **QoS Performance Benchmarking**: Compare Download Speed, Upload Speed, Latency, Jitter, and Signal Strength by Carrier, Network Technology, Time of Day, and Location.
4. **Machine Learning Prediction**: Build and evaluate linear regression and tree-based regression models to predict QoS metrics (Download Speed & Latency) using MAE, RMSE, and R².
5. **Big Data Processing (Apache PySpark)**: Demonstrate distributed DataFrame transformations, aggregations, filtering, and the 5 V's of Big Data (Volume, Velocity, Variety, Veracity, Value).
6. **Interactive Telemetry Dashboard**: Present insights, KPIs, analytical charts, and model results in a modern Next.js + React web application.

---

## Machine Learning Model Comparison & Evaluation Metrics Explained

### Why Compare Multiple ML Models?
In data science, no single algorithm is optimal for all datasets (the *No Free Lunch* theorem). We compare 5 different models:
- **Linear Regression**: Simple baseline; assumes linear relationships between features and target.
- **Decision Tree**: Captures non-linear decision boundaries and feature interactions.
- **Random Forest**: Ensemble method; reduces variance and prevents overfitting.
- **Gradient Boosting**: Sequential ensemble; optimizes residual errors iteratively.
- **XGBoost**: Highly optimized gradient boosting framework for tabular telemetry data.

Comparing these models on the dashboard allows us to select the model with the lowest error and highest explainability.

---

### Understanding the Evaluation Metrics (MAE, RMSE, R²)

| Metric | Full Name | Practical Meaning in Telecom Analytics | Ideal Value |
|---|---|---|---|
| **MAE** | **Mean Absolute Error** | Measures the average magnitude of errors in original units (e.g., Mbps or ms). An MAE of `4.78 ms` means predictions are off by ~4.78 ms on average. | **Lower is better** (0 = perfect prediction) |
| **RMSE** | **Root Mean Square Error** | Similar to MAE, but squares errors before taking the root, heavily penalizing **large outliers** or extreme drops. In telecom, large latency spikes or dropouts destroy video calls/gaming, so tracking RMSE is critical. | **Lower is better** (0 = perfect prediction) |
| **R²** | **R-squared (Coefficient of Determination)** | Measures the percentage of variance in the target variable explained by the features (0.0 = 0%, 1.0 = 100%). Indicates how much predictive information the dataset features actually contain. | **Higher is better** (1.0 = 100% variance explained) |

#### Academic Note on Dataset R² Results:
- **Download Speed Prediction**: Achieves `R² ≈ 0.0`. This occurs because in synthetically generated datasets, numerical features are often randomized independently. The dashboard transparently highlights this, showing that features like signal strength do not linearly predict throughput in this specific dataset.
- **Latency Prediction**: Achieves better stability (`MAE ~ 4.78 ms`), demonstrating model selection in practice.

---

## Repository Structure

```text
QOS Analysis/
├── 5g_network_data.csv        # Primary 5G dataset (50,000 rows × 21 cols)
├── python/
│   ├── load_data.py           # Dataset discovery and merging
│   ├── config.py              # Central schema and configuration settings
│   ├── preprocessing/
│   │   └── clean_data.py      # Missing value imputation, outlier detection, encoding
│   ├── statistical_analysis.py# Descriptive stats & Pearson/Spearman correlations
│   ├── qos_analysis.py        # Grouped QoS statistics (Carrier, Tech, Temporal)
│   ├── visualization/
│   │   └── eda.py             # Matplotlib/Seaborn plot generation
│   ├── ml/
│   │   └── train_model.py     # Train & evaluate Linear Regression, Decision Tree, RF, GB, XGB
│   ├── generate_outputs.py    # Export results & copy assets for frontend
│   └── run_pipeline.py        # Master pipeline runner
├── big_data/
│   └── big_data_analysis.py   # PySpark distributed DataFrame pipeline & 5 V's demonstration
├── public/
│   ├── data/                  # Output JSON data served to frontend dashboard
│   └── plots/                 # Generated static plot images
├── app/                       # Next.js 14 App Router dashboard
│   ├── layout.tsx             # Root layout with sidebar navigation
│   ├── globals.css            # Dark telecom theme styling
│   ├── overview/page.tsx      # Overview KPIs & summary charts (with X/Y axis labels)
│   ├── qos/page.tsx           # QoS analysis by Carrier, Tech & Temporal trends
│   ├── prediction/page.tsx    # ML Model evaluation & feature importance
│   └── bigdata/page.tsx       # PySpark results & Big Data 5 V's breakdown
├── components/                # Modular React components (KPICard, ChartCard, Sidebar)
├── package.json               # Node.js dependencies (Next.js, Recharts, Lucide)
├── requirements.txt           # Python dependencies (pandas, scikit-learn, pyspark)
├── PROJECT_STATUS.md          # Complete project status audit
└── README.md                  # Project documentation
```

---

## 🛠️ Technology Stack

| Domain | Technologies |
|---|---|
| **Data Processing & Analytics** | Python 3.10+, Pandas, NumPy, SciPy |
| **Data Visualization** | Matplotlib, Seaborn, Recharts |
| **Machine Learning** | Scikit-Learn (Linear Regression, Decision Tree, Random Forest, Gradient Boosting), XGBoost |
| **Big Data Engine** | Apache Spark (PySpark Distributed DataFrames) |
| **Frontend Dashboard** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons |

---

## Project Pipeline & Workflow

```text
5G Network Dataset (50,000 Records)
        ↓
Data Preprocessing (Python / Pandas)
        ↓
Exploratory Data Analysis & Statistics
        ↓
QoS Grouped Benchmarking (Carrier, Technology, Location)
        ↓
Machine Learning Regression (MAE, RMSE, R²)
        ↓
Distributed Big Data Aggregation (PySpark)
        ↓
Interactive Web Dashboard (Next.js + Recharts)
```

---

## How to Run the Project

### 1. Python Pipeline Execution

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the complete Python data processing & ML pipeline:
```bash
python python/run_pipeline.py
```

### 2. Big Data Analysis (PySpark)

Ensure Java (JDK 8/11/17) is installed (`java -version`), then execute:
```bash
python big_data/big_data_analysis.py
```

*(Note: If PySpark is not installed, the script automatically uses a Pandas fallback while producing identical output schemas).*

### 3. Interactive Web Dashboard

Install Node modules and start the development server:
```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the interactive dashboard.

---

## Key Results & Insights

1. **Overall Averages**:
   - Average Download Speed: **~551.18 Mbps**
   - Average Upload Speed: **~84.80 Mbps**
   - Average Latency: **~10.50 ms**
   - Average Jitter: **~2.56 ms**
   - Average Signal Strength: **~ -84.84 dBm**

2. **Machine Learning Evaluation**:
   - Models compared across MAE, RMSE, and R² for target metrics.
   - Linear Regression & Tree models evaluated on 80/20 chronological splits.

3. **Big Data Concept Demonstration**:
   - **Volume**: 50,000 records processed in memory partitions.
   - **Velocity**: Real-time measurement streaming scenario modeled.
   - **Variety**: Mixed numeric, categorical, temporal, and boolean network schema.
   - **Veracity**: Deduplication & IQR outlier retention.
   - **Value**: Actionable carrier comparison & QoE optimization.

---

## Academic Summary

This project demonstrates an end-to-end data lifecycle from raw network measurements to actionable QoS insights. It combines data engineering (PySpark), statistical analytics (Pandas/SciPy), predictive modeling (Scikit-Learn), and modern web visualization (Next.js/React).
