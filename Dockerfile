# Blender-Ollama MCP Server Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    portaudio19-dev \
    libasound2-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir \
    SpeechRecognition>=3.10.0 \
    pyaudio>=0.2.11 \
    edge-tts>=6.1.0 \
    playsound>=1.3.0 \
    requests

# Copy application code
COPY . .

# Create directories for databases and output
RUN mkdir -p /app/databases /app/output /app/temp_audio

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_URL=http://ollama:11434
ENV BLENDER_HOST=host.docker.internal
ENV BLENDER_PORT=9876

# Expose any ports if needed (MCP uses stdio, but for future expansion)
# EXPOSE 8000

# Default command
CMD ["python", "mcp_server.py"]

