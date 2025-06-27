#!/bin/bash

set -e

# Change to project root directory (two levels up from this script)
cd "$(dirname "$0")/../.."

# Build the Docker image
echo "[INFO] Building Docker image..."
docker build -f backend/run_scripts/Dockerfile.selenium -t etsy-scraper .
echo "[INFO] Docker image built successfully."

# Run the container with volume mounts
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/.env:/app/.env \
    etsy-scraper /bin/bash