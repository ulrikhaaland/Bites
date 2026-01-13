from __future__ import annotations

import json
from typing import Sequence

import numpy as np
import pandas as pd
import ruptures as rpt

COMPLETENESS_THRESHOLD = 0.8


def compute_completeness(days: pd.DataFrame) -> pd.DataFrame:
    days = days.copy()
    macro_cols = ["calories", "protein_g", "carbs_g", "fat_g"]
    missing_macros = days[macro_cols].isna().mean(axis=1)
    low_kcal = days["calories"].fillna(0) < 800
    days["completeness_score"] = (1 - missing_macros) * (~low_kcal).astype(float)
    return days


def compute_metrics_daily(foods: pd.DataFrame, days: pd.DataFrame) -> pd.DataFrame:
    days = days.copy()
    days = compute_completeness(days)

    meal_counts = (
        foods.groupby(["date", "meal"], dropna=False)
        .agg(protein_g=("protein_g", "sum"))
        .reset_index()
    )
    protein_meals_ge_30g = (
        meal_counts.assign(ge30=lambda df: df["protein_g"] >= 30)
        .groupby("date")["ge30"]
        .sum()
        .rename("protein_meals_ge_30g")
    )

    protein_per_meal_avg = (
        meal_counts.groupby("date")["protein_g"].mean().rename("protein_per_meal_avg")
    )

    upf_proxy = (
        foods.groupby("date")["is_packaged"].mean().fillna(0).rename("upf_proxy")
    )

    total_grams = foods.groupby("date")["amount"].sum().rename("total_grams")
    energy_density = (
        days.set_index("date")["calories"]
        .div(total_grams)
        .replace([np.inf, -np.inf], np.nan)
        .rename("energy_density")
    )

    metrics = days.set_index("date")[["calories", "protein_g", "fiber_g"]].rename(
        columns={"calories": "kcal"}
    )

    metrics = metrics.join([protein_per_meal_avg, protein_meals_ge_30g, upf_proxy])
    metrics["fiber_per_1000kcal"] = (
        metrics["fiber_g"] / metrics["kcal"] * 1000
    )

    metrics = metrics.join(energy_density)
    metrics["flags_json"] = metrics.apply(
        lambda row: json.dumps(
            {
                "missing_kcal": pd.isna(row["kcal"]),
                "missing_protein": pd.isna(row["protein_g"]),
                "missing_fiber": pd.isna(row["fiber_g"]),
            }
        ),
        axis=1,
    )

    metrics = _add_rolling_stats(metrics)
    metrics = metrics.reset_index()
    return metrics


def _add_rolling_stats(metrics: pd.DataFrame) -> pd.DataFrame:
    metrics = metrics.sort_index()
    for window, suffix in [(7, "7d"), (30, "30d")]:
        metrics[f"kcal_mean_{suffix}"] = metrics["kcal"].rolling(window).mean()
        metrics[f"kcal_std_{suffix}"] = metrics["kcal"].rolling(window).std()
        metrics[f"protein_mean_{suffix}"] = metrics["protein_g"].rolling(window).mean()
        metrics[f"protein_std_{suffix}"] = metrics["protein_g"].rolling(window).std()
        metrics[f"fiber_mean_{suffix}"] = metrics["fiber_g"].rolling(window).mean()
        metrics[f"fiber_std_{suffix}"] = metrics["fiber_g"].rolling(window).std()
    return metrics


def detect_phases(days: pd.DataFrame) -> Sequence[dict[str, str]]:
    series = days[["calories", "protein_g", "carbs_g"]].fillna(0).values
    if len(series) < 10:
        return []
    model = rpt.Pelt(model="rbf").fit(series)
    breakpoints = model.predict(pen=5)

    phases = []
    start_idx = 0
    for end_idx in breakpoints:
        segment = days.iloc[start_idx:end_idx]
        if segment.empty:
            continue
        deltas = segment[["calories", "protein_g", "carbs_g"]].mean().to_dict()
        label = _label_phase(deltas)
        phases.append(
            {
                "start_date": str(segment["date"].iloc[0]),
                "end_date": str(segment["date"].iloc[-1]),
                "label": label,
                "deltas_json": json.dumps(deltas),
            }
        )
        start_idx = end_idx
    return phases


def _label_phase(deltas: dict[str, float]) -> str:
    protein = deltas.get("protein_g", 0)
    carbs = deltas.get("carbs_g", 0)
    if protein >= 140:
        return "Higher-protein phase"
    if carbs < 150:
        return "Lower-carb phase"
    return "Balanced phase"
