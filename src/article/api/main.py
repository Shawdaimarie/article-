from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from article.api.db import Base, engine, get_db
from article.api.models import Run
from article.api.schemas import RunCreate, RunOut

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Article API",
    description="Stores and serves charter-compliance run history for the Article CLI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/runs", response_model=RunOut, status_code=201)
def create_run(run_in: RunCreate, db: Session = Depends(get_db)):
    run = Run(
        project_name=run_in.project_name,
        charter_name=run_in.charter_name,
        charter_version=run_in.charter_version,
        score=run_in.score,
        passed=run_in.passed,
        failed=run_in.failed,
        skipped=run_in.skipped,
        results=[r.model_dump() for r in run_in.results],
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@app.get("/runs", response_model=list[RunOut])
def list_runs(
    project_name: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Run).order_by(Run.created_at.desc())
    if project_name:
        query = query.filter(Run.project_name == project_name)
    return query.limit(limit).all()


@app.get("/runs/{run_id}", response_model=RunOut)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
