# Personal Health Voice Copilot: Detailed Project Documentation

## 1. Executive Summary

Personal Health Voice Copilot is a production-oriented, multi-agent, voice-enabled clinical guidance assistant built with FastAPI and Python 3.11. The system combines:

- Multi-agent orchestration for decision-making
- Retrieval-Augmented Generation (RAG) over domain documents
- Semantic conversation memory
- Voice input with local speech-to-text
- Voice output with configurable text-to-speech
- Safety guardrails for urgent symptom escalation and non-diagnostic behavior

It is designed for hospital demonstrations where explainability, safe response behavior, and end-to-end voice interaction are required.

---

## 2. Project Goals and Scope

### 2.1 Primary Goals

- Provide safe, supportive health guidance (not diagnosis)
- Support both text and voice conversations
- Use retrieval from curated documents for grounded responses
- Retain semantic memory of prior interactions
- Expose clear APIs for chat, voice, and calculators
- Present orchestration transparency in the UI

### 2.2 Out-of-Scope (Current Version)

- Clinical diagnosis or treatment prescription
- Real-time bidirectional WebSocket audio streaming
- Multi-tenant authentication and authorization
- Full observability stack (Prometheus/Grafana/OpenTelemetry)

---

## 3. High-Level Architecture

The runtime architecture is organized into layers:

1. Interface Layer
- FastAPI endpoints for health, chat, streaming chat, voice, and tools
- Professional web UI in frontend/index.html

2. Orchestration Layer
- PlannerAgent: determines intent, urgency hints, route steps
- OrchestratorAgent: executes the final plan and composes outputs

3. Intelligence Layer
- GeminiService for response generation (standard and streaming)
- RAGAgent for retrieval from FAISS-backed LlamaIndex store
- ToolAgent for deterministic calculators and symptom helper
- MemoryAgent for semantic recall and persistence

4. Safety Layer
- SafetyGuard urgency assessment and safe response enforcement

5. Voice Layer
- WhisperSTTService using faster-whisper for transcription
- TTSService using gTTS (or optional Coqui)

6. Storage Layer
- FAISS index for RAG documents
- FAISS index for conversation memory
- JSON record store for memory metadata
- Storage folder for generated audio

---

## 4. Repository Structure and Responsibilities

### 4.1 Application Modules

- app/main.py
  - Creates FastAPI app
  - Registers API router
  - Mounts storage folder as static files for audio playback

- app/api/routes.py
  - Defines all HTTP routes
  - Maintains singleton service instances via lru_cache
  - Contains response cache for repeated chat queries
  - Contains streaming chat endpoint (NDJSON over StreamingResponse)

- app/core/config.py
  - Centralized settings via pydantic-settings
  - Directory bootstrap through ensure_dirs
  - TTS configuration (language/accent/speed)

- app/core/schemas.py
  - Pydantic contracts for requests/responses

- app/core/safety.py
  - Urgent keyword detection
  - Safety disclaimer and emergency escalation message composition

- app/agents/planner_agent.py
  - Rule-based plan generation with steps and flags

- app/agents/orchestrator_agent.py
  - Core pipeline execution and final response assembly

- app/agents/rag_agent.py
  - Query-time retrieval from prebuilt index

- app/agents/tool_agent.py
  - Tool invocation for symptom checker and calculator endpoints

- app/memory/memory_agent.py
  - Semantic embedding, FAISS add/search, JSON persistence

- app/rag/index_manager.py
  - Loads existing RAG index or builds one from docs directory

- app/services/llm_service.py
  - Text generation and token streaming wrappers for Gemini

- app/services/stt_service.py
  - Local transcription with Whisper model (CPU int8)

- app/services/tts_service.py
  - Speech synthesis (gTTS default, Coqui optional)

- app/tools/health_tools.py
  - Deterministic BMI, hydration, and symptom helper logic

### 4.2 Frontend

- frontend/index.html
  - Single-page glassmorphism UI
  - Tabs for chat, live voice, calculators, memory, architecture
  - Streaming chat rendering
  - Live orchestration stage chips (Planning, Context, Generating, Finalized)

### 4.3 Data and Storage

- data/docs
  - Domain files for RAG indexing

- data/memory/memory_records.json
  - Persistent memory records and embeddings

- storage/faiss
  - RAG index persistence

- storage/memory_faiss
  - Memory FAISS index

- storage
  - Temporary input audio and generated response audio

### 4.4 Tests

- tests/test_tools.py
  - Validates BMI/hydration/symptom helper outputs

- tests/test_planner.py
  - Validates urgency detection and requested tool selection

- tests/test_orchestrator.py
  - Validates safety application and memory persistence behavior via stubs

---

## 5. Technology Stack

## 5.1 Backend and API

- fastapi==0.115.6
- uvicorn[standard]==0.32.1
- python-multipart==0.0.19
- pydantic==2.10.3
- pydantic-settings==2.7.0

## 5.2 LLM and NLP

- google-generativeai==0.8.3
- sentence-transformers==3.3.1
- transformers==4.41.2
- tokenizers==0.19.1
- huggingface-hub==0.27.1

