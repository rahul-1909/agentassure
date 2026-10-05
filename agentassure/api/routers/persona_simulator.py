"""Persona Simulator API Endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from agentassure.db.session import get_db
from agentassure.db.models.persona import PersonaProfile, SimulationRun
from agentassure.db.models.user import User
from agentassure.schemas.persona import (
    PersonaResponse,
    SimulationRunRequest,
    SimulationRunResponse,
)
from agentassure.simulation.simulator_engine import SimulatorEngine
from agentassure.api.deps import get_current_user
from agentassure.utils.audit import AuditLogger

router = APIRouter(prefix="/simulator", tags=["Persona Simulator"])


@router.get("/personas", response_model=List[PersonaResponse])
def list_personas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all 10+ synthetic adversarial customer personas."""
    SimulatorEngine.sync_personas(db)
    personas = db.scalars(
        select(PersonaProfile).where(PersonaProfile.is_active.is_(True))
    ).all()
    return personas


@router.post("/run", response_model=SimulationRunResponse, status_code=status.HTTP_201_CREATED)
def run_simulation(
    payload: SimulationRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute synthetic multi-turn customer dialogue simulation against agent candidate."""
    try:
        sim_run = SimulatorEngine.run_simulation(db, payload)
        AuditLogger.log_action(
            db,
            action="run_persona_simulation",
            entity_type="simulation_run",
            entity_id=sim_run.id,
            user_id=current_user.id,
            details={
                "persona_key": payload.persona_key,
                "surfaced_failure": sim_run.surfaced_failure,
            },
        )
        return SimulationRunResponse(
            id=sim_run.id,
            persona_id=sim_run.persona_id,
            persona_key=payload.persona_key,
            agent_version=sim_run.agent_version,
            total_turns=sim_run.total_turns,
            successful_goal=sim_run.successful_goal,
            surfaced_failure=sim_run.surfaced_failure,
            failure_category=sim_run.failure_category,
            transcript_log=sim_run.transcript_log,
            latency_avg_ms=sim_run.latency_avg_ms,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/runs", response_model=List[SimulationRunResponse])
def list_simulation_runs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List historical simulation runs and surfaced edge-case failures."""
    runs = db.scalars(
        select(SimulationRun).order_by(desc(SimulationRun.created_at)).limit(limit)
    ).all()
    return [
        SimulationRunResponse(
            id=r.id,
            persona_id=r.persona_id,
            persona_key=r.persona.persona_key if r.persona else None,
            agent_version=r.agent_version,
            total_turns=r.total_turns,
            successful_goal=r.successful_goal,
            surfaced_failure=r.surfaced_failure,
            failure_category=r.failure_category,
            transcript_log=r.transcript_log,
            latency_avg_ms=r.latency_avg_ms,
        )
        for r in runs
    ]
