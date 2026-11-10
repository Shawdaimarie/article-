import os
import secrets
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Header
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

def require_token(authorization: Optional[str] = Header(default=None)):
    expected = os.environ.get("ARTICLE_API_TOKEN", "")
    if len(expected) < 32:
        raise HTTPException(status_code=503, detail="Configure ARTICLE_API_TOKEN (at least 32 characters)")
    if not authorization or not secrets.compare_digest(authorization, "Bearer " + expected):
        raise HTTPException(status_code=401, detail="Valid bearer token required")


STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/runs", response_model=RunOut, status_code=201, dependencies=[Depends(require_token)])
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


@app.get("/runs", response_model=list[RunOut], dependencies=[Depends(require_token)])
def list_runs(
    project_name: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Run).order_by(Run.created_at.desc())
    if project_name:
        query = query.filter(Run.project_name == project_name)
    return query.limit(limit).all()


@app.get("/runs/{run_id}", response_model=RunOut, dependencies=[Depends(require_token)])
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
