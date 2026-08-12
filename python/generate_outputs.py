"""Generate insights and copy outputs for frontend consumption."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config import (
    COL_CARRIER,
    COL_DOWNLOAD,
    COL_LATENCY,
    COL_LOCATION,
    COL_NETWORK,
    COL_SIGNAL,
    FRONTEND_DATA_DIR,
    OUTPUT_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
)

CLEANED_PATH = PROCESSED_DATA_DIR / "cleaned_dataset.csv"


def load_json(name: str) -> dict | list:
    path = OUTPUT_DIR / name
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def generate_insights() -> dict:
    carrier = load_json("carrier_analysis.json")
    tech = load_json("technology_analysis.json")
    corr = load_json("correlations.json")
    model = load_json("model_comparison.json")
    feat_imp = load_json("feature_importance.json")
    qos = load_json("qos_summary.json")

    insights = []

    if carrier:
        best_c = max(carrier, key=lambda x: x.get("Download Speed (Mbps)", 0))
        insights.append({
            "category": "Carrier",
            "title": "Best Download Speed by Carrier",
            "value": f"{best_c[COL_CARRIER]} — {best_c['Download Speed (Mbps)']} Mbps avg",
            "detail": "Computed from mean download speed grouped by carrier.",
        })
        best_lat = min(carrier, key=lambda x: x.get("Latency (ms)", 999))
        insights.append({
            "category": "Carrier",
            "title": "Lowest Latency Carrier",
            "value": f"{best_lat[COL_CARRIER]} — {best_lat['Latency (ms)']} ms avg",
            "detail": "Computed from mean latency grouped by carrier.",
        })

    if tech:
        best_tech = max(tech, key=lambda x: x.get("Download Speed (Mbps)", 0))
        insights.append({
            "category": "Technology",
            "title": "Highest Avg Download by Network Type",
            "value": f"{best_tech[COL_NETWORK]} — {best_tech['Download Speed (Mbps)']} Mbps",
            "detail": "Compares 4G, 5G NSA, and 5G SA performance.",
        })

    if corr and corr.get("pearson"):
        cols = corr.get("columns", [])
        max_r, max_pair = 0, ("", "")
        pearson = corr["pearson"]
        for i, c1 in enumerate(cols):
            for c2 in cols[i + 1:]:
                r = abs(pearson.get(c1, {}).get(c2, 0))
                if r > max_r:
                    max_r, max_pair = r, (c1, c2)
        if max_pair[0]:
            insights.append({
                "category": "Correlation",
                "title": "Strongest QoS Correlation",
                "value": f"{max_pair[0]} ↔ {max_pair[1]} (r={max_r:.3f})",
                "detail": "Pearson correlation between numerical QoS parameters.",
            })

    for target, data in (model or {}).items():
        if isinstance(data, dict) and "best_model" in data:
            m = data["best_metrics"]
            insights.append({
                "category": "ML",
                "title": f"Best Model for {target}",
                "value": f"{data['best_model']} — MAE={m['MAE']}, RMSE={m['RMSE']}, R²={m['R2']}",
                "detail": "Selected using composite ranking across MAE, RMSE, and R².",
            })

    if feat_imp:
        for target, fi in feat_imp.items():
            if fi.get("features"):
                top = fi["features"][0]
                insights.append({
                    "category": "Feature Importance",
                    "title": f"Top Feature for {target}",
                    "value": f"{top['feature']} (importance={top['importance']})",
                    "detail": f"From {fi['best_model']} feature importance.",
                })

    if qos and qos.get("averages"):
        avgs = qos["averages"]
        insights.append({
            "category": "Overview",
            "title": "Dataset Overview",
            "value": f"{qos['total_records']:,} records | Avg DL: {avgs.get(COL_DOWNLOAD, 'N/A')} Mbps",
            "detail": "Historical network analytics from processed dataset.",
        })

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "insights": insights,
    }
    with open(OUTPUT_DIR / "insights.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    return result


def copy_to_frontend():
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = [
        "dataset_summary.json",
        "descriptive_statistics.json",
        "correlations.json",
        "qos_summary.json",
        "carrier_analysis.json",
        "technology_analysis.json",
        "temporal_analysis.json",
        "location_analysis.json",
        "model_comparison.json",
        "feature_importance.json",
        "feature_selection.json",
        "insights.json",
        "eda_report.json",
    ]
    for f in files:
        src = OUTPUT_DIR / f
        if src.exists():
            shutil.copy2(src, FRONTEND_DATA_DIR / f)

    cleaned = PROCESSED_DATA_DIR / "cleaned_dataset.csv"
    if cleaned.exists():
        df = pd.read_csv(cleaned, nrows=5000)
        df.to_csv(FRONTEND_DATA_DIR / "sample_records.csv", index=False)
        df.to_json(FRONTEND_DATA_DIR / "sample_records.json", orient="records", date_format="iso")

    meta = {
        "last_processed": datetime.now(timezone.utc).isoformat(),
        "total_records": int(pd.read_csv(cleaned, usecols=[0]).shape[0]) if cleaned.exists() else 0,
        "data_source": "Historical CSV dataset — not live telecom feed",
    }
    with open(FRONTEND_DATA_DIR / "meta.json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    plots_src = OUTPUT_DIR / "plots"
    plots_dest = PROJECT_ROOT / "public" / "plots"
    if plots_src.exists():
        if plots_dest.exists():
            shutil.rmtree(plots_dest)
        shutil.copytree(plots_src, plots_dest)

    print(f"Frontend data copied to {FRONTEND_DATA_DIR.relative_to(PROJECT_ROOT)}")


def generate_all():
    generate_insights()
    copy_to_frontend()


if __name__ == "__main__":
    generate_all()
