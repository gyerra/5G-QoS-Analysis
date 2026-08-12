"""
STEP 3: Data Preprocessing
Cleans, types, encodes, and scales the dataset for analysis and ML.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

from config import (
    COL_CARRIER,
    COL_CONGESTION,
    COL_DEVICE,
    COL_DOWNLOAD,
    COL_LATENCY,
    COL_LOCATION,
    COL_NETWORK,
    COL_TIMESTAMP,
    COL_UPLOAD,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
    QOS_CATEGORICAL,
    QOS_NUMERIC,
)

LOADED_PATH = PROCESSED_DATA_DIR / "loaded_dataset.csv"
CLEANED_PATH = PROCESSED_DATA_DIR / "cleaned_dataset.csv"
ENCODERS_PATH = PROCESSED_DATA_DIR / "label_encoders.json"
OUTLIER_PATH = PROCESSED_DATA_DIR / "outlier_report.json"


def load_dataset() -> pd.DataFrame:
    if not LOADED_PATH.exists():
        from load_data import load_and_merge

        df, _ = load_and_merge()
        return df
    return pd.read_csv(LOADED_PATH, low_memory=False)


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[COL_TIMESTAMP] = pd.to_datetime(df[COL_TIMESTAMP])
    df["hour"] = df[COL_TIMESTAMP].dt.hour
    df["day_of_week"] = df[COL_TIMESTAMP].dt.dayofweek
    df["month"] = df[COL_TIMESTAMP].dt.month
    df["date"] = df[COL_TIMESTAMP].dt.date.astype(str)
    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    report = {}
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            fill = df[col].median()
            df[col] = df[col].fillna(fill)
            report[col] = {"strategy": "median", "value": float(fill)}
        else:
            fill = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(fill)
            report[col] = {"strategy": "mode", "value": str(fill)}
    return df, report


def detect_outliers_iqr(df: pd.DataFrame, columns: list[str]) -> dict:
    report = {}
    numeric_cols = [c for c in columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        report[col] = {
            "method": "IQR",
            "lower_bound": round(float(lower), 4),
            "upper_bound": round(float(upper), 4),
            "outlier_count": int(len(outliers)),
            "outlier_pct": round(len(outliers) / len(df) * 100, 2),
            "action": "retained — may represent legitimate network conditions",
        }
    return report


def encode_categoricals(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = df.copy()
    encoders = {}
    cat_cols = [c for c in QOS_CATEGORICAL if c in df.columns]
    for col in cat_cols:
        le = LabelEncoder()
        df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
        encoders[col] = {str(i): cls for i, cls in enumerate(le.classes_)}
    bool_cols = [c for c in df.columns if df[c].dtype == bool]
    for col in bool_cols:
        df[f"{col}_encoded"] = df[col].astype(int)
    return df, encoders


def clean_data() -> pd.DataFrame:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()
    initial_rows = len(df)

    df = df.drop_duplicates()
    df, missing_report = handle_missing(df)
    df = parse_timestamps(df)
    outlier_report = detect_outliers_iqr(df, QOS_NUMERIC + [COL_DOWNLOAD, COL_UPLOAD, COL_LATENCY])
    df, encoders = encode_categoricals(df)

    df = df.sort_values(COL_TIMESTAMP).reset_index(drop=True)
    df.to_csv(CLEANED_PATH, index=False)

    with open(ENCODERS_PATH, "w", encoding="utf-8") as fh:
        json.dump(encoders, fh, indent=2)
    with open(OUTLIER_PATH, "w", encoding="utf-8") as fh:
        json.dump(outlier_report, fh, indent=2)

    summary = {
        "initial_rows": initial_rows,
        "final_rows": len(df),
        "duplicates_removed": initial_rows - len(df),
        "missing_treatment": missing_report,
        "outliers_retained": True,
        "timestamp_parsed": True,
        "columns_added": ["hour", "day_of_week", "month", "date"],
    }
    with open(PROCESSED_DATA_DIR / "preprocessing_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(f"Cleaned dataset: {len(df):,} rows -> {CLEANED_PATH.relative_to(PROJECT_ROOT)}")
    return df


if __name__ == "__main__":
    clean_data()
