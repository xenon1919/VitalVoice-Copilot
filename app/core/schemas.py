from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    action: Literal["respond", "rag", "tool", "memory", "safety"]
    detail: str


class QueryPlan(BaseModel):
    intent: str
    urgent: bool = False
    requested_tools: list[str] = Field(default_factory=list)
    needs_rag: bool = False
    steps: list[PlanStep] = Field(default_factory=list)


class ChatRequest(BaseModel):
    user_id: str
    query: str


class ChatResponse(BaseModel):
    user_id: str
    query: str
    plan: QueryPlan
    response_text: str
    retrieved_context: list[str] = Field(default_factory=list)
    tool_results: dict[str, Any] = Field(default_factory=dict)
    memory_hits: list[str] = Field(default_factory=list)
    urgent: bool = False


class ToolBMIRequest(BaseModel):
    weight_kg: float = Field(gt=0)
    height_cm: float = Field(gt=0)


class ToolHydrationRequest(BaseModel):
    weight_kg: float = Field(gt=0)
    activity_level: Literal["low", "moderate", "high"] = "moderate"


class VoiceResponse(BaseModel):
    user_id: str
    transcript: str
    response_text: str
    output_audio_path: str
