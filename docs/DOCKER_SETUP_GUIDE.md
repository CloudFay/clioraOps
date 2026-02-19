# Docker Setup Guide

This guide explains how to run ClioraOps using Docker for a consistent, isolated environment.

## Quick Start (Docker Compose)

The easiest way to run ClioraOps with its local AI backup is using Docker Compose.

1.  **Configure environment**:
    ```bash
    export GEMINI_API_KEY="your-api-key"
    ```

2.  **Start services**:
    ```bash
    docker-compose up -d
    ```

3.  **Run commands**:
    ```bash
    docker-compose exec clioraops clioraops start
    ```

## Manual Image Build

If you want to build the image yourself:

```bash
./deployment/scripts/build_docker.sh 0.3.0
```

## Volumes & Persistence

ClioraOps persists its state in two main volumes:
- `workspace`: Where generated files and tutorials are stored.
- `clioraops-config`: Where your AI preferences and session history live.

## Networking

When running in Compose, ClioraOps can communicate with the local Ollama instance via the `ai-provider` alias.
