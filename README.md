# Video Content Analyzer

Production-ready, self-hosted video intelligence for education and eLearning workflows. The application converts YouTube videos or uploaded media into searchable knowledge assets with transcript, summary, title, category, grounded Q&A, and timestamp-linked source navigation.

## Highlights

- Separate React frontend and FastAPI backend
- Whisper-based local transcription
- FAISS semantic retrieval with sentence-transformers embeddings
- Ollama + Mistral for summary and grounded Q&A
- Timestamp-linked answers for direct study navigation
- Docker Compose deployment with frontend, backend, and Ollama services
- 100% free and open-source stack

## Repository Layout

```text
video-analyzer/
|-- docker-compose.yml
|-- .env.example
|-- README.md
|-- backend/
|   |-- Dockerfile
|   |-- main.py
|   |-- app.py
|   |-- requirements.txt
|   |-- check_env.py
|   |-- core/
|   |-- prompts/
|   `-- data/
`-- frontend/
    |-- Dockerfile
    |-- nginx.conf
    |-- package.json
    |-- vite.config.ts
    |-- index.html
    `-- src/
```

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python check_env.py
python main.py
```

Backend URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Ollama

```bash
ollama serve
ollama pull mistral
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: [http://127.0.0.1:5173](http://127.0.0.1:5173)

Optional local frontend env:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Docker Production

```bash
cp .env.example .env
docker compose up --build
```

On first run, pull the model:

```bash
docker exec vca-ollama ollama pull mistral
```

Services:

- Frontend: [http://localhost](http://localhost)
- Backend API: [http://localhost:8000](http://localhost:8000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Ollama: [http://localhost:11434](http://localhost:11434)

## API Endpoints

- `GET /api/health`
- `POST /api/process`
- `POST /api/ask`

## Notes

- Cached transcript and FAISS index artifacts are reused unless `force_reprocess=true`.
- Uploaded file timestamps are shown as references; direct player seeking is available for YouTube URLs.
- For local Windows development, install system `ffmpeg` and `ffprobe`, and ensure Node.js is available for `yt-dlp`.
