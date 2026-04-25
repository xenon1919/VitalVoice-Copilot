from __future__ import annotations

from app.core.schemas import PlanStep, QueryPlan
from app.services.llm_service import GeminiService


class PlannerAgent:
    def __init__(self) -> None:
        self.llm = GeminiService()

    def plan(self, query: str) -> QueryPlan:
        q = query.lower()
        urgent = any(k in q for k in ["chest pain", "trouble breathing", "fainting", "severe"])

        requested_tools: list[str] = []
        if any(k in q for k in ["bmi", "weight", "height"]):
            requested_tools.append("bmi")
        if any(k in q for k in ["hydration", "water intake", "drink water"]):
            requested_tools.append("hydration")
        if any(k in q for k in ["headache", "fever", "tired", "fatigue", "symptom"]):
            requested_tools.append("symptom_checker")

        needs_rag = any(k in q for k in ["why", "cause", "what should", "recommend", "guide", "symptom"])
        intent = "health_guidance"

        steps = [
            PlanStep(action="memory", detail="Retrieve relevant past interactions"),
            PlanStep(action="safety", detail="Assess urgency and apply safety guardrails"),
        ]

        if needs_rag:
            steps.append(PlanStep(action="rag", detail="Retrieve evidence from health docs"))
        if requested_tools:
            steps.append(PlanStep(action="tool", detail="Run relevant health utility tools"))
        steps.append(PlanStep(action="respond", detail="Generate final safe response"))

        return QueryPlan(
            intent=intent,
            urgent=urgent,
            requested_tools=requested_tools,
            needs_rag=needs_rag,
            steps=steps,
        )
