from fastapi import Request
from backend.graph.pipeline import MultiAgentWorkflow


def get_workflow(request: Request) -> MultiAgentWorkflow:
    return request.app.state.workflow


get_pipeline = get_workflow
