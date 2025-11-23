# YouTube Video Summarizer - Docker Configuration
# 
# This Dockerfile creates a production-ready container for the YouTube Video Summarizer
# application. It includes both the Flask backend and React frontend in a single container
# for simplified deployment.
#
# Key Features:
# - Multi-stage build for optimized image size
# - Production-ready Python environment
# - Built React frontend served by Flask
# - Proper security configurations
# - Health checks for monitoring

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend build
WORKDIR /app/frontend

# Copy package files first for better Docker layer caching
COPY youtube-summarizer-frontend/package.json ./
COPY youtube-summarizer-frontend/pnpm-lock.yaml ./

# Install dependencies
RUN npm install -g pnpm && pnpm install

# Copy frontend source code
COPY youtube-summarizer-frontend/ ./

# Build the React application for production
RUN pnpm run build

# Stage 2: Production Python environment
FROM python:3.11-slim AS production

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_APP=src/main.py

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install dependencies
COPY youtube-summarizer/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY youtube-summarizer/src/ ./src/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./src/static/

# Create necessary directories
RUN mkdir -p src/database && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 5000 for the Flask application
EXPOSE 5000

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Start the Flask application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

