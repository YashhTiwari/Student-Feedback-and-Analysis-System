"""
FastAPI backend for the Student Feedback & Analysis System.
Wraps the existing ML code in src/ and exposes it as a JSON API for the React frontend.

Run (from project root):   uvicorn api.main:app --reload --port 8000
API docs:                  http://localhost:8000/docs
"""
import json
import random
import sys
import threading
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import analysis as A  # noqa: E402
from config import CLEAN_CSV, MODEL_PATH, OUT_DIR, RAW_CSV  # noqa: E402
from predict import predict_comment  # noqa: E402
from preprocess import rating_to_sentiment  # noqa: E402

app = FastAPI(title="Student Feedback & Analysis API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
_write_lock = threading.Lock()


# ---------- helpers ----------
def load_df() -> pd.DataFrame:
    if not CLEAN_CSV.exists() or not MODEL_PATH.exists():
        raise HTTPException(503, "Data/model missing. Run: python src/run_pipeline.py")
    return pd.read_csv(CLEAN_CSV)


def records(df: pd.DataFrame, index: bool = True) -> list:
    """DataFrame -> list of JSON-safe dicts (NaN becomes null)."""
    if index:
        df = df.reset_index()
    df = df.astype(object).where(pd.notna(df), None)
    out = df.to_dict("records")
    for r in out:
        for k, v in r.items():
            if isinstance(v, (np.integer,)):
                r[k] = int(v)
            elif isinstance(v, (np.floating,)):
                r[k] = float(v)
    return out


def grade(positive_pct: float) -> str:
    return "A" if positive_pct >= 70 else "B" if positive_pct >= 55 else "C" if positive_pct >= 40 else "D"


# ---------- schemas ----------
class CommentIn(BaseModel):
    comment: str = Field(..., min_length=3, max_length=500)


class FeedbackIn(BaseModel):
    teacher: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=5, max_length=500)
    student_id: str | None = Field(default=None, max_length=20)


# ---------- read endpoints ----------
@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    df = load_df()
    pairs = df.groupby("teacher")["subject"].first()
    return {
        "teachers": [{"name": t, "subject": s} for t, s in pairs.items()],
        "subjects": sorted(df["subject"].unique().tolist()),
        "topics": sorted(df["topic"].unique().tolist()),
    }


@app.get("/api/summary")
def summary(subject: str | None = None):
    df = load_df()
    if subject:
        df = df[df["subject"] == subject]
    if df.empty:
        raise HTTPException(404, "No data for this subject")
    pct = df["sentiment"].value_counts(normalize=True).mul(100).round(1)
    return {
        "responses": int(len(df)),
        "avg_rating": round(float(df["rating"].mean()), 2),
        "positive": float(pct.get("positive", 0)),
        "neutral": float(pct.get("neutral", 0)),
        "negative": float(pct.get("negative", 0)),
        "counts": {k: int(v) for k, v in df["sentiment"].value_counts().items()},
    }


@app.get("/api/teachers")
def teachers(subject: str | None = None):
    df = load_df()
    if subject:
        df = df[df["subject"] == subject]
    rep = A.teacher_report(df)
    subj = df.groupby("teacher")["subject"].first()
    rows = records(rep)
    for r in rows:
        r["subject"] = subj[r["teacher"]]
        r["grade"] = grade(r["positive"])
    return rows


@app.get("/api/teachers/{name}")
def teacher_detail(name: str):
    df = load_df()
    t = df[df["teacher"] == name]
    if t.empty:
        raise HTTPException(404, f"Teacher '{name}' not found")
    pos = float((t["sentiment"] == "positive").mean() * 100)
    neg = t[t["sentiment"] == "negative"].sort_values("date", ascending=False).head(8)
    mm = A.mismatches(t).head(8)
    return {
        "teacher": name,
        "subject": t["subject"].iloc[0],
        "responses": int(len(t)),
        "avg_rating": round(float(t["rating"].mean()), 2),
        "positive": round(pos, 1),
        "negative": round(float((t["sentiment"] == "negative").mean() * 100), 1),
        "grade": grade(pos),
        "summary": A.teacher_summary_text(df, name),
        "topics": records(A.sentiment_pct(t, "topic")),
        "recent_negative": records(neg[["date", "rating", "topic", "comment"]], index=False),
        "mismatches": records(mm, index=False),
    }


