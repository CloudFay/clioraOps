#!/bin/bash

# ClioraOps Docker Build Script
# Usage: ./build_docker.sh [tag]

SET_TAG=${1:-latest}
IMAGE_NAME="clioraops"

echo "🚀 Building ClioraOps Docker image: ${IMAGE_NAME}:${SET_TAG}..."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    exit 1
fi

# Build the image
docker build -t "${IMAGE_NAME}:${SET_TAG}" .

if [ $? -eq 0 ]; then
    echo "✅ Successfully built ${IMAGE_NAME}:${SET_TAG}"
    echo "💡 Run it with: docker run -it ${IMAGE_NAME}:${SET_TAG}"
else
    echo "❌ Build failed."
    exit 1
fi
