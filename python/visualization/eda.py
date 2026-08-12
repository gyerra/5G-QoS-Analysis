"""Exploratory Data Analysis — generates distribution and relationship plots."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from config import (
    COL_DOWNLOAD,
    COL_JITTER,
    COL_LATENCY,
    COL_PING,
    COL_SIGNAL,
    COL_UPLOAD,
    OUTPUT_DIR,
    PLOTS_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
)

CLEANED_PATH = PROCESSED_DATA_DIR / "cleaned_dataset.csv"

DIST_COLS = [
    (COL_DOWNLOAD, "Download Speed (Mbps)"),
    (COL_UPLOAD, "Upload Speed (Mbps)"),
    (COL_LATENCY, "Latency (ms)"),
    (COL_JITTER, "Jitter (ms)"),
    (COL_SIGNAL, "Signal Strength (dBm)"),
]

SCATTER_PAIRS = [
    (COL_SIGNAL, COL_DOWNLOAD, "signal_vs_download"),
    (COL_SIGNAL, COL_LATENCY, "signal_vs_latency"),
    (COL_LATENCY, COL_DOWNLOAD, "latency_vs_download"),
    (COL_JITTER, COL_LATENCY, "jitter_vs_latency"),
]


def load_cleaned() -> pd.DataFrame:
    if not CLEANED_PATH.exists():
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "preprocessing"))
        from clean_data import clean_data
        return clean_data()
    return pd.read_csv(CLEANED_PATH, low_memory=False)


def plot_distributions(df: pd.DataFrame) -> list[str]:
    saved = []
    for col, label in DIST_COLS:
        if col not in df.columns:
            continue
        fig, axes = plt.subplots(1, 3, figsize=(14, 4))
        sns.histplot(df[col], kde=True, ax=axes[0], color="#06b6d4")
        axes[0].set_title(f"Histogram — {label}")
        sns.boxplot(x=df[col], ax=axes[1], color="#8b5cf6")
        axes[1].set_title(f"Box Plot — {label}")
        sample = df[col].sample(min(5000, len(df)), random_state=42)
        sns.kdeplot(sample, ax=axes[2], color="#3b82f6", fill=True)
        axes[2].set_title(f"KDE — {label}")
        fname = f"dist_{col.replace(' ', '_').replace('(', '').replace(')', '').lower()}.png"
        path = PLOTS_DIR / fname
        plt.tight_layout()
        fig.savefig(path, dpi=100, bbox_inches="tight")
        plt.close(fig)
        saved.append(fname)
    return saved


def plot_scatters(df: pd.DataFrame) -> list[str]:
    saved = []
    sample = df.sample(min(3000, len(df)), random_state=42)
    for x, y, name in SCATTER_PAIRS:
        if x not in df.columns or y not in df.columns:
            continue
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(sample[x], sample[y], alpha=0.3, s=8, c="#06b6d4")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"{x} vs {y}")
        fname = f"scatter_{name}.png"
        path = PLOTS_DIR / fname
        fig.savefig(path, dpi=100, bbox_inches="tight")
        plt.close(fig)
        saved.append(fname)
    return saved


def plot_correlation_heatmap(df: pd.DataFrame) -> str:
    numeric = [c for c, _ in DIST_COLS if c in df.columns]
    if COL_PING in df.columns:
        numeric.append(COL_PING)
    corr = df[numeric].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax, center=0)
    ax.set_title("QoS Correlation Heatmap")
    fname = "correlation_heatmap.png"
    path = PLOTS_DIR / fname
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return fname


def run_eda() -> dict:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_cleaned()
    dist = plot_distributions(df)
    scatters = plot_scatters(df)
    heatmap = plot_correlation_heatmap(df)
    report = {"distributions": dist, "scatter_plots": scatters, "heatmap": heatmap}
    with open(OUTPUT_DIR / "eda_report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"EDA plots saved to {PLOTS_DIR.relative_to(PROJECT_ROOT)}")
    return report


if __name__ == "__main__":
    run_eda()
