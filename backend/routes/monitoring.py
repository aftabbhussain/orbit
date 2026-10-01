from fastapi import APIRouter, Depends, Request
from loguru import logger

from backend.contracts import SystemStatus
from backend.dependencies import get_workflow
from backend.graph.pipeline import MultiAgentWorkflow

router = APIRouter(prefix="/health", tags=["monitoring"])


@router.get("", response_model=SystemStatus)
async def health_check(
    workflow: MultiAgentWorkflow = Depends(get_workflow),
) -> SystemStatus:
    status_map = {"workflow": "healthy" if workflow else "unhealthy"}

    try:
        if workflow and hasattr(workflow, "app"):
            status_map["workflow_graph"] = "healthy"
        else:
            status_map["workflow_graph"] = "not_configured"
    except Exception as err:
        logger.warning(f"Health check probe failed: {err}")
        status_map["workflow"] = "unhealthy"

    is_overall_healthy = all(
        s in ["healthy", "not_configured"] for s in status_map.values()
    )

    return SystemStatus(
        status="healthy" if is_overall_healthy else "degraded",
        version="2.0.0",
        components=status_map,
    )


@router.get("/ready")
async def readiness_probe(request: Request) -> dict:
    try:
        pipeline = request.app.state.workflow
        if pipeline is None:
            return {"ready": False, "reason": "Workflow not initialized"}
        return {"ready": True}
    except Exception as exc:
        return {"ready": False, "reason": str(exc)}


@router.get("/live")
async def liveness_probe() -> dict:
    return {"alive": True}
