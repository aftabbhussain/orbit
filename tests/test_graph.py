import pytest
from backend.graph.pipeline import (
    MultiAgentWorkflow,
    create_workflow,
    WorkflowOutcome,
)
from backend.graph.nodes.router import plan_node, RouteDecision
from backend.graph.nodes.judge import validation_node, RelevanceVerdict
from backend.graph.nodes.writer import gen_node


class TestWorkflowOutcomeContract:
    def test_outcome_creation(self):
        record = WorkflowOutcome(
            answer="Generated answer",
            source=[{"id": 1, "title": "Paper Title"}],
            reasoning_step=["Step 1 completed"],
            trace_id="trace-abc",
            langfuse_url="https://langfuse.internal/trace/trace-abc",
        )
        assert record.answer == "Generated answer"
        assert len(record.source) == 1
        assert len(record.reasoning_step) == 1
        assert record.trace_id == "trace-abc"


class TestDecisionSchemas:
    def test_router_decision_schema(self):
        decision = RouteDecision(
            decision="process",
            route="vector_search",
            reasoning="Academic paper query",
        )
        assert decision.decision == "process"
        assert decision.route == "vector_search"
        assert decision.reasoning == "Academic paper query"

    def test_router_decision_optional_route(self):
        decision = RouteDecision(
            decision="direct_answer",
            reasoning="Casual greeting",
        )
        assert decision.decision == "direct_answer"
        assert decision.route is None

    def test_verdict_schema(self):
        verdict = RelevanceVerdict(
            validation="relevant",
            reasoning="Context directly answers question",
        )
        assert verdict.validation == "relevant"
        assert verdict.reasoning == "Context directly answers question"


class TestGraphLifecycle:
    def test_workflow_initialization(self):
        flow = create_workflow()
        assert flow is not None
        assert hasattr(flow, "app")
        assert flow.app is not None

    def test_workflow_run_callable(self):
        flow = create_workflow()
        assert hasattr(flow, "run")
        assert callable(flow.run)
