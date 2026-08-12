"""
STEP 1: Dataset Inspection
Automatically discovers and profiles all CSV files in the project.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "python" / "output"

# Search locations for CSV files (per project spec + actual layout)
CSV_SEARCH_DIRS = [
    PROJECT_ROOT / "QOS Analysis",
    PROJECT_ROOT,
]

QOS_KEYWORDS = {
    "download_speed": [
        r"download\s*speed",
        r"dl\s*speed",
        r"throughput.*down",
    ],
    "upload_speed": [
        r"upload\s*speed",
        r"ul\s*speed",
        r"throughput.*up",
    ],
    "latency": [r"^latency", r"\blatency\b", r"\brtt\b"],
    "jitter": [r"jitter"],
        "packet_loss": [r"packet\s*loss", r"loss\s*rate"],
        "dropped_connection": [r"dropped\s*connection"],
    "signal_strength": [r"signal\s*strength", r"\brsrp\b", r"\brssi\b", r"dbm"],
    "network_technology": [r"network\s*type", r"\btechnology\b", r"\brat\b", r"\bgeneration\b"],
    "carrier": [r"carrier", r"operator", r"mno"],
    "location": [r"location", r"city", r"region", r"area"],
    "timestamp": [r"timestamp", r"datetime", r"date\s*time", r"time"],
    "geographic": [r"latitude", r"longitude", r"lat\b", r"lon\b", r"geo"],
}


def discover_csv_files() -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for directory in CSV_SEARCH_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.csv")):
            key = str(path.resolve())
            if key not in seen:
                seen.add(key)
                found.append(path)
    return found


def classify_column(name: str, series: pd.Series) -> dict:
    name_lower = name.lower()
    col_info: dict = {"name": name}

    # QoS role detection
    qos_roles = []
    for role, patterns in QOS_KEYWORDS.items():
        if any(re.search(p, name_lower) for p in patterns):
            qos_roles.append(role)
    col_info["qos_roles"] = qos_roles

    # Type classification (bool before numeric — pandas treats bool as numeric)
    if pd.api.types.is_bool_dtype(series):
        col_info["category"] = "boolean"
    elif pd.api.types.is_datetime64_any_dtype(series):
        col_info["category"] = "datetime"
    elif pd.api.types.is_numeric_dtype(series):
        col_info["category"] = "numerical"
    else:
        # Try parsing as datetime for object columns
        if any(k in name_lower for k in ("timestamp", "datetime", "date", "time")):
            parsed = pd.to_datetime(series, errors="coerce")
            if parsed.notna().mean() > 0.9:
                col_info["category"] = "datetime_candidate"
            else:
                col_info["category"] = "categorical"
        elif any(k in name_lower for k in ("latitude", "longitude", "lat", "lon")):
            col_info["category"] = "geographic"
        elif series.nunique(dropna=True) <= min(50, max(1, len(series) // 20)):
            col_info["category"] = "categorical"
        else:
            col_info["category"] = "text_or_high_cardinality"

    return col_info


def profile_dataframe(path: Path) -> dict:
    df = pd.read_csv(path, low_memory=False)
    rows, cols = df.shape

    column_profiles = []
    numerical_cols = []
    categorical_cols = []
    datetime_cols = []
    geographic_cols = []
    qos_related_cols = []

    for col in df.columns:
        series = df[col]
        info = classify_column(col, series)
        missing = int(series.isna().sum())
        missing_pct = round(missing / rows * 100, 4) if rows else 0.0
        dtype = str(series.dtype)
        nunique = int(series.nunique(dropna=True))

        profile = {
            "column": col,
            "dtype": dtype,
            "category": info["category"],
            "qos_roles": info["qos_roles"],
            "missing_count": missing,
            "missing_pct": missing_pct,
            "unique_count": nunique,
        }

        if info["category"] == "numerical":
            numerical_cols.append(col)
            profile["min"] = float(series.min()) if pd.notna(series.min()) else None
            profile["max"] = float(series.max()) if pd.notna(series.max()) else None
            profile["mean"] = round(float(series.mean()), 4) if pd.notna(series.mean()) else None
        elif info["category"] in ("categorical", "boolean", "text_or_high_cardinality"):
            categorical_cols.append(col)
            if nunique <= 30:
                profile["sample_values"] = series.dropna().astype(str).unique()[:15].tolist()
        elif info["category"] in ("datetime", "datetime_candidate"):
            datetime_cols.append(col)
        elif info["category"] == "geographic":
            geographic_cols.append(col)

        if info["qos_roles"]:
            qos_related_cols.append({"column": col, "roles": info["qos_roles"]})

        column_profiles.append(profile)

    duplicate_rows = int(df.duplicated().sum())

    # Merge compatibility (single file for now, but check structure)
    merge_notes = {
        "can_merge_with_others": False,
        "reason": "Only one CSV file found; no merge required.",
    }

    # Recommended targets and features
    target_candidates = []
    feature_candidates = []

    target_map = {
        "download_speed": "Download Speed (Mbps)",
        "latency": "Latency (ms)",
        "upload_speed": "Upload Speed (Mbps)",
    }
    for role, col_name in target_map.items():
        matched = [c["column"] for c in column_profiles if role in c["qos_roles"]]
        if matched:
            target_candidates.append({"role": role, "column": matched[0]})

    feature_roles = [
        "signal_strength",
        "jitter",
        "dropped_connection",
        "network_technology",
        "carrier",
        "location",
        "timestamp",
    ]
    for role in feature_roles:
        matched = [c["column"] for c in column_profiles if role in c["qos_roles"]]
        for m in matched:
            feature_candidates.append({"role": role, "column": m})

    # Additional useful numeric features not in qos keywords
    extra_features = [
        c["column"]
        for c in column_profiles
        if c["category"] == "numerical"
        and not c["qos_roles"]
        and c["column"] not in [t["column"] for t in target_candidates]
    ]
    for col in extra_features:
        feature_candidates.append({"role": "other_numeric", "column": col})

    data_quality_issues = []
    if duplicate_rows > 0:
        data_quality_issues.append(
            f"{duplicate_rows} exact duplicate rows ({duplicate_rows/rows*100:.2f}%)"
        )
    high_missing = [c for c in column_profiles if c["missing_pct"] > 5]
    if high_missing:
        data_quality_issues.append(
            "Columns with >5% missing: "
            + ", ".join(f"{c['column']} ({c['missing_pct']}%)" for c in high_missing)
        )
    if not high_missing:
        any_missing = [c for c in column_profiles if c["missing_count"] > 0]
        if any_missing:
            data_quality_issues.append(
                "Minor missing values in: "
                + ", ".join(f"{c['column']} ({c['missing_count']})" for c in any_missing)
            )
        else:
            data_quality_issues.append("No missing values detected.")

    return {
        "filename": path.name,
        "filepath": str(path.relative_to(PROJECT_ROOT)),
        "rows": rows,
        "columns": cols,
        "column_names": list(df.columns),
        "duplicate_rows": duplicate_rows,
        "column_profiles": column_profiles,
        "numerical_columns": numerical_cols,
        "categorical_columns": categorical_cols,
        "datetime_columns": datetime_cols,
        "geographic_columns": geographic_cols,
        "qos_related_columns": qos_related_cols,
        "merge_notes": merge_notes,
        "recommended_targets": target_candidates,
        "potential_ml_features": feature_candidates,
        "data_quality_issues": data_quality_issues,
    }


def build_unavailable_qos(all_profiles: list[dict]) -> list[str]:
    found_roles = set()
    for p in all_profiles:
        for q in p["qos_related_columns"]:
            found_roles.update(q["roles"])

    expected = [
        "download_speed",
        "upload_speed",
        "latency",
        "jitter",
        "packet_loss",
        "dropped_connection",
        "signal_strength",
        "network_technology",
        "carrier",
        "location",
        "timestamp",
    ]
    return [r for r in expected if r not in found_roles]


def generate_markdown_report(summary: dict) -> str:
    lines = [
        "# 5G Network Dataset — Data Profile Report",
        "",
        f"**Generated:** {summary['generated_at']}",
        f"**Inspection script:** `python/inspect_dataset.py`",
        "",
        "## 1. Files Found",
        "",
    ]

    if not summary["files"]:
        lines.append("*No CSV files found.*")
    else:
        for f in summary["files"]:
            lines.append(f"- `{f['filepath']}` — **{f['rows']:,}** rows × **{f['columns']}** columns")

    lines.extend(["", "## 2. Merge Recommendation", ""])
    if len(summary["files"]) == 1:
        lines.append(
            "A single CSV file was found. **Analyse as a standalone dataset** — no merge required."
        )
    else:
        lines.append("Multiple files detected — see merge analysis in JSON summary.")

    lines.extend(["", "## 3. Column Overview", ""])
    for f in summary["files"]:
        lines.extend([f"### {f['filename']}", "", "| Column | Type | Category | Missing | Unique | QoS Roles |", "| --- | --- | --- | --- | --- | --- |"])
        for c in f["column_profiles"]:
            roles = ", ".join(c["qos_roles"]) if c["qos_roles"] else "—"
            lines.append(
                f"| {c['column']} | {c['dtype']} | {c['category']} | "
                f"{c['missing_count']} ({c['missing_pct']}%) | {c['unique_count']} | {roles} |"
            )
        lines.append("")

    lines.extend(["## 4. QoS Metrics Availability", ""])
    unavailable = summary["unavailable_qos_metrics"]
    for role in [
        "download_speed",
        "upload_speed",
        "latency",
        "jitter",
        "packet_loss",
        "dropped_connection",
        "signal_strength",
        "network_technology",
        "carrier",
        "location",
        "timestamp",
    ]:
        status = "Available" if role not in unavailable else "**NOT AVAILABLE**"
        matched = []
        for f in summary["files"]:
            for q in f["qos_related_columns"]:
                if role in q["roles"]:
                    matched.append(q["column"])
        col_str = f" (`{', '.join(matched)}`)" if matched else ""
        lines.append(f"- **{role.replace('_', ' ').title()}**: {status}{col_str}")

    lines.extend(["", "## 5. Data Quality", ""])
    for f in summary["files"]:
        lines.append(f"### {f['filename']}")
        lines.append(f"- Duplicate rows: **{f['duplicate_rows']:,}**")
        for issue in f["data_quality_issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    lines.extend(["## 6. Recommended ML Targets", ""])
    for f in summary["files"]:
        for t in f["recommended_targets"]:
            lines.append(f"- **{t['role']}** → `{t['column']}`")

    lines.extend(["", "## 7. Potential ML Features", ""])
    for f in summary["files"]:
        for feat in f["potential_ml_features"]:
            lines.append(f"- `{feat['column']}` ({feat['role']})")

    lines.extend(["", "## 8. Data Quality Impact on Project", ""])
    for note in summary.get("project_impact_notes", []):
        lines.append(f"- {note}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = discover_csv_files()
    file_profiles = [profile_dataframe(p) for p in csv_files]

    unavailable = build_unavailable_qos(file_profiles)

    project_impact = []
    if not csv_files:
        project_impact.append("No CSV files found — pipeline cannot proceed.")
    else:
        total_rows = sum(f["rows"] for f in file_profiles)
        project_impact.append(f"Dataset contains {total_rows:,} records — sufficient for EDA and ML.")
        if unavailable:
            project_impact.append(
                f"Unavailable QoS metrics ({', '.join(unavailable)}) will be excluded from analysis."
            )
        dup_total = sum(f["duplicate_rows"] for f in file_profiles)
        if dup_total:
            project_impact.append(
                f"{dup_total:,} duplicate rows should be reviewed during preprocessing."
            )
        if "timestamp" not in unavailable:
            project_impact.append(
                "Timestamp column present — chronological train/test split recommended for ML."
            )
        if "packet_loss" in unavailable:
            project_impact.append(
                "No continuous packet-loss percentage column; 'Dropped Connection' (boolean) is available as a drop-event indicator only."
            )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "search_directories": [str(d.relative_to(PROJECT_ROOT)) for d in CSV_SEARCH_DIRS],
        "files_found": len(csv_files),
        "files": file_profiles,
        "unavailable_qos_metrics": unavailable,
        "merge_recommendation": (
            "Single file — analyse standalone, no merge."
            if len(csv_files) <= 1
            else "Review column compatibility before merging."
        ),
        "project_impact_notes": project_impact,
    }

    # JSON output
    json_path = OUTPUT_DIR / "dataset_summary.json"
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)

    # CSV summary (flattened per column)
    rows_for_csv = []
    for f in file_profiles:
        for c in f["column_profiles"]:
            rows_for_csv.append(
                {
                    "filename": f["filename"],
                    "column": c["column"],
                    "dtype": c["dtype"],
                    "category": c["category"],
                    "missing_count": c["missing_count"],
                    "missing_pct": c["missing_pct"],
                    "unique_count": c["unique_count"],
                    "qos_roles": "|".join(c["qos_roles"]) if c["qos_roles"] else "",
                }
            )
    pd.DataFrame(rows_for_csv).to_csv(OUTPUT_DIR / "dataset_summary.csv", index=False)

    # Markdown report
    md_path = OUTPUT_DIR / "data_profile.md"
    md_path.write_text(generate_markdown_report(summary), encoding="utf-8")

    print(f"Inspected {len(csv_files)} CSV file(s)")
    for f in file_profiles:
        print(f"  - {f['filename']}: {f['rows']:,} rows, {f['columns']} columns, {f['duplicate_rows']} duplicates")
    print(f"Outputs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