@app.get("/api/subjects")
def subjects():
    return records(A.subject_report(load_df()))


@app.get("/api/topics")
def topics(subject: str | None = None):
    df = load_df()
    if subject:
        df = df[df["subject"] == subject]
    return records(A.topic_complaints(df))


@app.get("/api/heatmap")
def heatmap():
    m = A.teacher_topic_matrix(load_df(), "negative")
    return {
        "teachers": m.index.tolist(),
        "topics": m.columns.tolist(),
        "values": [[None if pd.isna(v) else float(v) for v in row] for row in m.values],
    }


@app.get("/api/trend")
def trend(subject: str | None = None):
    df = load_df()
    if subject:
        df = df[df["subject"] == subject]
    return records(A.monthly_trend(df))


@app.get("/api/highlights")
def highlights(subject: str | None = None):
    df = load_df()
    if subject:
        df = df[df["subject"] == subject]
    return {
        "complaints": records(A.top_issues(df), index=False),
        "praises": records(A.top_praises(df), index=False),
    }


@app.get("/api/words")
def words(sentiment: str = Query("negative", pattern="^(positive|neutral|negative)$"), n: int = 30):
    return records(A.top_words(load_df(), sentiment, min(n, 60)), index=False)


@app.get("/api/model")
def model_info():
    mfile = OUT_DIR / "metrics.json"
    if not mfile.exists():
        raise HTTPException(503, "Run python src/run_pipeline.py first")
    m = json.loads(mfile.read_text())
    report = []
    rfile = OUT_DIR / "classification_report.txt"
    if rfile.exists():
        for line in rfile.read_text().splitlines():
            parts = line.split()
            if len(parts) == 5 and parts[0] in ("negative", "neutral", "positive"):
                report.append({"label": parts[0], "precision": float(parts[1]), "recall": float(parts[2]),
                               "f1": float(parts[3]), "support": int(parts[4])})
    return {
        "best_model": m["best_model"],
        "results": [{"model": k, **v} for k, v in m["results"].items()],
        "report": report,
    }


# ---------- write / predict endpoints ----------
@app.post("/api/predict")
def predict(body: CommentIn):
    r = predict_comment(body.comment)
    return {"sentiment": r["sentiment"], "confidence": r["confidence"], "probabilities": r["probabilities"],
            "topic": r["topic"], "cleaned": r["cleaned"]}


@app.post("/api/feedback")
def submit_feedback(body: FeedbackIn):
    df = load_df()
    match = df[df["teacher"] == body.teacher]
    if match.empty:
        raise HTTPException(422, f"Unknown teacher '{body.teacher}'")
    comment = " ".join(body.comment.split())
    pred = predict_comment(comment)
    row = {
        "student_id": (body.student_id or f"W{random.randint(1000, 9999)}").strip(),
        "teacher": body.teacher,
        "subject": match["subject"].iloc[0],
        "rating": body.rating,
        "comment": comment,
        "date": date.today().isoformat(),
    }
    clean_row = {**row, "clean_comment": pred["cleaned"], "sentiment": rating_to_sentiment(body.rating),
                 "topic": pred["topic"], "predicted_sentiment": pred["sentiment"]}
    with _write_lock:
        pd.DataFrame([row]).to_csv(RAW_CSV, mode="a", header=False, index=False)
        cols = list(pd.read_csv(CLEAN_CSV, nrows=0).columns)
        pd.DataFrame([clean_row])[cols].to_csv(CLEAN_CSV, mode="a", header=False, index=False)
    return {"saved": True, "sentiment": pred["sentiment"], "confidence": pred["confidence"], "topic": pred["topic"]}


@app.get("/api/outputs/{filename}")
def output_image(filename: str):
    f = (OUT_DIR / filename).resolve()
    if f.parent != OUT_DIR.resolve() or f.suffix != ".png" or not f.exists():
        raise HTTPException(404, "Not found")
    return FileResponse(f)


# ---------- serve the built React app (after `npm run build`) ----------
DIST = ROOT / "frontend" / "dist"
if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        f = DIST / full_path
        return FileResponse(f if f.is_file() else DIST / "index.html")
