"""QoS performance analysis by carrier, technology, time, and location."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from config import (
    COL_CARRIER,
    COL_DOWNLOAD,
    COL_JITTER,
    COL_LATENCY,
    COL_LOCATION,
    COL_NETWORK,
    COL_SIGNAL,
    COL_TIMESTAMP,
    COL_UPLOAD,
    OUTPUT_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
)

CLEANED_PATH = PROCESSED_DATA_DIR / "cleaned_dataset.csv"
METRICS = [COL_DOWNLOAD, COL_UPLOAD, COL_LATENCY, COL_JITTER, COL_SIGNAL]


def load_cleaned() -> pd.DataFrame:
    if not CLEANED_PATH.exists():
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent / "preprocessing"))
        from clean_data import clean_data
        df = clean_data()
    else:
        df = pd.read_csv(CLEANED_PATH, low_memory=False)
    df[COL_TIMESTAMP] = pd.to_datetime(df[COL_TIMESTAMP])
    return df


def group_means(df: pd.DataFrame, group_col: str) -> list[dict]:
    available = [m for m in METRICS if m in df.columns]
    grouped = df.groupby(group_col)[available].mean().round(2).reset_index()
    return grouped.to_dict(orient="records")


def temporal_analysis(df: pd.DataFrame) -> dict:
    hourly = df.groupby("hour")[[m for m in METRICS if m in df.columns]].mean().round(2)
    daily = df.groupby("day_of_week")[[m for m in METRICS if m in df.columns]].mean().round(2)
    monthly = df.groupby("month")[[m for m in METRICS if m in df.columns]].mean().round(2)

    peak_hour_dl = int(hourly[COL_DOWNLOAD].idxmax()) if COL_DOWNLOAD in hourly.columns else None
    peak_hour_lat = int(hourly[COL_LATENCY].idxmax()) if COL_LATENCY in hourly.columns else None

    return {
        "hourly": {
            "labels": [int(h) for h in hourly.index],
            "download_speed": hourly[COL_DOWNLOAD].tolist() if COL_DOWNLOAD in hourly.columns else [],
            "upload_speed": hourly[COL_UPLOAD].tolist() if COL_UPLOAD in hourly.columns else [],
            "latency": hourly[COL_LATENCY].tolist() if COL_LATENCY in hourly.columns else [],
            "jitter": hourly[COL_JITTER].tolist() if COL_JITTER in hourly.columns else [],
            "signal_strength": hourly[COL_SIGNAL].tolist() if COL_SIGNAL in hourly.columns else [],
        },
        "daily": {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "download_speed": daily[COL_DOWNLOAD].tolist() if COL_DOWNLOAD in daily.columns else [],
            "latency": daily[COL_LATENCY].tolist() if COL_LATENCY in daily.columns else [],
        },
        "monthly": {
            "labels": [int(m) for m in monthly.index],
            "download_speed": monthly[COL_DOWNLOAD].tolist() if COL_DOWNLOAD in monthly.columns else [],
            "latency": monthly[COL_LATENCY].tolist() if COL_LATENCY in monthly.columns else [],
        },
        "peak_download_hour": peak_hour_dl,
        "peak_latency_hour": peak_hour_lat,
    }


def run_qos_analysis() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_cleaned()

    carrier = group_means(df, COL_CARRIER)
    technology = group_means(df, COL_NETWORK)
    location = group_means(df, COL_LOCATION)
    temporal = temporal_analysis(df)

    overall = {}
    for m in METRICS:
        if m in df.columns:
            overall[m] = round(float(df[m].mean()), 2)

    qos_summary = {
        "total_records": len(df),
        "averages": overall,
        "date_range": {
            "start": str(df[COL_TIMESTAMP].min()),
            "end": str(df[COL_TIMESTAMP].max()),
        },
        "unavailable_metrics": {
            "packet_loss_pct": "Not present in dataset — only boolean Dropped Connection available",
            "latitude_longitude": "Not present — city-level Location only",
        },
    }

    with open(OUTPUT_DIR / "carrier_analysis.json", "w", encoding="utf-8") as fh:
        json.dump(carrier, fh, indent=2)
    with open(OUTPUT_DIR / "technology_analysis.json", "w", encoding="utf-8") as fh:
        json.dump(technology, fh, indent=2)
    with open(OUTPUT_DIR / "location_analysis.json", "w", encoding="utf-8") as fh:
        json.dump(location, fh, indent=2)
    with open(OUTPUT_DIR / "temporal_analysis.json", "w", encoding="utf-8") as fh:
        json.dump(temporal, fh, indent=2)
    with open(OUTPUT_DIR / "qos_summary.json", "w", encoding="utf-8") as fh:
        json.dump(qos_summary, fh, indent=2)

    print(f"QoS analysis saved to {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")
    return qos_summary


if __name__ == "__main__":
    run_qos_analysis()
