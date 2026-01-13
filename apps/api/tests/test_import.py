from __future__ import annotations

from pathlib import Path

from app.metrics import compute_metrics_daily
from app.parsers import parse_mfp_export

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_mfp_export():
    files = [
        ("diary.csv", (FIXTURES / "diary.csv").read_bytes()),
        ("daily_totals.csv", (FIXTURES / "daily_totals.csv").read_bytes()),
    ]
    parsed = parse_mfp_export(files)
    assert not parsed.foods.empty
    assert not parsed.days.empty
    assert not parsed.meals.empty
    assert set(parsed.foods["meal"]) <= {"breakfast", "lunch", "dinner", "snack", "other"}


def test_compute_metrics_daily():
    files = [
        ("diary.csv", (FIXTURES / "diary.csv").read_bytes()),
        ("daily_totals.csv", (FIXTURES / "daily_totals.csv").read_bytes()),
    ]
    parsed = parse_mfp_export(files)
    metrics = compute_metrics_daily(parsed.foods, parsed.days)
    assert "fiber_per_1000kcal" in metrics.columns
    assert metrics["upf_proxy"].between(0, 1).all()
