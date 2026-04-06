# InsightStream — Extract Insights from Video Content

> A production-grade AI chatbot that extracts insights from any YouTube video using RAG (Retrieval Augmented Generation). Ask questions about any YouTube video and get accurate, context-aware answers.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-latest-green?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-FF4B4B?style=flat-square&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2%20%2B%20ECR-FF9900?style=flat-square&logo=amazonaws)

---

## Features

- **YouTube Transcript Extraction** — Automatically fetches transcripts for any YouTube video. Supports English, Hindi, Bengali, Tamil, Telugu, and 10+ other Indian regional languages with auto-translation to English.
- **RAG Pipeline** — Transcript is chunked, embedded, and stored in a FAISS vector store. Questions are answered using retrieved context — not hallucination.
- **Smart Caching** — Pipeline is built once per video and cached using `@lru_cache`. Follow-up questions on the same video are near-instant.
- **Proxy + Cookie Support** — Handles YouTube rate limiting via Webshare rotating proxies with automatic fallback to browser cookies.
- **Retry with Fallback** — First attempt uses proxy, subsequent attempts fall back to cookies, ensuring maximum reliability.
- **Multilingual Support** — Supports 15+ Indian languages with automatic English translation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│         (Video ID input, question, answer display)       │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                       │
│              /api/chat  (with @lru_cache)                │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    RAG Pipeline                          │
│                                                          │
│  YoutubeLoader → TextSplitter → EmbeddingModel          │
│       → VectorStore (FAISS) → Retriever → RAGChain      │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼───────┐         ┌────────▼────────┐
│  YouTube API  │         │  FAISS Index    │
│  (transcript  │         │  (saved locally │
│   fetching)   │         │   per video)    │
└───────────────┘         └─────────────────┘
```

---

## How It Works

```
1. User enters YouTube Video ID
        ↓
2. YoutubeLoader fetches transcript
   (proxy → cookies → direct fallback)
        ↓
3. RecursiveCharacterTextSplitter chunks transcript
   (chunk_size=1000, overlap=200)
        ↓
4. OpenAI text-embedding-3-small creates vectors
        ↓
5. FAISS stores vectors locally
        ↓
6. User asks a question
        ↓
7. FAISS retrieves top-4 similar chunks
        ↓
8. GPT-4o-mini generates answer from context
        ↓
9. Pipeline cached — follow-up questions are instant ⚡
```

---

## Project Structure

```
InsightStream/
│
├── backend/                    # FastAPI application
│   ├── main.py                 # App entry point
│   └── routes/
│       └── chat.py             # /api/chat endpoint with @lru_cache
│
├── frontend/                   # Streamlit UI
│   └── app.py
│
├── pipeline/                   # Orchestration layer
│   └── rag_pipeline.py         # Orchestrates all components
│
├── src/                        # Core components
│   ├── ingestion/              # YouTube transcript loader
│   ├── text_splitter/          # RecursiveCharacterTextSplitter
│   ├── embeddings/             # OpenAI embeddings
│   ├── vector_store/           # FAISS store
│   ├── retriever/              # Retriever
│   ├── chains/                 # RAG chain (LangChain)
│   ├── prompts/                # Prompt templates
│   ├── logger/                 # Rotating file + console logger
│   └── exception/              # Custom exception with traceback
│
├── config/
│   └── settings.py             # Pydantic settings
│
├── entity/
│   ├── config_entity.py        # Dataclass configs
│   └── artifact_entity.py      # Dataclass artifacts
│
├── artifacts/                  # Generated at runtime (gitignored)
│   └── faiss_index/            # FAISS vector store
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── .github/workflows/cicd.yml  # CI/CD → AWS ECR → EC2
├── requirements.txt
└── .env.example
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | GPT-4o-mini (OpenAI) |
| Embeddings | text-embedding-3-small (OpenAI) |
| RAG Framework | LangChain |
| Vector Store | FAISS |
| Transcript API | youtube-transcript-api |
| Proxy | Webshare Rotating Proxy |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Containerization | Docker + Docker Compose |
| Registry | AWS ECR |
| Deployment | AWS EC2 |
| CI/CD | GitHub Actions |

---

## Getting Started

### Prerequisites

- Python 3.12+
- OpenAI API key
- Webshare proxy credentials (optional but recommended)
- Browser cookies exported as `cookies.txt` (optional fallback)

### Local Setup

**1. Clone the repository:**
```bash
git clone https://github.com/Hello-Mitra/InsightStream.git
cd InsightStream
```

**2. Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file:**
```bash
cp .env.example .env
# Fill in your API keys
```

**5. Run the backend:**
```bash
uvicorn backend.main:app --port 5000 --reload
```

**6. Run the frontend (new terminal):**
```bash
streamlit run frontend/app.py
```

**7. Open in browser:**
```
http://localhost:8501
```

### Docker Setup

```bash
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```env
OPENAI_API_KEY=your_openai_api_key

# Optional — for YouTube rate limit bypass
WEBSHARE_PROXY_USERNAME=your_webshare_username
WEBSHARE_PROXY_PASSWORD=your_webshare_password
```

### Handling YouTube Rate Limits

InsightStream uses a three-tier fallback strategy:

```
Attempt 1 → Webshare rotating proxy  (fastest, most reliable)
        ↓ rate limited
Attempt 2 → Browser cookies.txt      (authenticated session)
        ↓ rate limited
Attempt 3 → Direct request           (may be rate limited)
```

To use cookies, export your YouTube browser cookies using the **"Get cookies.txt LOCALLY"** Chrome extension and place the file as `cookies.txt` in the project root.

---

## Supported Languages

InsightStream automatically detects and translates transcripts from:

`English` `Hindi` `Bengali` `Telugu` `Tamil` `Marathi` `Gujarati` `Kannada` `Malayalam` `Odia` `Assamese` `Punjabi` `Urdu` `Nepali` `Sinhala`

All non-English transcripts are automatically translated to English before processing.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Ask a question about a YouTube video |
| `GET` | `/health` | Health check |

Full interactive API docs at `http://localhost:5000/docs`

### Example Request

```json
POST /api/chat
{
    "video_id": "Y0SbCp4fUvA",
    "question": "Can you summarize this video?"
}
```

### Example Response

```json
{
    "answer": "This video discusses..."
}
```

---

## CI/CD Pipeline

```
git push origin main
        │
        ▼
Continuous-Integration (GitHub hosted runner)
        │
        ├── Lint with Ruff
        ├── Build backend Docker image
        ├── Push to AWS ECR
        ├── Build frontend Docker image
        └── Push to AWS ECR
        │
        ▼
Continuous-Deployment (EC2 self-hosted runner)
        │
        ├── Fix workspace permissions
        ├── Pull latest images from ECR
        ├── docker-compose down
        └── docker-compose up -d
```

---

## Performance

- **First question on a video** — 30-90 seconds (transcript fetch + embedding)
- **Follow-up questions** — < 3 seconds (pipeline cached via `@lru_cache`)
- **Cache capacity** — 5 videos cached simultaneously (`maxsize=5`)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Arijit Mitra**

[![GitHub](https://img.shields.io/badge/GitHub-Hello--Mitra-181717?style=flat-square&logo=github)](https://github.com/Hello-Mitra)