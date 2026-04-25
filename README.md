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

### 1. Install
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Optional (Coqui TTS backend):
```bash
pip install TTS==0.22.0
```

### 2. Configure
```bash
copy .env.example .env
```
Set `GEMINI_API_KEY` in `.env`.

### 3. Add RAG docs
Place `.txt`, `.md`, or `.pdf` files in `data/docs/`.

### 4. Build RAG index
```bash
python -m app.scripts.build_rag_index
```

### 5. Run API
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
- Coqui TTS is optional and requires additional model assets on first run.
- gTTS is the default and may require internet access.
