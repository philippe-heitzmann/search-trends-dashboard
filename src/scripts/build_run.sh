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
docker run -p 8501:8501 $IMAGE_NAME

# Check if the container ran successfully
if [ $? -ne 0 ]; then
  echo "Docker container failed to run. Exiting."
  exit 1
fi

echo "The Related Queries Dashboard is running on http://localhost:8501"
