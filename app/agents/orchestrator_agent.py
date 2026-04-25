from __future__ import annotations

from app.agents.planner_agent import PlannerAgent
from app.agents.rag_agent import RAGAgent
from app.agents.tool_agent import ToolAgent
from app.core.safety import SafetyGuard
from app.core.schemas import ChatResponse
from app.memory.memory_agent import MemoryAgent
from app.services.llm_service import GeminiService


class OrchestratorAgent:
    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.rag_agent = RAGAgent()
        self.tool_agent = ToolAgent()
        self.memory_agent = MemoryAgent()
        self.safety = SafetyGuard()
        self.llm = GeminiService()

    def process_query(self, user_id: str, query: str) -> ChatResponse:
        plan = self.planner.plan(query)
        safety = self.safety.assess(query)

        memory_hits = self.memory_agent.recall(query)
        retrieved_context = self.rag_agent.retrieve(query) if plan.needs_rag else []
        tool_results = self.tool_agent.run(plan.requested_tools, query) if plan.requested_tools else {}

        response_prompt = self._build_response_prompt(
            query=query,
            memory_hits=memory_hits,
            retrieved_context=retrieved_context,
            tool_results=tool_results,
            urgent=safety.urgent or plan.urgent,
        )
        generated = self.llm.generate_text(response_prompt)
        safe_response = self.safety.apply(generated, urgent=safety.urgent or plan.urgent)

        self.memory_agent.add_interaction(user_id=user_id, query=query, response=safe_response)

        return ChatResponse(
            user_id=user_id,
            query=query,
            plan=plan,
            response_text=safe_response,
            retrieved_context=retrieved_context,
            tool_results=tool_results,
            memory_hits=memory_hits,
            urgent=safety.urgent or plan.urgent,
        )

    def _build_response_prompt(
        self,
        query: str,
        memory_hits: list[str],
        retrieved_context: list[str],
        tool_results: dict,
        urgent: bool,
    ) -> str:
        return f"""
You are a careful health voice copilot.

User query:
{query}

Urgent flag: {urgent}

Relevant past interactions:
{memory_hits}

Retrieved medical guidance context:
{retrieved_context}

Tool outputs:
{tool_results}

Rules:
- Never provide diagnosis.
- Use safe, supportive language.
- If urgent is true, strongly advise emergency medical help.
- Include concise practical next steps.
- Keep answer short and clear for voice output.
""".strip()
