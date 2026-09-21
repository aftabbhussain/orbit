from backend.graph.pipeline import MultiAgentWorkflow

_workflow = None

def get_workflow() -> MultiAgentWorkflow:
    global _workflow
    if _workflow is None:
        _workflow = MultiAgentWorkflow()
    return _workflow
