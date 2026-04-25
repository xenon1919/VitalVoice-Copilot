# Personal Health Voice Copilot

Production-grade multi-agent, voice-enabled AI system for safe health guidance.

## Features
- Multi-agent orchestration (`Orchestrator`, `Planner`, `RAG`, `Tool`, `Memory`)
- RAG with LlamaIndex + FAISS + MiniLM (`all-MiniLM-L6-v2`)
- Local STT with Whisper models via `faster-whisper`
- Voice output using Coqui TTS or gTTS
- Safety-first response policy (no diagnosis, emergency escalation)
- FastAPI backend with text and voice endpoints

## Architecture
1. Voice Input Layer (Whisper-compatible local inference)
2. Planner Agent (intent + action plan)
3. Orchestrator Agent (flow control + composition)
4. RAG Agent (LlamaIndex + FAISS + MiniLM retrieval)
5. Tool Agent (BMI, hydration, symptom risk helper)
6. Memory Agent (short-term + long-term semantic recall)
7. Voice Output Layer (Coqui/gTTS)

## Quick Start

### 1. Install `uv`
If you don't have `uv` installed:
```bash
pip install uv
```

### 2. Create virtual environment
```bash
uv venv
.venv\Scripts\activate
```

### 3. Sync dependencies
```bash
uv sync
```

Optional (Coqui TTS backend):
```bash
uv pip install TTS==0.22.0
```

### 4. Configure
```bash
copy .env.example .env
```
Set `GEMINI_API_KEY` in `.env`.

### 5. Add RAG docs
Place `.txt`, `.md`, or `.pdf` files in `data/docs/`.

### 6. Build RAG index
```bash
python -m app.scripts.build_rag_index
```

### 7. Run API
```bash
uvicorn app.main:app --reload
```

## API Endpoints
- `GET /health`
- `POST /chat/query` (text in, text out)
- `POST /voice/query` (audio in, text + audio file path out)
- `POST /tools/bmi`
- `POST /tools/hydration`

## Safety Policy
- Never presents diagnosis.
- Always states this is general advice.
- Escalates urgent symptoms (e.g., chest pain, breathing difficulty) to immediate medical care.

## Tests
```bash
pytest -q
```

## Notes
- This project uses `uv` for fast, reliable dependency management with `pyproject.toml`.
- Coqui TTS is optional and requires additional model assets on first run.
- gTTS is the default and may require internet access.
