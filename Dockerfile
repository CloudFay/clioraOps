# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

LABEL maintainer="Faith Omobude" \
    description="DevOps Learning Companion powered by AI" \
    version="0.2.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY clioraOps_cli/ ./clioraOps_cli/
COPY setup.py .
COPY README.md .
COPY LICENSE .

# Install application
RUN pip install --user -e .

# Create directory for user workspace
RUN mkdir -p /workspace && chmod 777 /workspace
WORKDIR /workspace

# Create volume mount points
VOLUME ["/workspace", "/root/.clioraops"]

# Expose port for web interface
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD clioraops status || exit 1

# Set entry point
ENTRYPOINT ["clioraops"]

# Default command
CMD ["start"]