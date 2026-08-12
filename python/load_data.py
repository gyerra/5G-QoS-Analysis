"""
STEP 2: Data Loading
Discovers CSV files, copies to raw/, loads and merges compatible datasets.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

from config import CSV_SEARCH_DIRS, PROCESSED_DATA_DIR, PROJECT_ROOT, RAW_DATA_DIR


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


def copy_to_raw(source: Path) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = RAW_DATA_DIR / source.name
    if not dest.exists() or dest.stat().st_mtime < source.stat().st_mtime:
        shutil.copy2(source, dest)
    return dest


def can_merge(dfs: list[pd.DataFrame]) -> bool:
    if len(dfs) <= 1:
        return True
    ref_cols = set(dfs[0].columns)
    return all(set(df.columns) == ref_cols for df in dfs[1:])


def load_and_merge() -> tuple[pd.DataFrame, dict]:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    sources = discover_csv_files()
    if not sources:
        raise FileNotFoundError("No CSV files found in project.")

    raw_paths = [copy_to_raw(s) for s in sources]
    frames = [pd.read_csv(p, low_memory=False) for p in raw_paths]

    meta = {
        "source_files": [str(s.relative_to(PROJECT_ROOT)) for s in sources],
        "raw_copies": [str(p.relative_to(PROJECT_ROOT)) for p in raw_paths],
        "file_rows": [len(df) for df in frames],
        "merged": False,
        "total_rows_before_dedup": sum(len(df) for df in frames),
    }

    if len(frames) == 1:
        merged = frames[0].copy()
        meta["merge_reason"] = "Single file — no merge required."
    elif can_merge(frames):
        merged = pd.concat(frames, ignore_index=True)
        meta["merged"] = True
        meta["merge_reason"] = "Identical schemas — concatenated."
    else:
        merged = frames[0].copy()
        meta["merge_reason"] = "Incompatible schemas — using first file only."

    before = len(merged)
    merged = merged.drop_duplicates()
    meta["duplicates_removed"] = before - len(merged)
    meta["final_rows"] = len(merged)
    meta["columns"] = list(merged.columns)

    out_path = PROCESSED_DATA_DIR / "loaded_dataset.csv"
    merged.to_csv(out_path, index=False)

    meta_path = PROCESSED_DATA_DIR / "load_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    print(f"Loaded {meta['final_rows']:,} rows from {len(sources)} file(s)")
    print(f"Saved to {out_path.relative_to(PROJECT_ROOT)}")
    return merged, meta


if __name__ == "__main__":
    load_and_merge()
