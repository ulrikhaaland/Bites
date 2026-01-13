from __future__ import annotations

from pathlib import Path

import duckdb

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DB_PATH = DATA_DIR / "bites.duckdb"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS foods_raw (
    id UUID DEFAULT uuid(),
    source TEXT,
    date DATE,
    meal TEXT,
    name TEXT,
    brand TEXT,
    amount DOUBLE,
    unit TEXT,
    calories DOUBLE,
    protein_g DOUBLE,
    carbs_g DOUBLE,
    fat_g DOUBLE,
    fiber_g DOUBLE,
    sugar_g DOUBLE,
    satfat_g DOUBLE,
    sodium_mg DOUBLE,
    extra_json JSON
);

CREATE TABLE IF NOT EXISTS days (
    date DATE PRIMARY KEY,
    calories DOUBLE,
    protein_g DOUBLE,
    carbs_g DOUBLE,
    fat_g DOUBLE,
    fiber_g DOUBLE,
    sugar_g DOUBLE,
    satfat_g DOUBLE,
    sodium_mg DOUBLE,
    completeness_score DOUBLE,
    source_json JSON
);

CREATE TABLE IF NOT EXISTS meals (
    date DATE,
    meal TEXT,
    calories DOUBLE,
    protein_g DOUBLE,
    carbs_g DOUBLE,
    fat_g DOUBLE,
    fiber_g DOUBLE,
    sugar_g DOUBLE,
    satfat_g DOUBLE,
    sodium_mg DOUBLE
);

CREATE TABLE IF NOT EXISTS metrics_daily (
    date DATE PRIMARY KEY,
    kcal DOUBLE,
    protein_g DOUBLE,
    fiber_g DOUBLE,
    kcal_mean_7d DOUBLE,
    kcal_std_7d DOUBLE,
    protein_mean_7d DOUBLE,
    protein_std_7d DOUBLE,
    fiber_mean_7d DOUBLE,
    fiber_std_7d DOUBLE,
    kcal_mean_30d DOUBLE,
    kcal_std_30d DOUBLE,
    protein_mean_30d DOUBLE,
    protein_std_30d DOUBLE,
    fiber_mean_30d DOUBLE,
    fiber_std_30d DOUBLE,
    fiber_per_1000kcal DOUBLE,
    protein_per_meal_avg DOUBLE,
    protein_meals_ge_30g INT,
    upf_proxy DOUBLE,
    energy_density DOUBLE,
    flags_json JSON
);

CREATE TABLE IF NOT EXISTS phases (
    id UUID DEFAULT uuid(),
    start_date DATE,
    end_date DATE,
    label TEXT,
    deltas_json JSON
);
"""


def get_connection() -> duckdb.DuckDBPyConnection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    conn.execute(SCHEMA_SQL)
    return conn
