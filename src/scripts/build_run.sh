#!/bin/bash

# Script to build and run the Docker container for the Related Queries Dashboard

# Name of the Docker image
IMAGE_NAME="related-queries-dashboard"

# Step 1: Build the Docker image
echo "Building the Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME .

# Check if the build was successful
if [ $? -ne 0 ]; then
  echo "Docker build failed. Exiting."
  exit 1
fi

# Step 2: Run the Docker container
echo "Running the Docker container..."
docker run --rm -p 8501:8501 \
  -v "$(pwd)/data:/app/data" \
  $IMAGE_NAME

# Check if the container ran successfully
if [ $? -ne 0 ]; then
  echo "Docker container failed to run. Exiting."
  exit 1
fi

# Step 3: Cleanup - Remove the Docker image
echo "Cleaning up - Removing Docker image..."
docker rmi $IMAGE_NAME

echo "The Related Queries Dashboard has finished running and cleaned up resources."
