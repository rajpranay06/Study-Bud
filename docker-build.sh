#!/bin/bash

# Get GROQ API key from .env file if it exists
if [ -f .env ]; then
    source .env
fi

# Fallback if not found in .env
if [ -z "$GROQ_API_KEY" ]; then
    echo "Warning: GROQ_API_KEY not found in .env file"
    echo "Enter your GROQ API key:"
    read GROQ_API_KEY
fi

# Choose which Dockerfile to use
if [ "$1" == "simple" ]; then
    DOCKERFILE="Dockerfile.simple"
    echo "Using simplified Docker build approach..."
else
    DOCKERFILE="Dockerfile"
    echo "Using standard Docker build approach..."
fi

# Build the Docker image
echo "Building Docker image with GROQ API key: $GROQ_API_KEY"
docker build --build-arg GROQ_API_KEY=$GROQ_API_KEY -t study-bud:latest -f $DOCKERFILE .

# Run the container
echo "Starting container..."
docker run -p 8000:8000 study-bud:latest 