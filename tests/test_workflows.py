"""Tests for the workflows system."""

from workflows.workflow import Workflow, SkillStep, PromptStep
from workflows.engine import WorkflowEngine
from skills.skill_manager import SkillRegistry
from skills.skill import BaseSkill, SkillResult


class EchoSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echoes input."

    def execute(self, input: str) -> SkillResult:
        return SkillResult(success=True, output=f"Echo: {input}")


def _make_context(sr: SkillRegistry):
    return {"skill_registry": sr, "input": "hello"}


class TestWorkflow:
    def test_skill_step_execution(self):
        sr = SkillRegistry()
        sr.register(EchoSkill())
        engine = WorkflowEngine()
        engine.register(
            Workflow(
                name="test_echo",
                description="Echo test",
                steps=[SkillStep(skill_name="echo", input_template="hello")],
            )
        )
        result = engine.run("test_echo", context=_make_context(sr))
        assert result.success is True
        assert "Echo: hello" in result.final_output

    def test_workflow_not_found(self):
        engine = WorkflowEngine()
        result = engine.run("nonexistent", context={})
        assert result.success is False

    def test_list_workflows(self):
        engine = WorkflowEngine()
        engine.register(Workflow(name="wf_a", description="A", steps=[]))
        engine.register(Workflow(name="wf_b", description="B", steps=[]))
        names = [w.name for w in engine.list_workflows()]
        assert "wf_a" in names
        assert "wf_b" in names
