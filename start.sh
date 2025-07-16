#!/bin/bash

# QuestMaster AI

set -e


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌟 QuestMaster AI - Agentic AI for Interactive Storytelling${NC}"
echo "================================================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo -e "${YELLOW}📝 Please edit .env file with your OpenAI API key and run again.${NC}"
        exit 1
    else
        echo -e "${RED}❌ .env.template not found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Load environment variables
echo -e "${BLUE}📋 Loading environment variables...${NC}"
set -a
source .env
set +a

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}📚 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -e .

# Check if Fast Downward exists
FAST_DOWNWARD_DIR="fast-downward-24.06.1"
if [ ! -d "$FAST_DOWNWARD_DIR" ]; then
    echo -e "${YELLOW}⚠️  Fast Downward not found. Please download and extract it to $FAST_DOWNWARD_DIR${NC}"
    echo -e "${YELLOW}💡 Download from: https://www.fast-downward.org/releases/24.06/fast-downward-24.06.1.tar.gz${NC}"
    echo -e "${YELLOW}📂 Extract to: $(pwd)/$FAST_DOWNWARD_DIR${NC}"
    exit 1
fi

# Check if Fast Downward is built
if [ ! -f "$FAST_DOWNWARD_DIR/builds/release/bin/downward" ]; then
    echo -e "${YELLOW}🔨 Building Fast Downward...${NC}"
    cd "$FAST_DOWNWARD_DIR"
    python build.py
    cd ..
fi

# Check requirements
echo -e "${BLUE}🔍 Checking system requirements...${NC}"
python -c "
import sys
sys.path.insert(0, 'src')
from questmaster.app import QuestMasterApp
from questmaster.core.logging import setup_logging

setup_logging(log_level='ERROR')
app = QuestMasterApp()
if not app.check_requirements():
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Requirements check failed. Please fix the issues above.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All requirements satisfied!${NC}"

# Ask user what to do
echo ""
echo "What would you like to do?"
echo "1) Run full pipeline (Phase 1 + Phase 2)"
echo "2) Run Phase 1 only (PDDL generation)"
echo "3) Run Phase 2 only (Story generation)"
echo "4) Start frontend (if already generated)"
echo "5) Check requirements only"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Running full QuestMaster pipeline...${NC}"
        python -m questmaster.cli run
        ;;
    2)
        echo -e "${GREEN}📝 Running Phase 1: PDDL Generation...${NC}"
        python -m questmaster.cli phase1
        ;;
    3)
        echo -e "${GREEN}🎮 Running Phase 2: Story Generation...${NC}"
        python -m questmaster.cli phase2
        ;;
    4)
        echo -e "${GREEN}🌐 Starting Streamlit frontend...${NC}"
        python -m questmaster.cli frontend
        ;;
    5)
        echo -e "${GREEN}🔍 Checking requirements...${NC}"
        python -m questmaster.cli check
        ;;
    *)
        echo -e "${RED}❌ Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Done!${NC}"