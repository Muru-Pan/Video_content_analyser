FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data/audio data/transcripts data/indexes data/temp

EXPOSE 8000
CMD ["python", "main.py"]
