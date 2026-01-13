from __future__ import annotations

import io
import json
import re
import zipfile
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

MEAL_MAP = {
    "breakfast": "breakfast",
    "lunch": "lunch",
    "dinner": "dinner",
    "snack": "snack",
    "snacks": "snack",
}

PACKAGE_KEYWORDS = [
    "bar",
    "protein bar",
    "pizza",
    "chips",
    "cookie",
    "cracker",
    "soda",
    "cereal",
    "wrap",
    "frozen",
]


@dataclass
class ParsedData:
    foods: pd.DataFrame
    days: pd.DataFrame
    meals: pd.DataFrame


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [re.sub(r"\s+", " ", col.strip().lower()) for col in df.columns]
    return df


def _read_csv_bytes(content: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(content))


def _extract_files(files: Iterable[tuple[str, bytes]]) -> dict[str, bytes]:
    extracted: dict[str, bytes] = {}
    for filename, content in files:
        if filename.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                for member in archive.namelist():
                    if member.lower().endswith(".csv"):
                        extracted[member] = archive.read(member)
        elif filename.lower().endswith(".csv"):
            extracted[filename] = content
    return extracted


def _detect_source(files: dict[str, bytes], required: list[str]) -> dict[str, bytes]:
    matches = {}
    for name, content in files.items():
        lowered = name.lower()
        if any(key in lowered for key in required):
            matches[name] = content
    return matches


def _coerce_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _map_meal(value: str) -> str:
    if not isinstance(value, str):
        return "other"
    key = value.strip().lower()
    return MEAL_MAP.get(key, "other")


def parse_mfp_export(files: Iterable[tuple[str, bytes]]) -> ParsedData:
    extracted = _extract_files(files)
    if not extracted:
        raise ValueError("No CSV files detected in upload.")

    food_candidates = _detect_source(extracted, ["food", "diary", "entries"])
    day_candidates = _detect_source(extracted, ["daily", "nutrition", "summary", "totals"])

    if not food_candidates:
        raise ValueError("No diary entries CSV detected.")
    if not day_candidates:
        raise ValueError("No daily totals CSV detected.")

    foods_df = _normalize_columns(_read_csv_bytes(next(iter(food_candidates.values()))))
    days_df = _normalize_columns(_read_csv_bytes(next(iter(day_candidates.values()))))

    foods_df = foods_df.rename(
        columns={
            "date": "date",
            "meal": "meal",
            "food": "name",
            "food name": "name",
            "brand": "brand",
            "quantity": "amount",
            "amount": "amount",
            "unit": "unit",
            "calories": "calories",
            "protein (g)": "protein_g",
            "protein": "protein_g",
            "carbohydrates": "carbs_g",
            "carbs": "carbs_g",
            "fat": "fat_g",
            "fiber": "fiber_g",
            "sugar": "sugar_g",
            "saturated fat": "satfat_g",
            "sodium": "sodium_mg",
        }
    )

    days_df = days_df.rename(
        columns={
            "date": "date",
            "calories": "calories",
            "protein": "protein_g",
            "protein (g)": "protein_g",
            "carbohydrates": "carbs_g",
            "carbs": "carbs_g",
            "fat": "fat_g",
            "fiber": "fiber_g",
            "sugar": "sugar_g",
            "saturated fat": "satfat_g",
            "sodium": "sodium_mg",
        }
    )

    foods_df["meal"] = foods_df.get("meal", "other").apply(_map_meal)
    foods_df["date"] = pd.to_datetime(foods_df["date"]).dt.date
    days_df["date"] = pd.to_datetime(days_df["date"]).dt.date

    foods_df = _coerce_numeric(
        foods_df,
        [
            "amount",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "fiber_g",
            "sugar_g",
            "satfat_g",
            "sodium_mg",
        ],
    )
    days_df = _coerce_numeric(
        days_df,
        [
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "fiber_g",
            "sugar_g",
            "satfat_g",
            "sodium_mg",
        ],
    )

    foods_df["source"] = "mfp"
    foods_df["extra_json"] = None

    meals_df = (
        foods_df.groupby(["date", "meal"], dropna=False)
        .agg(
            calories=("calories", "sum"),
            protein_g=("protein_g", "sum"),
            carbs_g=("carbs_g", "sum"),
            fat_g=("fat_g", "sum"),
            fiber_g=("fiber_g", "sum"),
            sugar_g=("sugar_g", "sum"),
            satfat_g=("satfat_g", "sum"),
            sodium_mg=("sodium_mg", "sum"),
        )
        .reset_index()
    )

    foods_df["brand"] = foods_df["brand"].fillna("")
    foods_df["name"] = foods_df["name"].fillna("")

    foods_df["is_packaged"] = foods_df.apply(
        lambda row: _is_packaged(row["name"], row["brand"]), axis=1
    )

    days_df["source_json"] = days_df.apply(lambda _: json.dumps({"source": "mfp"}), axis=1)

    return ParsedData(foods=foods_df, days=days_df, meals=meals_df)


def _is_packaged(name: str, brand: str) -> bool:
    value = f"{name} {brand}".lower()
    return any(keyword in value for keyword in PACKAGE_KEYWORDS)
