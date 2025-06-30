# Multi-stage build for Flask backend
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Build stage
FROM base AS builder

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM base AS production

# Create non-root user
RUN groupadd --gid 1001 flask && \
    useradd --uid 1001 --gid flask --shell /bin/bash --create-home flask

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/flask/.local

# Copy application code
COPY --chown=flask:flask . .

# Make startup script executable
RUN chmod +x start.sh

# Set PATH to include local binaries
ENV PATH=/home/flask/.local/bin:$PATH

# Set environment variables
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create necessary directories
RUN mkdir -p /app/logs && chown flask:flask /app/logs
RUN mkdir -p /app/data && chown flask:flask /app/data
RUN mkdir -p /app/instance && chown flask:flask /app/instance

# Switch to non-root user
USER flask

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health/', timeout=5)" || exit 1

# Run the application
CMD ["./start.sh"]