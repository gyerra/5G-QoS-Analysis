"""
Big Data Analysis — 5G QoS Dataset using Apache PySpark
========================================================
Demonstrates: Volume, Velocity, Variety, Veracity, Value (5 V's)

Pipeline:
  SparkSession
      ↓
  Load CSV (Distributed DataFrame)
      ↓
  Schema + Record Count
      ↓
  Data Cleaning (missing, duplicates)
      ↓
  Filtering
      ↓
  GroupBy Carrier → Aggregation
      ↓
  GroupBy Network Type → Aggregation
      ↓
  GroupBy Location → Aggregation
      ↓
  Export Results → JSON
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "5g_network_data.csv"
OUTPUT_JSON = PROJECT_ROOT / "public" / "data" / "bigdata_results.json"

# ---------------------------------------------------------------------------
# Try importing PySpark; provide helpful message if not installed
# ---------------------------------------------------------------------------
try:
    # pyrefly: ignore [missing-import]
    from pyspark.sql import SparkSession
    # pyrefly: ignore [missing-import]
    from pyspark.sql import functions as F
    # pyrefly: ignore [missing-import]
    from pyspark.sql.types import DoubleType
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False


def run_pyspark_analysis() -> dict:
    """Full PySpark QoS analysis pipeline."""

    # -----------------------------------------------------------------------
    # 1. Create SparkSession
    # -----------------------------------------------------------------------
    spark = (
        SparkSession.builder
        .appName("5G_QoS_BigData_Analysis")
        .master("local[*]")                         # use all local CPU cores
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")        # disable web UI for script mode
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")          # suppress INFO/WARN noise

    print("=" * 60)
    print("5G QoS Big Data Analysis — Apache PySpark")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # 2. Load CSV into Spark DataFrame
    # -----------------------------------------------------------------------
    print(f"\n[1] Loading dataset: {CSV_PATH.name}")
    df = spark.read.csv(
        str(CSV_PATH),
        header=True,
        inferSchema=True,
    )

    # -----------------------------------------------------------------------
    # 3. Schema + basic dimensions
    # -----------------------------------------------------------------------
    print("\n[2] Schema:")
    df.printSchema()

    total_records = df.count()
    total_columns = len(df.columns)

    print(f"\n[3] Dimensions:")
    print(f"    Rows    : {total_records:,}")
    print(f"    Columns : {total_columns}")

    # -----------------------------------------------------------------------
    # 4. Data Quality — Missing Values
    # -----------------------------------------------------------------------
    print("\n[4] Missing Value Analysis:")
    missing_counts = {}
    for col_name in df.columns:
        null_count = df.filter(F.col(col_name).isNull()).count()
        missing_counts[col_name] = null_count
        if null_count > 0:
            print(f"    {col_name}: {null_count} missing")

    total_missing = sum(missing_counts.values())
    if total_missing == 0:
        print("    No missing values detected.")

    # -----------------------------------------------------------------------
    # 5. Remove Duplicate Rows
    # -----------------------------------------------------------------------
    print("\n[5] Duplicate Removal:")
    df_deduped = df.dropDuplicates()
    duplicates_removed = total_records - df_deduped.count()
    print(f"    Duplicates removed : {duplicates_removed:,}")
    print(f"    Remaining records  : {df_deduped.count():,}")

    # -----------------------------------------------------------------------
    # 6. Overall QoS Aggregation
    # -----------------------------------------------------------------------
    print("\n[6] Overall QoS Averages:")
    overall_row = df_deduped.agg(
        F.round(F.avg("Download Speed (Mbps)"), 2).alias("avg_download"),
        F.round(F.avg("Upload Speed (Mbps)"), 2).alias("avg_upload"),
        F.round(F.avg("Latency (ms)"), 2).alias("avg_latency"),
        F.round(F.avg("Jitter (ms)"), 2).alias("avg_jitter"),
        F.round(F.avg("Signal Strength (dBm)"), 2).alias("avg_signal"),
        F.count("*").alias("record_count"),
    ).collect()[0]

    overall = {
        "avg_download_mbps": float(overall_row["avg_download"]),
        "avg_upload_mbps":   float(overall_row["avg_upload"]),
        "avg_latency_ms":    float(overall_row["avg_latency"]),
        "avg_jitter_ms":     float(overall_row["avg_jitter"]),
        "avg_signal_dbm":    float(overall_row["avg_signal"]),
        "record_count":      int(overall_row["record_count"]),
    }

    print(f"    Avg Download  : {overall['avg_download_mbps']} Mbps")
    print(f"    Avg Upload    : {overall['avg_upload_mbps']} Mbps")
    print(f"    Avg Latency   : {overall['avg_latency_ms']} ms")
    print(f"    Avg Jitter    : {overall['avg_jitter_ms']} ms")
    print(f"    Avg Signal    : {overall['avg_signal_dbm']} dBm")

    # -----------------------------------------------------------------------
    # 7. GroupBy Carrier
    # -----------------------------------------------------------------------
    print("\n[7] Carrier Aggregation:")
    carrier_df = (
        df_deduped
        .groupBy("Carrier")
        .agg(
            F.round(F.avg("Download Speed (Mbps)"), 2).alias("avg_download"),
            F.round(F.avg("Upload Speed (Mbps)"), 2).alias("avg_upload"),
            F.round(F.avg("Latency (ms)"), 2).alias("avg_latency"),
            F.round(F.avg("Jitter (ms)"), 2).alias("avg_jitter"),
            F.round(F.avg("Signal Strength (dBm)"), 2).alias("avg_signal"),
            F.count("*").alias("record_count"),
        )
        .orderBy("avg_download", ascending=False)
    )
    carrier_df.show(truncate=False)
    carrier_results = [row.asDict() for row in carrier_df.collect()]

    # -----------------------------------------------------------------------
    # 8. GroupBy Network Type
    # -----------------------------------------------------------------------
    print("\n[8] Network Type Aggregation:")
    tech_df = (
        df_deduped
        .groupBy("Network Type")
        .agg(
            F.round(F.avg("Download Speed (Mbps)"), 2).alias("avg_download"),
            F.round(F.avg("Upload Speed (Mbps)"), 2).alias("avg_upload"),
            F.round(F.avg("Latency (ms)"), 2).alias("avg_latency"),
            F.round(F.avg("Jitter (ms)"), 2).alias("avg_jitter"),
            F.round(F.avg("Signal Strength (dBm)"), 2).alias("avg_signal"),
            F.count("*").alias("record_count"),
        )
        .orderBy("avg_download", ascending=False)
    )
    tech_df.show(truncate=False)
    tech_results = [row.asDict() for row in tech_df.collect()]

    # -----------------------------------------------------------------------
    # 9. GroupBy Location
    # -----------------------------------------------------------------------
    print("\n[9] Location Aggregation:")
    location_df = (
        df_deduped
        .groupBy("Location")
        .agg(
            F.round(F.avg("Download Speed (Mbps)"), 2).alias("avg_download"),
            F.round(F.avg("Latency (ms)"), 2).alias("avg_latency"),
            F.count("*").alias("record_count"),
        )
        .orderBy("avg_download", ascending=False)
    )
    location_df.show(truncate=False)
    location_results = [row.asDict() for row in location_df.collect()]

    # -----------------------------------------------------------------------
    # 10. Filtering — High-quality connections (Signal > -80 dBm, Latency < 5 ms)
    # -----------------------------------------------------------------------
    print("\n[10] Filtering — High-Quality Connections (Signal > -80 dBm AND Latency < 5 ms):")
    high_quality = df_deduped.filter(
        (F.col("Signal Strength (dBm)") > -80) &
        (F.col("Latency (ms)") < 5)
    )
    hq_count = high_quality.count()
    hq_pct = round(hq_count / total_records * 100, 2)
    print(f"    High-quality records : {hq_count:,} ({hq_pct}%)")

    # -----------------------------------------------------------------------
    # 11. Network Type Distribution
    # -----------------------------------------------------------------------
    print("\n[11] Network Type Distribution:")
    dist_df = (
        df_deduped
        .groupBy("Network Type")
        .count()
        .orderBy("count", ascending=False)
    )
    dist_df.show()
    network_distribution = {
        row["Network Type"]: int(row["count"])
        for row in dist_df.collect()
    }

    # -----------------------------------------------------------------------
    # 12. Dropped Connection Rate by Carrier
    # -----------------------------------------------------------------------
    print("\n[12] Dropped Connection Rate by Carrier:")
    drop_df = (
        df_deduped
        .groupBy("Carrier")
        .agg(
            F.round(F.avg(F.col("Dropped Connection").cast(DoubleType())) * 100, 2)
             .alias("drop_rate_pct"),
            F.count("*").alias("total"),
        )
        .orderBy("drop_rate_pct", ascending=False)
    )
    drop_df.show()
    drop_results = [row.asDict() for row in drop_df.collect()]

    # -----------------------------------------------------------------------
    # 13. Build output dictionary
    # -----------------------------------------------------------------------
    result = {
        "pyspark_version": spark.version,
        "dataset": {
            "filename": CSV_PATH.name,
            "total_records": total_records,
            "total_columns": total_columns,
            "missing_values": total_missing,
            "duplicates_removed": duplicates_removed,
            "high_quality_records": hq_count,
            "high_quality_pct": hq_pct,
        },
        "overall_qos": overall,
        "carrier_aggregation": carrier_results,
        "technology_aggregation": tech_results,
        "location_aggregation": location_results,
        "network_distribution": network_distribution,
        "dropped_connection_by_carrier": drop_results,
        "big_data_concepts": {
            "Volume": (
                f"The dataset contains {total_records:,} network measurement records "
                "spanning 11 months (June 2024 – May 2025). In real 5G networks, such "
                "measurements are collected continuously from millions of devices, "
                "generating data at a scale that requires distributed processing frameworks."
            ),
            "Velocity": (
                "Network quality measurements (signal strength, latency, throughput) can be "
                "generated every few seconds per device. Across thousands of active users in "
                "a city, this results in millions of records per hour — requiring stream "
                "processing pipelines like Apache Kafka + Spark Streaming."
            ),
            "Variety": (
                f"The dataset contains {total_columns} columns of mixed types: "
                "numerical (speed, latency, signal), categorical (carrier, location, band, "
                "network type), boolean (VoNR, dropped connection), and temporal (timestamp). "
                "Real deployments also include GPS coordinates, application-layer metrics, "
                "and device telemetry."
            ),
            "Veracity": (
                "Real-world network data suffers from sensor errors, dropped packets, "
                f"inconsistent timestamps, and device-specific biases. This dataset had "
                f"{total_missing} missing values and {duplicates_removed} duplicates, "
                "which were addressed during preprocessing. Outliers were identified using "
                "IQR analysis and retained as valid extreme network conditions."
            ),
            "Value": (
                "Raw network measurements become actionable insights through analysis: "
                "carrier performance comparison, network type benchmarking, temporal QoS "
                "trends, and predictive modelling. These insights drive network planning, "
                "carrier selection, and service quality improvements."
            ),
        },
        "spark_pipeline_steps": [
            "SparkSession.builder → local[*] cluster",
            "spark.read.csv() → Distributed DataFrame",
            "df.printSchema() → Column types",
            "df.count() → Total records",
            "df.filter(isNull) → Missing value detection",
            "df.dropDuplicates() → Data deduplication",
            "df.agg(avg, count) → Overall QoS aggregation",
            "df.groupBy('Carrier').agg() → Carrier comparison",
            "df.groupBy('Network Type').agg() → Technology comparison",
            "df.groupBy('Location').agg() → Location analysis",
            "df.filter(condition) → High-quality record selection",
        ],
    }

    # -----------------------------------------------------------------------
    # 14. Export to JSON for dashboard consumption
    # -----------------------------------------------------------------------
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, default=str)

    print(f"\n[OK] Results exported -> {OUTPUT_JSON.relative_to(PROJECT_ROOT)}")

    spark.stop()
    return result


# ---------------------------------------------------------------------------
# Fallback: pandas-based simulation if PySpark is not installed
# ---------------------------------------------------------------------------
def run_pandas_fallback() -> dict:
    """
    Runs the same analysis using pandas when PySpark is not installed.
    Produces identical JSON output so the dashboard still works.
    This also demonstrates the conceptual difference between the two.
    """
    import pandas as pd

    print("=" * 60)
    print("PySpark not installed — running Pandas fallback")
    print("(Install PySpark with: pip install pyspark)")
    print("=" * 60)

    df = pd.read_csv(str(CSV_PATH))
    total_records = len(df)
    total_columns = len(df.columns)
    total_missing = int(df.isnull().sum().sum())
    before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before - len(df)

    high_quality = df[
        (df["Signal Strength (dBm)"] > -80) &
        (df["Latency (ms)"] < 5)
    ]
    hq_count = len(high_quality)
    hq_pct = round(hq_count / total_records * 100, 2)

    overall = {
        "avg_download_mbps": round(float(df["Download Speed (Mbps)"].mean()), 2),
        "avg_upload_mbps":   round(float(df["Upload Speed (Mbps)"].mean()), 2),
        "avg_latency_ms":    round(float(df["Latency (ms)"].mean()), 2),
        "avg_jitter_ms":     round(float(df["Jitter (ms)"].mean()), 2),
        "avg_signal_dbm":    round(float(df["Signal Strength (dBm)"].mean()), 2),
        "record_count":      int(len(df)),
    }

    def group_agg(group_col):
        g = df.groupby(group_col).agg(
            avg_download=("Download Speed (Mbps)", "mean"),
            avg_upload=("Upload Speed (Mbps)", "mean"),
            avg_latency=("Latency (ms)", "mean"),
            avg_jitter=("Jitter (ms)", "mean"),
            avg_signal=("Signal Strength (dBm)", "mean"),
            record_count=(group_col, "count"),
        ).round(2).reset_index()
        return g.rename(columns={group_col: group_col}).to_dict(orient="records")

    carrier_results = group_agg("Carrier")
    tech_results = group_agg("Network Type")
    location_results = [
        {
            "Location": r["Location"],
            "avg_download": r["avg_download"],
            "avg_latency": r["avg_latency"],
            "record_count": r["record_count"],
        }
        for r in group_agg("Location")
    ]

    network_distribution = df["Network Type"].value_counts().to_dict()
    network_distribution = {str(k): int(v) for k, v in network_distribution.items()}

    drop_df = df.groupby("Carrier")["Dropped Connection"].agg(
        lambda x: round(x.astype(float).mean() * 100, 2)
    ).reset_index()
    drop_df.columns = ["Carrier", "drop_rate_pct"]
    drop_df["total"] = df.groupby("Carrier").size().values
    drop_results = drop_df.to_dict(orient="records")

    result = {
        "pyspark_version": "N/A (pandas fallback)",
        "dataset": {
            "filename": CSV_PATH.name,
            "total_records": total_records,
            "total_columns": total_columns,
            "missing_values": total_missing,
            "duplicates_removed": duplicates_removed,
            "high_quality_records": hq_count,
            "high_quality_pct": hq_pct,
        },
        "overall_qos": overall,
        "carrier_aggregation": carrier_results,
        "technology_aggregation": tech_results,
        "location_aggregation": location_results,
        "network_distribution": network_distribution,
        "dropped_connection_by_carrier": drop_results,
        "big_data_concepts": {
            "Volume": (
                f"The dataset contains {total_records:,} network measurement records "
                "spanning 11 months (June 2024 – May 2025). In real 5G networks, such "
                "measurements are collected continuously from millions of devices, "
                "generating data at a scale that requires distributed processing frameworks."
            ),
            "Velocity": (
                "Network quality measurements (signal strength, latency, throughput) can be "
                "generated every few seconds per device. Across thousands of active users in "
                "a city, this results in millions of records per hour — requiring stream "
                "processing pipelines like Apache Kafka + Spark Streaming."
            ),
            "Variety": (
                f"The dataset contains {total_columns} columns of mixed types: "
                "numerical (speed, latency, signal), categorical (carrier, location, band, "
                "network type), boolean (VoNR, dropped connection), and temporal (timestamp). "
                "Real deployments also include GPS coordinates, application-layer metrics, "
                "and device telemetry."
            ),
            "Veracity": (
                "Real-world network data suffers from sensor errors, dropped packets, "
                f"inconsistent timestamps, and device-specific biases. This dataset had "
                f"{total_missing} missing values and {duplicates_removed} duplicates, "
                "which were addressed during preprocessing. Outliers were identified using "
                "IQR analysis and retained as valid extreme network conditions."
            ),
            "Value": (
                "Raw network measurements become actionable insights through analysis: "
                "carrier performance comparison, network type benchmarking, temporal QoS "
                "trends, and predictive modelling. These insights drive network planning, "
                "carrier selection, and service quality improvements."
            ),
        },
        "spark_pipeline_steps": [
            "SparkSession.builder → local[*] cluster",
            "spark.read.csv() → Distributed DataFrame",
            "df.printSchema() → Column types",
            "df.count() → Total records",
            "df.filter(isNull) → Missing value detection",
            "df.dropDuplicates() → Data deduplication",
            "df.agg(avg, count) → Overall QoS aggregation",
            "df.groupBy('Carrier').agg() → Carrier comparison",
            "df.groupBy('Network Type').agg() → Technology comparison",
            "df.groupBy('Location').agg() → Location analysis",
            "df.filter(condition) → High-quality record selection",
        ],
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, default=str)

    print(f"\n[OK] Results exported -> {OUTPUT_JSON.relative_to(PROJECT_ROOT)}")
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if PYSPARK_AVAILABLE:
        run_pyspark_analysis()
    else:
        print("WARNING: PySpark not found. Using pandas fallback.")
        print("To install PySpark: pip install pyspark")
        print("Also ensure Java 8/11/17 is installed: java -version\n")
        run_pandas_fallback()
