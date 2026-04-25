from app.agents.orchestrator_agent import OrchestratorAgent
from app.core.schemas import QueryPlan


class StubPlanner:
    def plan(self, _query: str) -> QueryPlan:
        return QueryPlan(intent="health_guidance", urgent=False, needs_rag=False, requested_tools=[])


class StubRAG:
    def retrieve(self, _query: str) -> list[str]:
        return ["Hydration and rest can support mild headache symptoms."]


class StubTools:
    def run(self, _requested_tools: list[str], _query: str) -> dict:
        return {}


class StubMemory:
    def __init__(self) -> None:
        self.saved = False

    def recall(self, _query: str) -> list[str]:
        return ["User previously reported headache."]

    def add_interaction(self, user_id: str, query: str, response: str) -> None:
        self.saved = bool(user_id and query and response)


class StubLLM:
    def generate_text(self, _prompt: str) -> str:
        return "You may try rest and hydration while monitoring symptoms."


def test_orchestrator_applies_safety_and_persists_memory() -> None:
    orchestrator = OrchestratorAgent.__new__(OrchestratorAgent)
    orchestrator.planner = StubPlanner()
    orchestrator.rag_agent = StubRAG()
    orchestrator.tool_agent = StubTools()
    orchestrator.memory_agent = StubMemory()

    from app.core.safety import SafetyGuard

    orchestrator.safety = SafetyGuard()
    orchestrator.llm = StubLLM()

    result = orchestrator.process_query("user-1", "I have a headache")
    assert "general advice" in result.response_text.lower()
    assert orchestrator.memory_agent.saved is True
