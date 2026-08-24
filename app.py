"""Service-Runner: a typed JSON front door to PySCF.

The contract is two calls, exactly as taught on the Week 4 slide:
    POST /jobs               -> {"job_id": ...}
    GET  /jobs/{id}/result   -> energy, timings, versions, environment

Endpoints are plain `def` (not `async def`) so FastAPI runs them in a
threadpool — a multi-second SCF therefore never blocks the event loop.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import runner

api = FastAPI(
    title="CompChem Service-Runner",
    version="1.0.0",
    description="Submit a PySCF single point as JSON; collect a result record as JSON.",
)

# Week 4 is a single-process teaching service, so an in-memory store is honest.
# Every result is ALSO written to results/ so it survives the process.
_JOBS: dict[str, dict] = {}
RESULTS = Path("results")


class JobSpec(BaseModel):
    """The typed contract. Pydantic validates it before PySCF ever runs."""
    molecule: str = Field(..., description="XYZ block, e.g. 'O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587'")
    method: Literal["HF", "B3LYP", "MP2"] = "HF"
    basis: str = "def2-svp"
    grid: int = Field(3, ge=0, le=9, description="DFT grid level; ignored by HF and MP2")
    conv_tol: float = Field(1e-9, gt=0, lt=1)
    charge: int = 0
    spin: int = Field(0, ge=0)


class JobAccepted(BaseModel):
    job_id: str


@api.get("/health")
def health() -> dict:
    return {"status": "ok", "methods": list(runner.SUPPORTED_METHODS)}


@api.post("/jobs", response_model=JobAccepted, status_code=201)
def submit(spec: JobSpec) -> JobAccepted:
    job_id = uuid.uuid4().hex[:12]
    try:
        record = runner.run_job(spec.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    record["job_id"] = job_id
    _JOBS[job_id] = record
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / f"job_{job_id}.json").write_text(json.dumps(record, indent=2) + "\n")
    return JobAccepted(job_id=job_id)


@api.get("/jobs/{job_id}/result")
def result(job_id: str) -> dict:
    if job_id not in _JOBS:
        raise HTTPException(status_code=404, detail=f"no such job: {job_id}")
    return _JOBS[job_id]
