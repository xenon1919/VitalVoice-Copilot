from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from time import time
from typing import Iterator
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse

from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.tool_agent import ToolAgent
from app.core.schemas import (
    ChatRequest,
    ChatResponse,
    ToolBMIRequest,
    ToolHydrationRequest,
    VoiceResponse,
)
from app.services.stt_service import WhisperSTTService
from app.services.tts_service import TTSService

router = APIRouter()

_CHAT_CACHE_TTL_SECONDS = 300
_chat_cache: dict[str, tuple[float, ChatResponse]] = {}


@lru_cache
def get_orchestrator() -> OrchestratorAgent:
    return OrchestratorAgent()


@lru_cache
def get_tool_agent() -> ToolAgent:
    return ToolAgent()


@lru_cache
def get_stt_service() -> WhisperSTTService:
    return WhisperSTTService()


@lru_cache
def get_tts_service() -> TTSService:
    return TTSService()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/", include_in_schema=False)
def root() -> Response:
    """Serve the frontend HTML dashboard"""
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
    if not frontend_path.exists():
        return Response(
            content="<h1>Frontend not found</h1><p>Place index.html in the frontend/ folder</p>",
            media_type="text/html",
            status_code=404,
        )
    html_content = frontend_path.read_text(encoding="utf-8")
    return Response(content=html_content, media_type="text/html")


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@router.post("/chat/query", response_model=ChatResponse)
def chat_query(payload: ChatRequest) -> ChatResponse:
    cache_key = f"{payload.user_id.strip()}::{payload.query.strip().lower()}"
    now = time()
    cached = _chat_cache.get(cache_key)
    if cached and (now - cached[0]) < _CHAT_CACHE_TTL_SECONDS:
        return cached[1].model_copy(deep=True)

    response = get_orchestrator().process_query(user_id=payload.user_id, query=payload.query)
    _chat_cache[cache_key] = (now, response.model_copy(deep=True))

    if len(_chat_cache) > 300:
        expired_keys = [k for k, (ts, _) in _chat_cache.items() if (now - ts) >= _CHAT_CACHE_TTL_SECONDS]
        for key in expired_keys:
            _chat_cache.pop(key, None)

    return response


@router.post("/chat/query/stream")
def chat_query_stream(payload: ChatRequest) -> StreamingResponse:
    def event_stream() -> Iterator[str]:
        cache_key = f"{payload.user_id.strip()}::{payload.query.strip().lower()}"
        now = time()
        cached = _chat_cache.get(cache_key)
        if cached and (now - cached[0]) < _CHAT_CACHE_TTL_SECONDS:
            cached_response = cached[1].model_copy(deep=True)
            meta_event = {
                "type": "meta",
                "plan": cached_response.plan.model_dump(),
                "urgent": cached_response.urgent,
                "cached": True,
            }
            yield json.dumps(meta_event) + "\n"
            yield json.dumps({"type": "token", "content": cached_response.response_text}) + "\n"
            yield json.dumps({"type": "final", "data": cached_response.model_dump()}) + "\n"
            return

        try:
            orchestrator = get_orchestrator()
            plan = orchestrator.planner.plan(payload.query)
            safety = orchestrator.safety.assess(payload.query)
            urgent_flag = bool(plan.urgent or safety.urgent)

            memory_hits = orchestrator.memory_agent.recall(payload.query)
            retrieved_context = orchestrator.rag_agent.retrieve(payload.query) if plan.needs_rag else []
            tool_results = (
                orchestrator.tool_agent.run(plan.requested_tools, payload.query) if plan.requested_tools else {}
            )

            meta_event = {
                "type": "meta",
                "plan": plan.model_dump(),
                "urgent": urgent_flag,
                "cached": False,
                "route": [step.action for step in plan.steps],
            }
            yield json.dumps(meta_event) + "\n"

            response_prompt = orchestrator._build_response_prompt(
                query=payload.query,
                memory_hits=memory_hits,
                retrieved_context=retrieved_context,
                tool_results=tool_results,
                urgent=urgent_flag,
            )

            chunks: list[str] = []
            for piece in orchestrator.llm.generate_text_stream(response_prompt):
                chunks.append(piece)
                yield json.dumps({"type": "token", "content": piece}) + "\n"

            generated = "".join(chunks).strip()
            if not generated:
                generated = "I could not generate a response."

            safe_response = orchestrator.safety.apply(generated, urgent=urgent_flag)
            orchestrator.memory_agent.add_interaction(
                user_id=payload.user_id,
                query=payload.query,
                response=safe_response,
            )

            final = ChatResponse(
                user_id=payload.user_id,
                query=payload.query,
                plan=plan,
                response_text=safe_response,
                retrieved_context=retrieved_context,
                tool_results=tool_results,
                memory_hits=memory_hits,
                urgent=urgent_flag,
            )

            _chat_cache[cache_key] = (time(), final.model_copy(deep=True))
            yield json.dumps({"type": "final", "data": final.model_dump()}) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@router.post("/voice/query", response_model=VoiceResponse)
async def voice_query(user_id: str = "unknown", audio: UploadFile = File(...)) -> VoiceResponse:
    safe_name = Path(audio.filename or "query.wav").name
    tmp_path = Path("storage") / f"input_{uuid4().hex}_{safe_name}"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = await audio.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        tmp_path.write_bytes(content)

        # Transcribe audio
        try:
            transcript = get_stt_service().transcribe(str(tmp_path))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Transcription failed: {str(e)}")
        
        if not transcript or not transcript.strip():
            raise HTTPException(status_code=400, detail="No speech detected in audio. Please speak clearly.")

        # Process query through orchestrator
        result = get_orchestrator().process_query(user_id=user_id, query=transcript)
        
        # Synthesize response to speech
        try:
            output_audio_path = get_tts_service().synthesize(result.response_text)
        except Exception as e:
            output_audio_path = None  # TTS failure is not critical

        return VoiceResponse(
            user_id=user_id,
            transcript=transcript,
            response_text=result.response_text,
            output_audio_path=output_audio_path or "tts_generation_pending",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice query error: {str(e)}")
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


@router.post("/tools/bmi")
def bmi_tool(payload: ToolBMIRequest) -> dict:
    return get_tool_agent().run_bmi(weight_kg=payload.weight_kg, height_cm=payload.height_cm)


@router.post("/tools/hydration")
def hydration_tool(payload: ToolHydrationRequest) -> dict:
    return get_tool_agent().run_hydration(weight_kg=payload.weight_kg, activity_level=payload.activity_level)
