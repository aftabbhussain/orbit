import pytest
from backend.graph.pipeline import MultiAgentWorkflow

def test_workflow_init():
    workflow = MultiAgentWorkflow()
    assert workflow is not None
