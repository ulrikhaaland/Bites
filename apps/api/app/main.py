from __future__ import annotations

import json
import uuid
from datetime import date
from typing import Any

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_connection
from app.metrics import compute_metrics_daily, detect_phases
from app.models import DayDetail, DayRecord, ImportStatus, PhaseResponse, SummaryResponse, TimeseriesPoint, TimeseriesResponse
from app.parsers import parse_mfp_export

app = FastAPI(title="Bites API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"] ,
)

IMPORT_JOBS: dict[str, ImportStatus] = {}


@app.post("/api/import", response_model=ImportStatus)
async def import_data(background_tasks: BackgroundTasks, files: list[UploadFile] = File(...)) -> ImportStatus:
    job_id = str(uuid.uuid4())
    status = ImportStatus(job_id=job_id, status="queued", progress=0)
    IMPORT_JOBS[job_id] = status

    file_bytes = [(file.filename, await file.read()) for file in files]
    background_tasks.add_task(_process_import, job_id, file_bytes)
    return status


@app.get("/api/import/{job_id}/status", response_model=ImportStatus)
async def import_status(job_id: str) -> ImportStatus:
    status = IMPORT_JOBS.get(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status


@app.get("/api/summary", response_model=SummaryResponse)
async def summary(start: date, end: date) -> SummaryResponse:
    conn = get_connection()
    query = """
        SELECT
            AVG(kcal) AS average_kcal,
            AVG(protein_g) AS average_protein_g,
            AVG(fiber_g) AS average_fiber_g,
            VAR_SAMP(kcal) AS kcal_variance,
            AVG(protein_meals_ge_30g) AS protein_meals_ge_30g,
            AVG(CASE WHEN completeness_score >= 0.8 THEN 1 ELSE 0 END) * 100 AS completeness_percent
        FROM metrics_daily md
        JOIN days d ON md.date = d.date
        WHERE md.date BETWEEN ? AND ?
    """
    row = conn.execute(query, [start, end]).fetchone()
    return SummaryResponse(
        start=start,
        end=end,
        average_kcal=row[0],
        average_protein_g=row[1],
        average_fiber_g=row[2],
        kcal_variance=row[3],
        protein_meals_ge_30g=row[4],
        completeness_percent=row[5],
    )


@app.get("/api/timeseries", response_model=TimeseriesResponse)
async def timeseries(metric: str, start: date, end: date) -> TimeseriesResponse:
    if metric not in {"kcal", "protein_g", "fiber_g", "upf_proxy"}:
        raise HTTPException(status_code=400, detail="Invalid metric")
    conn = get_connection()
    query = f"""
        SELECT date, {metric},
            CASE
                WHEN ? = 'kcal' THEN kcal_mean_7d
                WHEN ? = 'protein_g' THEN protein_mean_7d
                WHEN ? = 'fiber_g' THEN fiber_mean_7d
                ELSE NULL
            END AS rolling_mean
        FROM metrics_daily
        WHERE date BETWEEN ? AND ?
        ORDER BY date
    """
    rows = conn.execute(query, [metric, metric, metric, start, end]).fetchall()
    points = [TimeseriesPoint(date=row[0], value=row[1], rolling_mean=row[2]) for row in rows]
    return TimeseriesResponse(metric=metric, points=points)


@app.get("/api/days", response_model=list[DayRecord])
async def days(start: date, end: date, page: int = 1, page_size: int = 30, sort: str = "date") -> list[DayRecord]:
    if sort not in {"date", "calories", "protein_g"}:
        raise HTTPException(status_code=400, detail="Invalid sort")
    offset = (page - 1) * page_size
    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT date, calories, protein_g, carbs_g, fat_g, fiber_g, sugar_g, satfat_g, sodium_mg, completeness_score
        FROM days
        WHERE date BETWEEN ? AND ?
        ORDER BY {sort}
        LIMIT ? OFFSET ?
        """,
        [start, end, page_size, offset],
    ).fetchall()
    return [
        DayRecord(
            date=row[0],
            calories=row[1],
            protein_g=row[2],
            carbs_g=row[3],
            fat_g=row[4],
            fiber_g=row[5],
            sugar_g=row[6],
            satfat_g=row[7],
            sodium_mg=row[8],
            completeness_score=row[9],
        )
        for row in rows
    ]


@app.get("/api/day/{day}", response_model=DayDetail)
async def day_detail(day: date) -> DayDetail:
    conn = get_connection()
    day_row = conn.execute(
        """
        SELECT date, calories, protein_g, carbs_g, fat_g, fiber_g, sugar_g, satfat_g, sodium_mg, completeness_score
        FROM days
        WHERE date = ?
        """,
        [day],
    ).fetchone()
    if not day_row:
        raise HTTPException(status_code=404, detail="Day not found")
    meals = conn.execute(
        """
        SELECT meal, calories, protein_g, carbs_g, fat_g, fiber_g, sugar_g, satfat_g, sodium_mg
        FROM meals WHERE date = ?
        """,
        [day],
    ).fetchall()
    foods = conn.execute(
        """
        SELECT meal, name, brand, amount, unit, calories, protein_g, carbs_g, fat_g, fiber_g
        FROM foods_raw WHERE date = ?
        """,
        [day],
    ).fetchall()
    return DayDetail(
        day=DayRecord(
            date=day_row[0],
            calories=day_row[1],
            protein_g=day_row[2],
            carbs_g=day_row[3],
            fat_g=day_row[4],
            fiber_g=day_row[5],
            sugar_g=day_row[6],
            satfat_g=day_row[7],
            sodium_mg=day_row[8],
            completeness_score=day_row[9],
        ),
        meals=[
            {
                "meal": row[0],
                "calories": row[1],
                "protein_g": row[2],
                "carbs_g": row[3],
                "fat_g": row[4],
                "fiber_g": row[5],
                "sugar_g": row[6],
                "satfat_g": row[7],
                "sodium_mg": row[8],
            }
            for row in meals
        ],
        foods=[
            {
                "meal": row[0],
                "name": row[1],
                "brand": row[2],
                "amount": row[3],
                "unit": row[4],
                "calories": row[5],
                "protein_g": row[6],
                "carbs_g": row[7],
                "fat_g": row[8],
                "fiber_g": row[9],
            }
            for row in foods
        ],
    )


@app.get("/api/phases", response_model=list[PhaseResponse])
async def phases(start: date, end: date) -> list[PhaseResponse]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT start_date, end_date, label, deltas_json
        FROM phases
        WHERE start_date <= ? AND end_date >= ?
        ORDER BY start_date
        """,
        [end, start],
    ).fetchall()
    return [
        PhaseResponse(
            start_date=row[0],
            end_date=row[1],
            label=row[2],
            deltas=json.loads(row[3]),
        )
        for row in rows
    ]


