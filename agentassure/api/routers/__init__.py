"""FastAPI Routers Package."""

from agentassure.api.routers.audio import router as audio_router
from agentassure.api.routers.auth import router as auth_router
from agentassure.api.routers.closed_loop_ticketing import router as ticketing_router
from agentassure.api.routers.failure_to_test import router as failure_router
from agentassure.api.routers.failure_to_test import test_cases_router
from agentassure.api.routers.health import router as health_router
from agentassure.api.routers.persona_simulator import router as simulator_router
from agentassure.api.routers.quality_reporting import router as reporting_router
from agentassure.api.routers.release_gating import router as release_gate_router
from agentassure.api.routers.review_workbench import router as review_router
from agentassure.api.routers.smart_sampling import router as sampling_router

__all__ = [
    "health_router",
    "auth_router",
    "review_router",
    "sampling_router",
    "failure_router",
    "test_cases_router",
    "simulator_router",
    "release_gate_router",
    "ticketing_router",
    "reporting_router",
    "audio_router",
]
