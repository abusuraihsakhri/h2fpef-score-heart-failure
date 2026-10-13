"""
FastAPI REST API Server for H2Fpef Score Heart Failure.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from .base import SecurityException
from h2fpef_score import calculate_h2fpef_score

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="H2Fpef Score Heart Failure API",
    description="H2FPEF point score and optional generic audit endpoints",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


class H2FPEFRequest(BaseModel):
    bmi: float
    num_antihypertensives: int
    af_present: bool
    pasp_mmhg: float
    age: float
    e_e_prime: float


@app.post("/api/score")
def api_score(payload: H2FPEFRequest):
    """Calculate H2FPEF from all six supplied inputs."""
    try:
        return calculate_h2fpef_score(**payload.model_dump())
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "h2fpef-score-heart-failure", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
