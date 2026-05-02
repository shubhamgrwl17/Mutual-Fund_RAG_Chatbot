FROM python:3.11-slim

WORKDIR /app

# Minimal dependencies for running a Chroma HTTP server
RUN pip install --no-cache-dir chromadb

EXPOSE 8000

# Chroma serves HTTP on 0.0.0.0:8000 by default for this command
CMD ["chroma", "run", "--host", "0.0.0.0", "--port", "8000"]

