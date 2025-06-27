FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    wget \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Piper TTS Hindi model (hi_IN-pratham-medium)
RUN mkdir -p /app/models \
 && wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx?download=true -O /app/models/hi_IN-pratham-medium.onnx \
 && wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/hi/hi_IN/pratham/medium/hi_IN-pratham-medium.onnx.json?download=true -O /app/models/hi_IN-pratham-medium.onnx.json

# Copy application code
COPY . .

# Environment setup
ENV GUNICORN_CMD_ARGS="--workers=1 --threads=1 --timeout=60 --log-level=debug"
ENV PYTHONUNBUFFERED=1

# Run Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app
