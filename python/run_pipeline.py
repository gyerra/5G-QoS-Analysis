"""Master script — runs the complete Python pipeline in order."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_data import load_and_merge
from preprocessing.clean_data import clean_data
from statistical_analysis import compute_statistics
from qos_analysis import run_qos_analysis
from visualization.eda import run_eda
from ml.train_model import train_all
from generate_outputs import generate_all


def main():
    print("=" * 60)
    print("5G QoS Analysis Pipeline")
    print("=" * 60)

    steps = [
        ("1/7 Load Data", load_and_merge),
        ("2/7 Preprocess", clean_data),
        ("3/7 Statistics", compute_statistics),
        ("4/7 QoS Analysis", run_qos_analysis),
        ("5/7 EDA", run_eda),
        ("6/7 ML Training", train_all),
        ("7/7 Generate Outputs", generate_all),
    ]

    for label, fn in steps:
        print(f"\n--- {label} ---")
        fn()

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
