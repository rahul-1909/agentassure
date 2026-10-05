"""Unit Tests for Synthetic Persona Simulator and Voice Simulation."""

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import select

from agentassure.simulation.personas import SYNTHETIC_PERSONAS
from agentassure.simulation.voice_layer import VoiceSimulator
from agentassure.simulation.simulator_engine import SimulatorEngine
from agentassure.db.models.persona import PersonaProfile, SimulationRun
from agentassure.schemas.persona import SimulationRunRequest


def test_ten_plus_personas_defined():
    assert len(SYNTHETIC_PERSONAS) >= 10
    keys = [p["persona_key"] for p in SYNTHETIC_PERSONAS]
    assert "price_sensitive_haggler" in keys
    assert "confused_elderly" in keys
    assert "hostile_escalator" in keys
    assert "hinglish_codeswitcher" in keys
    assert "prompt_injection_adversary" in keys


def test_voice_simulator_asr_jitter():
    clean = "My bank account balance in rupees is zero."
    # Simulate high error rate
    corrupted, conf = VoiceSimulator.simulate_asr(clean, word_error_rate=0.5)
    assert isinstance(corrupted, str)
    assert 0.0 <= conf <= 1.0


def test_voice_simulator_waveform_peaks():
    meta = VoiceSimulator.simulate_tts_audio_waveform("Test utterance for waveform playback.")
    assert "duration_seconds" in meta
    assert "peaks" in meta
    assert len(meta["peaks"]) > 0


def test_run_simulation_adversarial(db_session: Session):
    req = SimulationRunRequest(
        persona_key="prompt_injection_adversary",
        agent_version="v2.5.0-candidate",
        max_turns=2,
        voice_mode=False,
    )
    sim_run = SimulatorEngine.run_simulation(db_session, req)
    assert sim_run.id is not None
    assert sim_run.total_turns > 0
    assert len(sim_run.transcript_log) > 0


def test_run_simulation_hinglish(db_session: Session):
    req = SimulationRunRequest(
        persona_key="hinglish_codeswitcher",
        agent_version="v2.5.0-candidate",
        max_turns=3,
        voice_mode=True,
    )
    sim_run = SimulatorEngine.run_simulation(db_session, req)
    assert sim_run.id is not None
    assert sim_run.latency_avg_ms > 0.0
