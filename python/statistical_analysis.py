"""Statistical analysis for QoS metrics."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from config import (
    COL_DOWNLOAD,
    COL_JITTER,
    COL_LATENCY,
    COL_PING,
    COL_SIGNAL,
    COL_UPLOAD,
    OUTPUT_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
)

CLEANED_PATH = PROCESSED_DATA_DIR / "cleaned_dataset.csv"


def load_cleaned() -> pd.DataFrame:
    if not CLEANED_PATH.exists():
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent / "preprocessing"))
        from clean_data import clean_data
        return clean_data()
    return pd.read_csv(CLEANED_PATH, low_memory=False)


def descriptive_stats(series: pd.Series) -> dict:
    return {
        "mean": round(float(series.mean()), 4),
        "median": round(float(series.median()), 4),
        "min": round(float(series.min()), 4),
        "max": round(float(series.max()), 4),
        "std": round(float(series.std()), 4),
        "variance": round(float(series.var()), 4),
        "q1": round(float(series.quantile(0.25)), 4),
        "q3": round(float(series.quantile(0.75)), 4),
        "count": int(series.count()),
    }


def compute_statistics() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_cleaned()

    metrics = {
        "download_speed_mbps": COL_DOWNLOAD,
        "upload_speed_mbps": COL_UPLOAD,
        "latency_ms": COL_LATENCY,
        "jitter_ms": COL_JITTER,
        "signal_strength_dbm": COL_SIGNAL,
        "ping_google_ms": COL_PING,
    }

    descriptive = {}
    for key, col in metrics.items():
        if col in df.columns:
            descriptive[key] = descriptive_stats(df[col])

    numeric_cols = [c for c in metrics.values() if c in df.columns]
    pearson = df[numeric_cols].corr(method="pearson").round(4)
    spearman = df[numeric_cols].corr(method="spearman").round(4)

    pearson_dict = pearson.to_dict()
    spearman_dict = spearman.to_dict()

    insights = []
    if COL_SIGNAL in df.columns and COL_DOWNLOAD in df.columns:
        r = pearson.loc[COL_SIGNAL, COL_DOWNLOAD]
        direction = "positive" if r > 0 else "negative"
        insights.append(
            f"Signal strength and download speed show a {direction} Pearson correlation "
            f"(r={r:.3f}); stronger signal conditions are associated with "
            f"{'higher' if r > 0 else 'lower'} observed download speeds in the dataset."
        )
    if COL_LATENCY in df.columns and COL_JITTER in df.columns:
        r = pearson.loc[COL_LATENCY, COL_JITTER]
        insights.append(
            f"Latency and jitter exhibit Pearson r={r:.3f}. "
            "Higher jitter tends to co-occur with latency variation in this dataset."
        )

    result = {
        "descriptive_statistics": descriptive,
        "pearson_correlation": pearson_dict,
        "spearman_correlation": spearman_dict,
        "insights": insights,
        "note": "Correlation does not imply causation.",
    }

    with open(OUTPUT_DIR / "descriptive_statistics.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)

    corr_export = {
        "columns": numeric_cols,
        "pearson": pearson_dict,
        "spearman": spearman_dict,
    }
    with open(OUTPUT_DIR / "correlations.json", "w", encoding="utf-8") as fh:
        json.dump(corr_export, fh, indent=2)

    print(f"Statistics saved to {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")
    return result


if __name__ == "__main__":
    compute_statistics()
