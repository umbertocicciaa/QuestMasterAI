#!/bin/bash

# QuestMaster AI Docker Setup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 QuestMaster AI - Docker Setup${NC}"
echo "================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found.${NC}"
    if [ -f ".env.template" ]; then
        echo -e "${BLUE}📝 Creating .env from template...${NC}"
        cp .env.template .env
        echo -e "${YELLOW}Please edit .env file with your OpenAI API key before continuing.${NC}"
        read -p "Press Enter after editing .env file..."
    else
        echo -e "${RED}❌ .env.template not found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Load environment variables to check
set -a
source .env
set +a

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo -e "${RED}❌ OpenAI API key not set in .env file.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configuration OK${NC}"

# Ask what to do
echo ""
echo "What would you like to do?"
echo "1) Build and run QuestMaster (full pipeline)"
echo "2) Build Docker image only"
echo "3) Run existing image"
echo "4) Run in development mode"
echo "5) Run interactive CLI"
echo "6) Stop and remove containers"
echo "7) View logs"

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Building and running QuestMaster...${NC}"
        docker-compose up --build
        ;;
    2)
        echo -e "${GREEN}🔨 Building Docker image...${NC}"
        docker-compose build
        echo -e "${GREEN}✅ Build complete!${NC}"
        ;;
    3)
        echo -e "${GREEN}▶️  Running QuestMaster...${NC}"
        docker-compose up
        ;;
    4)
        echo -e "${GREEN}🛠️  Running in development mode...${NC}"
        docker-compose --profile dev up -p 8501:8501 questmaster-dev
        ;;
    5)
        echo -e "${GREEN}💻 Running interactive CLI...${NC}"
        docker-compose --profile cli run --rm -p 8501:8501 questmaster-cli 
        ;;
    6)
        echo -e "${YELLOW}🛑 Stopping and removing containers...${NC}"
        docker-compose down
        echo -e "${GREEN}✅ Cleanup complete!${NC}"
        ;;
    7)
        echo -e "${BLUE}📋 Viewing logs...${NC}"
        docker-compose logs -f
        ;;
    *)
        echo -e "${RED}❌ Invalid choice.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Done!${NC}"

if [ "$choice" = "1" ] || [ "$choice" = "3" ]; then
    echo ""
    echo -e "${BLUE}📱 QuestMaster AI is running at: http://localhost:8501${NC}"
    echo -e "${BLUE}🔧 Use Ctrl+C to stop the container${NC}"
fi
