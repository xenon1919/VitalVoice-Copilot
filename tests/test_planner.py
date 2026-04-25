from app.agents.planner_agent import PlannerAgent


def test_planner_detects_urgent_intent() -> None:
    planner = PlannerAgent()
    plan = planner.plan("I have chest pain and trouble breathing")
    assert plan.urgent is True
    assert any(step.action == "safety" for step in plan.steps)


def test_planner_requests_symptom_tool() -> None:
    planner = PlannerAgent()
    plan = planner.plan("I have a headache and fatigue")
    assert "symptom_checker" in plan.requested_tools
