# Stage 1: Build Frontend
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
# Copy package files and install dependencies
COPY src/phase8_ui/frontend/package*.json ./
RUN npm install
# Copy frontend source and build static export
COPY src/phase8_ui/frontend/ .
# Next.js export requires output: 'export' in next.config.ts
# Ensuring build creates the 'out' directory
RUN npm run build

# Stage 2: Backend & Runner
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for ChromaDB and other libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Copy static frontend build from Stage 1 to the backend static directory
COPY --from=frontend-builder /app/frontend/out /app/src/phase8_ui/static

# Expose port for Hugging Face Spaces
EXPOSE 7860

# Run FastAPI app with uvicorn
CMD ["uvicorn", "src.phase8_ui.app:app", "--host", "0.0.0.0", "--port", "7860"]
