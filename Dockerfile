FROM debian:12-slim as builder

WORKDIR /app

# Install system dependencies and Python tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-distutils python3-venv python3-pip python3-dev build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies into a virtualenv to avoid
# system-managed environment issues (PEP 668). This keeps the builder clean.
COPY requirements.txt .
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Production stage using mandated base image debian:12-slim
FROM debian:12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed Python virtualenv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Ensure virtualenv binaries are on PATH
ENV PATH=/opt/venv/bin:$PATH

# Expose ports
EXPOSE 8038 8138

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8138/api/v1/health || exit 1

# Start both backend and frontend services
CMD ["sh", "-c", "python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8138 & python3 -m http.server 8038 --directory dashboard"]