## 5.3 Retrieval and Vector Databases

- llama-index-core==0.12.8
- llama-index-readers-file==0.4.2
- llama-index-vector-stores-faiss==0.3.0
- llama-index-embeddings-huggingface==0.5.0
- faiss-cpu==1.9.0.post1
- numpy==1.26.4

## 5.4 Voice

- faster-whisper==1.1.0 (local STT)
- gTTS==2.5.4 (default TTS)
- pydub==0.25.1
- Optional: Coqui TTS backend

## 5.5 Quality and Validation

- pytest==8.3.4
- httpx==0.28.1

---

## 6. Configuration Model

Environment and runtime options are defined in app/core/config.py.

Important settings:

- app_name, host, port, log_level
- gemini_api_key, gemini_model
- embedding_model
- rag_top_k, memory_top_k
- docs_dir, rag_index_dir, memory_index_dir, memory_db_path
- whisper_model_size
- tts_engine
- tts_language, tts_tld, tts_slow
- output_audio_path

Behavioral notes:

- If gemini_api_key is missing, the system falls back to a generic safe text response.
- ensure_dirs creates required folders on startup.
- Current voice defaults are UK accent and normal speed via gTTS:
  - tts_language=en
  - tts_tld=co.uk
  - tts_slow=false

---

## 7. Data Contracts (Schemas)

### 7.1 Chat

ChatRequest:
- user_id: string
- query: string

ChatResponse:
- user_id
- query
- plan: QueryPlan
- response_text
- retrieved_context: string[]
- tool_results: object
- memory_hits: string[]
- urgent: boolean

### 7.2 Planning

QueryPlan:
- intent: string
- urgent: boolean
- requested_tools: string[]
- needs_rag: boolean
- steps: PlanStep[]

PlanStep:
- action: one of respond, rag, tool, memory, safety
- detail: string

### 7.3 Tools

ToolBMIRequest:
- weight_kg > 0
- height_cm > 0

ToolHydrationRequest:
- weight_kg > 0
- activity_level in low, moderate, high

### 7.4 Voice

VoiceResponse:
- user_id
- transcript
- response_text
- output_audio_path

---

## 8. API Reference

Base URL (local): http://localhost:8000

### 8.1 GET /health

Purpose:
- Liveness/health check

Response:
- { status: "ok" }

### 8.2 GET /

Purpose:
- Serves frontend dashboard

### 8.3 POST /chat/query

Purpose:
- Standard non-streaming chat

Key behavior:
- Uses in-memory cache with TTL (300 seconds) by normalized user_id+query key

### 8.4 POST /chat/query/stream

Purpose:
- Progressive response streaming for improved first-token latency

Transport:
- application/x-ndjson

Event types:

1. meta
- Includes plan, urgency, route, cache indicator

2. token
- Incremental text chunk

3. final
- Full final ChatResponse payload

4. error
- Error message in stream

### 8.5 POST /voice/query

Purpose:
- End-to-end voice request handling

Pipeline:
- Save uploaded audio to unique temp path
- STT transcription
- Orchestrator processing
- TTS synthesis
- Return transcript + text response + output audio path

Error handling:
- Empty audio file -> 400
- Transcription failure -> 400
- No speech detected -> 400
- Unexpected failures -> 500

### 8.6 POST /tools/bmi

Purpose:
- BMI computation with category and recommendation

### 8.7 POST /tools/hydration

Purpose:
- Daily hydration estimate with recommendation text

---

## 9. Detailed Method-by-Method Behavior

### 9.1 PlannerAgent.plan

Approach:
- Rule-based parsing of lowercased query

Outputs:
- urgent flag from critical keywords
- requested_tools list from domain keywords
- needs_rag flag based on explanation/recommendation style questions
- ordered step list for transparency and orchestration

Why this approach:
- Fast, deterministic behavior suitable for safety-sensitive triage-first routing

### 9.2 OrchestratorAgent.process_query

Execution order:

1. Build plan from planner
2. Assess urgency with safety guard
3. Recall semantic memory hits
4. Retrieve RAG context if needed
5. Execute requested tool set if needed
6. Build final prompt with query + context + tools + urgency
7. Generate LLM response
8. Apply safety wrapper/disclaimer
9. Persist interaction into memory
10. Return full ChatResponse

Design benefits:
- Clear data dependencies
- Strong explainability through plan and route trace
- Safety policy applied after generation to guarantee compliance

### 9.3 SafetyGuard.assess and SafetyGuard.apply

assess:
- Keyword scan for emergency patterns

apply:
- If urgent: force emergency escalation message plus disclaimer
- If non-urgent: append disclaimer if not already present

### 9.4 RAGAgent.retrieve

- Uses as_retriever with similarity_top_k from settings
- Returns list of stripped node content strings

### 9.5 MemoryAgent

add_interaction:
- Builds combined text entry
- Embeds using SentenceTransformer with normalized vectors
- Adds to FAISS IP index
- Persists full record to JSON
- Persists FAISS index to disk

recall:
- Embeds query
- Vector search for top_k
- Returns matching historical text snippets

### 9.6 GeminiService

