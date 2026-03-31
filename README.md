Video Content Analyzer
Production-ready, self-hosted video intelligence for education and eLearning workflows. Paste a YouTube URL or upload a media file to generate a transcript, summary, title, category tag, and grounded Q&A — where every answer links back to the exact timestamp in the video.
Transcription and embeddings run locally. LLM generation is handled by Groq's free API (no cost for standard usage). No data is stored by any third party.

Features

Local transcription via OpenAI Whisper — no API key required
Semantic search via FAISS + sentence-transformers embeddings
Grounded Q&A via Groq API (Llama 3 / Mixtral) — answers sourced only from the transcript
Timestamp-linked sources — every answer includes a "Jump to MM:SS" button
YouTube player integration — clicking a timestamp seeks the embedded player directly
Artifact caching — transcript and FAISS index reused on reruns unless force-reprocessed
Separate frontend and backend — React + Vite + Nginx and FastAPI + Uvicorn
Single-command Docker deployment — two containers orchestrated by Docker Compose
Free stack — Groq free tier, no paid services, no external data storage


Tech Stack
LayerToolsFrontendReact 18, TypeScript, Vite, NginxBackendPython 3.11, FastAPI, UvicornTranscriptionOpenAI Whisper (local)Embeddingssentence-transformers all-MiniLM-L6-v2 (local)Vector storeFAISS (CPU, local)LLMGroq API — llama3-8b-8192 (default)Media handlingyt-dlp, ffmpeg, ffprobeDeploymentDocker Compose

Repository Layout
textvideo-analyzer/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── app.py                  # FastAPI app and routes
│   ├── main.py                 # Uvicorn entry point
│   ├── check_env.py            # Pre-flight dependency checker
│   ├── requirements.txt
│   ├── core/
│   │   ├── chunker.py
│   │   ├── downloader.py
│   │   ├── embedder.py
│   │   ├── qa_chain.py
│   │   ├── summarizer.py
│   │   ├── transcriber.py
│   │   └── utils.py
│   ├── prompts/
│   │   ├── qa_prompt.txt
│   │   ├── summary_prompt.txt
│   │   └── category_prompt.txt
│   └── data/                   # Mounted as Docker volume
│       ├── audio/
│       ├── transcripts/
│       ├── indexes/
│       └── temp/
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    └── src/
        ├── api.ts
        ├── App.tsx
        ├── types.ts
        ├── components/
        └── hooks/

Prerequisites
Docker (recommended)

Docker Desktop — https://www.docker.com/products/docker-desktop
8 GB RAM minimum
10 GB free disk space
Groq API key — https://console.groq.com (free, no credit card required)

Local development

Python 3.11+
Node.js 20+
ffmpeg and ffprobe (system install — see Windows notes below)
Groq API key — https://console.groq.com


Get a Groq API Key

Go to https://console.groq.com
Sign up for a free account (no credit card required)
Navigate to API Keys → Create API Key
Copy the key — it starts with gsk_...
Add it to your .env file:

bash   GROQ_API_KEY=gsk_your_key_here
Groq's free tier includes generous rate limits suitable for development and small production workloads.

Docker Deployment
bash# 1. Clone the repository
git clone https://github.com/yourname/video-analyzer.git
cd video-analyzer

# 2. Create your env file
cp .env.example .env

# 3. Add your Groq API key to .env
# GROQ_API_KEY=gsk_your_key_here

# 4. Build and start all services
docker compose up --build
Service URLs
ServiceURLFrontendhttp://localhostBackend APIhttp://localhost:8000API docs (Swagger)http://localhost:8000/docs
Stop and restart
bash# Stop containers, keep all data volumes
docker compose down

# Stop and delete all data (clean slate)
docker compose down -v

# Start again without rebuilding
docker compose up

Local Development
1. Backend
bashcd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python check_env.py

python main.py
Backend runs at: http://127.0.0.1:8000
2. Frontend (separate terminal)
bashcd frontend
npm install
npm run dev
Frontend runs at: http://localhost:5173
Create frontend/.env.local:
bashVITE_API_URL=http://127.0.0.1:8000

API Reference
GET /api/health
json{ "status": "ok", "groq": "reachable" }
POST /api/process
Accepts multipart/form-data.
FieldTypeRequiredDefaultyoutube_urlstringone of these two—fileFileone of these two—whisper_modelstringnobaseforce_reprocessstringnofalse
Whisper model options: tiny, base, small, medium
Response
json{
  "video_id": "abc123",
  "transcript": "full transcript text...",
  "segments": [{ "start": 0.0, "end": 4.2, "text": "..." }],
  "summary": "summary text",
  "title": "Generated Title",
  "category": "Education",
  "status": "Ready. Processed video id: abc123"
}
POST /api/ask
Accepts application/json. Requires a video to be processed first.
json{
  "video_id": "abc123",
  "question": "What is the main concept explained?"
}
Response
json{
  "answer": "grounded answer text",
  "sources": [
    {
      "text": "source chunk excerpt",
      "timestamp": "01:42",
      "start_seconds": 102.4,
      "chunk_index": 3
    }
  ]
}

Environment Variables
Copy .env.example to .env and fill in your values.
VariableDefaultDescriptionGROQ_API_KEY(required)Your Groq API key from console.groq.comGROQ_MODELllama3-8b-8192Groq model to use for generationWHISPER_MODELbaseDefault Whisper model for transcriptionDATA_DIR/app/dataPath to data storage directoryWHISPER_CACHE/app/whisper_cachePath to Whisper model cacheFFMPEG_LOCATION(unset)Windows local dev only — path to ffmpeg/bin
Supported Groq models
ModelSpeedContextBest forllama3-8b-8192Fastest8KDefault — good for most videosllama3-70b-8192Slower8KBetter reasoning and answer qualitymixtral-8x7b-32768Fast32KLong transcripts and detailed content

docker-compose.yml
Groq replaces Ollama — only two containers are needed:
yamlversion: "3.9"

services:

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: vca-backend
    env_file:
      - .env
    environment:
      - DATA_DIR=/app/data
      - WHISPER_CACHE=/app/whisper_cache
    volumes:
      - app_data:/app/data
      - whisper_cache:/app/whisper_cache
    ports:
      - "8000:8000"
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: vca-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  app_data:
  whisper_cache:

Windows Local Development Notes
These steps apply only when running the backend locally on Windows. In Docker, ffmpeg is installed automatically inside the Linux container.
Install ffmpeg (system binary)

Download ffmpeg-release-essentials.zip from https://www.gyan.dev/ffmpeg/builds/
Extract to C:\ and rename the folder to ffmpeg
Confirm the following files exist:

   C:\ffmpeg\bin\ffmpeg.exe
   C:\ffmpeg\bin\ffprobe.exe

Add C:\ffmpeg\bin to Windows System PATH:

Search environment variables → Edit system environment variables
Environment Variables → System variables → Path → Edit → New
Enter C:\ffmpeg\bin → OK on all dialogs


Open a new terminal and verify:

bash   ffmpeg -version
   ffprobe -version

Do not install ffmpeg via pip. The pip package is a broken wrapper. Only the system binary works.

Node.js for yt-dlp
bashnode --version    # must be v18 or higher
Download from https://nodejs.org if not installed.
