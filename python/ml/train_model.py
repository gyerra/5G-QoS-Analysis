"""Train and evaluate ML models for QoS prediction."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from config import (
    COL_BAND,
    COL_BATTERY,
    COL_CARRIER,
    COL_CONGESTION,
    COL_DATA_USAGE,
    COL_DEVICE,
    COL_DOWNLOAD,
    COL_DROPPED,
    COL_DURATION,
    COL_HANDOVER,
    COL_JITTER,
    COL_LATENCY,
    COL_LOCATION,
    COL_NETWORK,
    COL_PING,
    COL_SIGNAL,
    COL_TEMP,
    COL_TIMESTAMP,
    COL_UPLOAD,
    COL_VIDEO,
    COL_VONR,
    MODELS_DIR,
    OUTPUT_DIR,
    PLOTS_DIR,
    PRIMARY_TARGETS,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
    RANDOM_STATE,
    TEST_SIZE,
)

CLEANED_PATH = PROCESSED_DATA_DIR / "cleaned_dataset.csv"

MODELS = {
    "Linear Regression": LinearRegression(),
    "Decision Tree": DecisionTreeRegressor(random_state=RANDOM_STATE, max_depth=12),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1),
    "Gradient Boosting": GradientBoostingRegressor(random_state=RANDOM_STATE),
    "XGBoost": XGBRegressor(random_state=RANDOM_STATE, n_estimators=100, verbosity=0),
}


def load_cleaned() -> pd.DataFrame:
    if not CLEANED_PATH.exists():
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "preprocessing"))
        from clean_data import clean_data
        return clean_data()
    df = pd.read_csv(CLEANED_PATH, low_memory=False)
    df[COL_TIMESTAMP] = pd.to_datetime(df[COL_TIMESTAMP])
    return df


def get_features(target: str) -> list[str]:
    """Feature columns for a given target — avoids target leakage."""
    numeric = [
        COL_SIGNAL, COL_JITTER, COL_BATTERY, COL_TEMP, COL_DURATION,
        COL_HANDOVER, COL_DATA_USAGE, COL_VIDEO,
    ]
    if target == COL_LATENCY:
        # Ping is highly related to latency — exclude to reduce leakage for fair evaluation
        pass
    else:
        numeric.append(COL_PING)

    numeric = [c for c in numeric if c != target]
    categorical = [COL_NETWORK, COL_CARRIER, COL_LOCATION, COL_BAND, COL_CONGESTION, COL_DEVICE]
    boolean = [COL_VONR, COL_DROPPED]
    temporal = ["hour", "day_of_week", "month"]
    return numeric + categorical + boolean + temporal


def prepare_xy(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    features = get_features(target)
    available = [f for f in features if f in df.columns]
    X = df[available].copy()

    for col in X.select_dtypes(include=["bool"]).columns:
        X[col] = X[col].astype(int)
    for col in X.select_dtypes(include=["object"]).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

    y = df[target]
    return X, y, available


def chronological_split(X: pd.DataFrame, y: pd.Series) -> tuple:
    split_idx = int(len(X) * (1 - TEST_SIZE))
    return X.iloc[:split_idx], X.iloc[split_idx:], y.iloc[:split_idx], y.iloc[split_idx:]


def evaluate_model(y_true, y_pred) -> dict:
    return {
        "MAE": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "RMSE": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 4),
        "R2": round(float(r2_score(y_true, y_pred)), 4),
    }


def select_best(results: list[dict]) -> dict:
    """Select best model considering all three metrics — composite ranking."""
    scored = []
    for r in results:
        mae_rank = sorted(results, key=lambda x: x["MAE"])
        rmse_rank = sorted(results, key=lambda x: x["RMSE"])
        r2_rank = sorted(results, key=lambda x: x["R2"], reverse=True)
        score = (
            mae_rank.index(r) + rmse_rank.index(r) + (len(r2_rank) - 1 - r2_rank.index(r))
        )
        scored.append((score, r))
    scored.sort(key=lambda x: x[0])
    return scored[0][1]


def plot_actual_vs_predicted(y_true, y_pred, target: str, model_name: str) -> str:
    fig, ax = plt.subplots(figsize=(7, 6))
    sample_idx = np.random.choice(len(y_true), min(2000, len(y_true)), replace=False)
    ax.scatter(y_true.iloc[sample_idx], y_pred[sample_idx], alpha=0.3, s=10, c="#06b6d4")
    lims = [min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())]
    ax.plot(lims, lims, "r--", lw=1)
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.set_title(f"Actual vs Predicted — {target}\n({model_name})")
    safe = target.replace(" ", "_").replace("(", "").replace(")", "").lower()
    fname = f"actual_vs_pred_{safe}.png"
    fig.savefig(PLOTS_DIR / fname, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return fname


def plot_residuals(y_true, y_pred, target: str, model_name: str) -> str:
    residuals = y_true.values - y_pred
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(y_pred, residuals, alpha=0.3, s=10, c="#8b5cf6")
    ax.axhline(0, color="r", linestyle="--")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Residual")
    ax.set_title(f"Residual Plot — {target}\n({model_name})")
    safe = target.replace(" ", "_").replace("(", "").replace(")", "").lower()
    fname = f"residuals_{safe}.png"
    fig.savefig(PLOTS_DIR / fname, dpi=100, bbox_inches="tight")
    plt.close(fig)
    return fname


def get_feature_importance(model, feature_names: list[str]) -> list[dict]:
    if hasattr(model, "feature_importances_"):
        imp = model.feature_importances_
    elif hasattr(model, "coef_"):
        imp = np.abs(model.coef_)
    else:
        return []
    pairs = sorted(zip(feature_names, imp), key=lambda x: x[1], reverse=True)
    return [{"feature": f, "importance": round(float(v), 4)} for f, v in pairs[:15]]


def train_for_target(df: pd.DataFrame, target: str) -> dict:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    X, y, feature_names = prepare_xy(df, target)
    X_train, X_test, y_train, y_test = chronological_split(X, y)

    comparison = []
    best_model = None
    best_name = None
    best_pred = None

    for name, model in MODELS.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        metrics = evaluate_model(y_test, pred)
        comparison.append({"model": name, **metrics})

    best = select_best(comparison)
    best_name = best["model"]
    best_model = MODELS[best_name]
    best_model.fit(X_train, y_train)
    best_pred = best_model.predict(X_test)

    safe_target = target.replace(" ", "_").replace("(", "").replace(")", "").lower()
    model_path = MODELS_DIR / f"best_{safe_target}.joblib"
    joblib.dump({"model": best_model, "features": feature_names, "target": target}, model_path)

    avp = plot_actual_vs_predicted(y_test, best_pred, target, best_name)
    res = plot_residuals(y_test, best_pred, target, best_name)
    importance = get_feature_importance(best_model, feature_names)

    # Sample predictions for frontend chart
    n = min(500, len(y_test))
    idx = np.linspace(0, len(y_test) - 1, n, dtype=int)
    prediction_chart = {
        "actual": [round(float(v), 2) for v in y_test.iloc[idx].values],
        "predicted": [round(float(v), 2) for v in best_pred[idx]],
    }

    return {
        "target": target,
        "split_method": "chronological (80/20) — data is time-dependent",
        "train_size": len(X_train),
        "test_size": len(X_test),
        "features": feature_names,
        "comparison": comparison,
        "best_model": best_name,
        "best_metrics": best,
        "feature_importance": importance,
        "plots": {"actual_vs_predicted": avp, "residuals": res},
        "prediction_chart": prediction_chart,
        "model_file": str(model_path.relative_to(PROJECT_ROOT)),
    }


def train_all() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_cleaned()

    results = {}
    all_comparison = []
    all_importance = {}

    for target in PRIMARY_TARGETS:
        result = train_for_target(df, target)
        results[target] = result
        for row in result["comparison"]:
            all_comparison.append({"target": target, **row})
        all_importance[target] = {
            "best_model": result["best_model"],
            "features": result["feature_importance"],
        }

    pd.DataFrame(all_comparison).to_csv(OUTPUT_DIR / "model_comparison.csv", index=False)

    with open(OUTPUT_DIR / "model_comparison.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, default=str)

    with open(OUTPUT_DIR / "feature_selection.json", "w", encoding="utf-8") as fh:
        json.dump(
            {t: results[t]["features"] for t in PRIMARY_TARGETS},
            fh, indent=2,
        )

    with open(OUTPUT_DIR / "feature_importance.json", "w", encoding="utf-8") as fh:
        json.dump(all_importance, fh, indent=2)

    print(f"Models trained. Comparison saved to {OUTPUT_DIR.relative_to(PROJECT_ROOT)}")
    return results


if __name__ == "__main__":
    train_all()
