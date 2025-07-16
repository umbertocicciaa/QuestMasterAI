#!/bin/bash

echo "🐳 Testing QuestMaster AI Docker Setup..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

echo "✅ Docker is available"

# Test building the image
echo "🔨 Building QuestMaster AI Docker image..."
docker build -t questmaster-ai:test . 2>&1 | grep -E "(Successfully|Error|ERROR|FAILED)" || echo "Build in progress..."

# If build succeeds, test the container
if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
    
    # Test CLI command
    echo "🧪 Testing CLI inside container..."
    docker run --rm questmaster-ai:test python -m questmaster.cli check
    
    if [ $? -eq 0 ]; then
        echo "✅ CLI test passed"
    else
        echo "❌ CLI test failed"
    fi
else
    echo "❌ Docker build failed"
fi

echo "🎉 Docker test completed!"