generate_text:
- Standard single-shot generation
- Fallback safe guidance if model/key unavailable

generate_text_stream:
- Uses Gemini stream mode
- Yields chunk.text progressively for NDJSON token events

### 9.7 WhisperSTTService.transcribe

- Validates file path
- Runs faster-whisper model on CPU int8
- Joins all segment text into final transcript

### 9.8 TTSService.synthesize

- Resolves output path and ensures parent directory
- If engine=coqui: uses local model synthesis
- Else gTTS with configurable language/accent/speed

---

## 10. Frontend Interaction Model

### 10.1 Chat Flow

- User submits text query
- UI sends request to /chat/query/stream
- UI receives NDJSON lines and updates:
  - Stage chips
  - Assistant text progressively
  - Final orchestration trace

### 10.2 Voice Flow

- Press-and-hold capture (browser MediaRecorder)
- Upload audio to /voice/query
- Display transcript and response
- Auto-play synthesized audio from /storage static mount

### 10.3 Demo Transparency Features

- Orchestration trace panel
- Stream stage indicator bar
- Professional wording for clinical demo context
- Safety and governance explanation section

---

## 11. Caching and Performance Strategy

Implemented optimizations:

1. Chat response cache
- Key: normalized user_id + query
- TTL: 300 seconds
- Repeated queries can return near-instantly

2. Streaming endpoint
- Improves perceived latency through first token rendering

3. Voice temp file uniqueness
- UUID-prefixed filenames reduce collision risk in concurrent voice requests

Observed baseline (local environment sample):

- Tools endpoints: low single-digit ms
- Cold chat requests: high seconds (LLM/network bound)
- Cached repeated chat requests: near-instant

---

## 12. Testing and Validation

Current test status:
- 6 tests passing

Coverage areas:

- Tool math and helper outputs
- Planner urgency and tool selection
- Orchestrator safety behavior and memory write path

Recommended additions:

- API integration tests for /chat/query/stream event ordering
- Voice endpoint tests with fixture audio samples
- Regression tests for response cache TTL behavior
- Load tests for concurrent voice and chat requests

---

## 13. Build, Run, and Operations

### 13.1 Setup

1. Create virtual environment
2. Install dependencies
3. Configure environment variables
4. Place documents in data/docs
5. Build or auto-load indexes

### 13.2 Local Run

- Start API: uvicorn app.main:app --reload
- Access UI: http://localhost:8000
- API docs: http://localhost:8000/docs

### 13.3 Operational Notes

- First model load may be slow
- gTTS depends on network availability
- Coqui optional install provides alternative local TTS engine
- Memory JSON can grow over time; add rotation/retention in production

---

## 14. Safety, Clinical Positioning, and Compliance Notes

Current safeguards:

- Urgent phrase detection and forced emergency escalation text
- Non-diagnostic disclaimer on all responses
- Separation of deterministic tools and generated guidance

Important reminder:

- This project is an informational assistant and not a medical diagnostic system.
- For real clinical deployment, add policy controls, audit logging, PHI handling controls, identity/access management, and regulatory review workflows.

---

## 15. Known Limitations

- Planner is keyword/rule-based, not probabilistic intent classification
- Stream endpoint currently sends plain NDJSON (not SSE framing)
- RAG quality depends on document quality and curation
- Memory persistence is synchronous on each write
- No authentication or role-based access controls in current build

---

## 16. Recommended Next Improvements

Priority 1:
- Add structured telemetry and stage timing metrics (planner, RAG, LLM, TTS)
- Add async task queue for TTS generation on longer responses
- Add API authentication and audit trail

Priority 2:
- Add confidence/scoring metadata in retrieval trace
- Add model fallback strategy and retry policy
- Add memory retention policy and archival

Priority 3:
- Add real-time bi-directional voice streaming
- Add multilingual mode and clinical terminology packs
- Add admin dashboard for prompt/version governance

---

## 17. End-to-End Request Walkthrough

Example: voice question about headache

1. Browser records audio and submits multipart file to /voice/query
2. Backend stores temporary audio in storage/input_<uuid>_<name>
3. WhisperSTTService transcribes speech to text
4. Orchestrator pipeline executes:
   - planner.plan
   - safety.assess
   - memory.recall
   - rag.retrieve if required
   - tool.run if required
   - llm.generate_text
   - safety.apply
   - memory.add_interaction
5. TTSService synthesizes response audio
6. Response payload returns transcript, answer text, and audio file path
7. Frontend displays transcript and plays audio

---

## 18. Glossary

- RAG: Retrieval-Augmented Generation
- STT: Speech-to-Text
- TTS: Text-to-Speech
- NDJSON: Newline-delimited JSON
- FAISS: Facebook AI Similarity Search library for vector retrieval
- Urgent flag: Boolean marker indicating high-risk symptom language

---

## 19. Quick Reference Commands

Install:
- pip install -r requirements.txt

Run server:
- uvicorn app.main:app --reload

Run tests:
- pytest -q

Build RAG index:
- python -m app.scripts.build_rag_index

---

## 20. Document Version

- Version: 1.0
- Last updated: 2026-04-25
- Scope: Current implemented system in this repository
