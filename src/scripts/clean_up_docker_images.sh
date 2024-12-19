#!/bin/bash

echo "🐳 Starting Docker cleanup..."

# Remove all stopped containers
echo "🔍 Checking for stopped containers..."
STOPPED_CONTAINERS=$(docker ps -a -q -f status=exited)
if [ ! -z "$STOPPED_CONTAINERS" ]; then
    echo "🗑️  Removing stopped containers..."
    docker rm $STOPPED_CONTAINERS
fi

# Remove dangling images
echo "🔍 Checking for dangling images..."
DANGLING_IMAGES=$(docker images -f "dangling=true" -q)
if [ ! -z "$DANGLING_IMAGES" ]; then
    echo "🗑️  Removing dangling images..."
    docker rmi $DANGLING_IMAGES
fi

# Remove unused networks
echo "🔍 Checking for unused networks..."
docker network prune -f

# Remove unused volumes
echo "🔍 Checking for unused volumes..."
docker volume prune -f

echo "✨ Docker cleanup complete!"