def _process_import(job_id: str, files: list[tuple[str, bytes]]) -> None:
    status = IMPORT_JOBS[job_id]
    status.status = "running"
    status.progress = 0.1
    try:
        parsed = parse_mfp_export(files)
        status.progress = 0.4

        conn = get_connection()
        conn.execute("DELETE FROM foods_raw")
        conn.execute("DELETE FROM days")
        conn.execute("DELETE FROM meals")
        conn.execute("DELETE FROM metrics_daily")
        conn.execute("DELETE FROM phases")

        conn.register("foods_df", parsed.foods)
        conn.register("days_df", parsed.days)
        conn.register("meals_df", parsed.meals)
        conn.execute("INSERT INTO foods_raw SELECT * FROM foods_df")
        conn.execute("INSERT INTO days SELECT * FROM days_df")
        conn.execute("INSERT INTO meals SELECT * FROM meals_df")

        status.progress = 0.7
        metrics = compute_metrics_daily(parsed.foods, parsed.days)
        conn.register("metrics_df", metrics)
        conn.execute("INSERT INTO metrics_daily SELECT * FROM metrics_df")

        phases = detect_phases(parsed.days.sort_values("date"))
        if phases:
            conn.register("phases_df", phases)
            conn.execute("INSERT INTO phases SELECT * FROM phases_df")

        status.status = "completed"
        status.progress = 1
    except Exception as exc:  # noqa: BLE001
        status.status = "error"
        status.errors.append(str(exc))
        status.progress = 1
