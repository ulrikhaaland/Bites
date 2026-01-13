from __future__ import annotations

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field


class ImportStatus(BaseModel):
    job_id: str
    status: str
    progress: float = Field(0, ge=0, le=1)
    errors: list[str] = []


class SummaryResponse(BaseModel):
    start: date
    end: date
    average_kcal: Optional[float]
    average_protein_g: Optional[float]
    average_fiber_g: Optional[float]
    kcal_variance: Optional[float]
    protein_meals_ge_30g: Optional[float]
    completeness_percent: Optional[float]


class TimeseriesPoint(BaseModel):
    date: date
    value: Optional[float]
    rolling_mean: Optional[float] = None


class TimeseriesResponse(BaseModel):
    metric: str
    points: list[TimeseriesPoint]


class DayRecord(BaseModel):
    date: date
    calories: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    fiber_g: Optional[float]
    sugar_g: Optional[float]
    satfat_g: Optional[float]
    sodium_mg: Optional[float]
    completeness_score: Optional[float]


class DayDetail(BaseModel):
    day: DayRecord
    meals: list[dict[str, Any]]
    foods: list[dict[str, Any]]


class PhaseResponse(BaseModel):
    start_date: date
    end_date: date
    label: str
    deltas: dict[str, Any]
