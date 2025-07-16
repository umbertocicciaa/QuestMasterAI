# 🗡️ QuestMaster AI

**Agentic AI for Interactive Storytelling**

QuestMaster AI is a sophisticated application that generates interactive story-based quests using advanced AI agents and automated planning. The system combines narrative generation with PDDL (Planning Domain Definition Language) to create dynamic, playable adventures.

## 🌟 Features

- **AI-Powered Story Generation**: Creates engaging narratives with characters, settings, and objectives
- **PDDL Planning Integration**: Uses Fast Downward planner for logical quest progression
- **Interactive Web Interface**: Streamlit-based frontend for immersive gameplay
- **Agentic Architecture**: Specialized AI agents for different aspects of quest creation
- **Docker Support**: Containerized deployment with automated Fast Downward installation
- **CLI Interface**: Command-line tools for development and testing

## 🏗️ Architecture

```
src/questmaster/
├── agents/           # AI agent implementations
├── core/            # Core configuration and settings
├── models/          # Data models and schemas
├── services/        # Business logic services
├── ui/             # User interface components
└── utils/          # Utility functions
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Setup and Run**:

   ```bash
   ./docker-setup.sh
   ```

2. **Or manually with Docker Compose**:

   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Web Interface: <http://localhost:8501>
   - API: <http://localhost:8000>

### Option 2: Local Development

1. **Setup Environment**:

   ```bash
   ./start.sh
   ```

2. **Set OpenAI API Key**:

   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Run the Application**:

   ```bash
   # Complete pipeline
   python -m questmaster.cli run
   
   # Or step by step
   python -m questmaster.cli phase1  # Story generation
   python -m questmaster.cli phase2  # Interactive frontend
   ```

## 🧠 AI Agents

### Story Generator Agent

- Creates immersive narratives with rich lore
- Generates characters, settings, and plot elements
- Integrates seamlessly with PDDL planning

### PDDL Generator Agent

- Converts stories into formal planning domains
- Creates actions, predicates, and goal conditions
- Ensures logical consistency in quest progression

### Reflection Agent

- Validates and refines generated content
- Provides quality assurance for stories and plans
- Suggests improvements and fixes inconsistencies

### Frontend Generator Agent

- Creates dynamic Streamlit interfaces
- Generates interactive game components
- Adapts UI to story requirements

## 🔧 Configuration

Configuration is managed through environment variables and the `src/questmaster/core/config.py` file:

```python
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
OPENAI_MODEL=gpt-4  # Default model
LOG_LEVEL=INFO      # Logging level
DEBUG=false         # Debug mode
```

## 📊 Usage Examples

### CLI Commands

```bash
# Check system requirements
python -m questmaster.cli check

# Generate story and PDDL
python -m questmaster.cli phase1

# Create interactive frontend
python -m questmaster.cli phase2

# Run complete pipeline
python -m questmaster.cli run

# Start generated frontend
python -m questmaster.cli frontend
```

### Python API

```python
from questmaster import QuestMasterApp

app = QuestMasterApp()

# Run complete pipeline
story_result = await app.run_phase1()
frontend_result = await app.run_phase2()

# Or use individual agents
story = await app.story_generator.generate_story()
pddl = await app.pddl_generator.generate_pddl(story)
```

## 🐳 Docker Details

The Docker setup includes:

- **Multi-stage build** for optimized image size
- **Automated Fast Downward installation** from source
- **Python 3.12** with all dependencies
- **Health checks** for reliable deployment
- **Volume mounts** for persistent data

### Docker Commands

```bash
# Build and run
docker-compose up --build

# Run specific services
docker-compose up app      # Main application
docker-compose up frontend # Just the web interface

# Test Docker setup
./test_docker.sh
```

## 🧪 Testing

```bash
# Test imports and basic functionality
python test_import.py

# Test CLI functionality
python -m questmaster.cli check

# Test Docker build
./test_docker.sh
```

## 📁 Project Structure

```
QuestMasterAI/
├── src/questmaster/          # Main package
├── data/                     # Game data and examples
├── resources/               # Templates and examples
├── fast-downward-24.06.1/   # PDDL planner (auto-generated)
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── start.sh               # Local setup script
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper testing
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Fast Downward** planning system
- **OpenAI** for GPT models
- **Streamlit** for web interface framework
- **Pydantic** for data validation
- 🔄 **Intelligent Reflection**: Automatically fixes PDDL validation issues
- 🎮 **Interactive Web Interface**: Beautiful Streamlit frontend for story interaction
- 🐳 **Docker Support**: Easy deployment with containerization
- 📦 **Modern Architecture**: Clean, maintainable codebase with proper separation of concerns
- 🛡️ **Type Safety**: Full type hints and validation with Pydantic
- 📊 **Structured Logging**: Rich logging with structlog
- ⚡ **CLI Interface**: Command-line tools for all operations

---

## 📌 Phase 1: Story Generation

### 🎯 Objective

Help authors generate a PDDL-modeled adventure by guiding them through an interactive narrative design process using LLM agents.

### 📝 Input

- **Lore Document** containing:
  - **Quest Description**: Initial state, goals, obstacles, and world context
  - **Branching Factor**: Min/max number of choices at each state
  - **Depth Constraints**: Min/max steps to goal
  - **Characters, Locations, Items**: Important story elements

### 🔁 Workflow

1. **PDDL Generation**  
   - Converts the Lore into a `domain.pddl` and `problem.pddl` file
   - Every line is annotated with natural language comments
  
2. **Validation with Classical Planner**  
   - Uses **Fast Downward** to ensure a solvable plan exists
   - Provides detailed error reporting

3. **Interactive Refinement Loop (if needed)**  
   - If no valid plan exists:
     - A **Reflection Agent** identifies issues and suggests fixes
     - Automatically attempts to correct PDDL errors
     - Supports multiple validation iterations

### ✅ Output

- Validated `domain.pddl` and `problem.pddl` files
- Finalized Lore document (if updated)
- Generated solution plan

---

## 🎮 Phase 2: Interactive Story Game

### 🎯 Objective

Use the output from Phase 1 to build a web-based interactive adventure game.

### 🛠 Workflow

- Generate an interactive story graph from PDDL and plan
- Create a modern Streamlit web interface
- Incorporate state-based navigation and choice tracking
- Provide game statistics and progress tracking

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **OpenAI API Key**
- **Git**
- **CMake** (for Fast Downward)

### Option 1: Local Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/umbertocicciaa/QuestMasterAI.git questmaster
    cd questmaster
    ```

2. **Install System Dependencies**

   - **macOS:**  

    ```bash
    brew install cmake
    ```

   - **Linux (Debian/Ubuntu):**  

    ```bash
    sudo apt-get install cmake build-essential
    ```

   - **Windows:**  
     [Download and install CMake](https://cmake.org/download/)

3. **Set Up Environment**

    ```bash
    # Copy environment template
    cp .env.template .env
    
    # Edit .env with your OpenAI API key
    nano .env  # or your preferred editor
    ```

4. **Run Setup Script**

    ```bash
    chmod +x start.sh
    ./start.sh
    ```

   The script will:
   - Create a virtual environment
   - Install Python dependencies
   - Download and build Fast Downward (if needed)
   - Check system requirements
   - Offer interactive menu options

### Option 2: Docker Installation

1. **Prerequisites**
   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)

2. **Clone and Setup**

    ```bash
    git clone https://github.com/umbertocicciaa/QuestMasterAI.git questmaster
    cd questmaster
    
    # Copy environment template and edit with your API key
    cp .env.template .env
    nano .env
    ```

3. **Run Docker Setup**

    ```bash
    chmod +x docker-setup.sh
    ./docker-setup.sh
    ```

   The script provides options to:
   - Build and run the full application
   - Run development mode
   - View logs
   - Manage containers

---

## 🎯 Usage

### Command Line Interface

QuestMaster provides a rich CLI for all operations:

```bash
# Check system requirements
python -m questmaster.cli check

# Run full pipeline (Phase 1 + Phase 2)
python -m questmaster.cli run

# Run Phase 1 only (PDDL generation)
python -m questmaster.cli phase1

# Run Phase 2 only (Story generation)
python -m questmaster.cli phase2

# Start the web interface
python -m questmaster.cli frontend

# Get help
python -m questmaster.cli --help
```

### Custom Lore Files

You can provide custom lore files:

```bash
python -m questmaster.cli run --lore-path /path/to/your/lore.json
```

### Development

For development with auto-reload:

```bash
# Install in development mode
pip install -e .

# Run with debug logging
python -m questmaster.cli --debug --log-level DEBUG run
```

---

## 📁 Project Structure

```
questmaster/
├── src/questmaster/           # Main application package
│   ├── agents/               # AI agents (PDDL, reflection, story, frontend)
│   ├── core/                 # Core functionality (config, logging, exceptions)
│   ├── models/               # Data models and schemas
│   ├── services/             # Service layer (LLM, planner, file operations)
│   ├── ui/                   # Streamlit UI components
│   ├── utils/                # Utility functions
│   ├── app.py                # Main application orchestrator
│   └── cli.py                # Command-line interface
├── data/                     # Data files (lore, PDDL, stories)
├── resources/                # Example files and templates
├── fast-downward-24.06.1/    # Fast Downward planner (auto-downloaded)
├── tests/                    # Test suite
├── docker-setup.sh           # Docker setup script
├── start.sh                  # Local setup script
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── pyproject.toml            # Project configuration
└── requirements.txt          # Python dependencies
```

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables

Configure via `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
CHATGPT_MODEL=gpt-4o-mini-2024-07-18
LOG_LEVEL=INFO
DEBUG=False
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0
FAST_DOWNWARD_TIMEOUT=300
```

### Production Deployment

For production, consider:

1. Using a reverse proxy (nginx)
2. Setting up SSL certificates
3. Implementing proper logging aggregation
4. Using Docker secrets for API keys
5. Setting up health monitoring

---

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone and install
git clone https://github.com/umbertocicciaa/QuestMasterAI.git
cd QuestMasterAI
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run type checking
mypy src/

# Format code
black src/
ruff check src/
```

### Architecture

The application follows a clean architecture pattern:

- **Agents**: High-level AI agents that orchestrate specific tasks
- **Services**: Business logic and external service integrations
- **Models**: Data models with validation using Pydantic
- **Core**: Cross-cutting concerns (config, logging, exceptions)
- **UI**: User interface components
- **Utils**: Utility functions

### Adding New Features

1. Create models in `src/questmaster/models/`
2. Implement services in `src/questmaster/services/`
3. Create agents in `src/questmaster/agents/`
4. Add CLI commands in `src/questmaster/cli.py`
5. Write tests in `tests/`

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/questmaster

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

---

## 📊 Monitoring and Logging

QuestMaster uses structured logging with rich console output:

```python
from questmaster.core.logging import get_logger

logger = get_logger(__name__)
logger.info("Processing quest", quest_id="123", user="alice")
```

Logs include:

- Structured JSON format
- Rich console formatting
- Contextual information
- Performance metrics

---

## 🔧 Configuration

Configuration is managed through:

1. **Environment variables** (`.env` file)
2. **Pydantic settings** (`src/questmaster/core/config.py`)
3. **CLI arguments** (override environment)

### Key Settings

- `OPENAI_API_KEY`: Your OpenAI API key
- `CHATGPT_MODEL`: GPT model to use
- `LOG_LEVEL`: Logging verbosity
- `FAST_DOWNWARD_PATH`: Path to Fast Downward installation
- `STREAMLIT_PORT`: Web interface port

---

## 🐛 Troubleshooting

### Common Issues

**1. Fast Downward Build Fails**

```bash
# Install build dependencies
sudo apt-get install build-essential cmake g++  # Linux
brew install cmake  # macOS
```

**2. OpenAI API Errors**

- Check your API key in `.env`
- Verify your OpenAI account has credits
- Check rate limits

**3. PDDL Validation Fails**

- Review the generated PDDL files in `data/`
- Check Fast Downward installation
- Enable debug logging for detailed error info

**4. Memory Issues**

- Increase Docker memory limits
- Use smaller GPT models for development
- Reduce story complexity

### Debug Mode

Enable detailed logging:

```bash
python -m questmaster.cli --debug --log-level DEBUG run
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## � Acknowledgments

- [Fast Downward](https://www.fast-downward.org/) for PDDL planning
- [OpenAI](https://openai.com/) for language models
- [Streamlit](https://streamlit.io/) for the web interface
- [Pydantic](https://pydantic.dev/) for data validation

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/umbertocicciaa/QuestMasterAI/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/umbertocicciaa/QuestMasterAI/discussions)

---

**Happy Quest Building!** 🏰✨

- Generate an HTML-based interface using LLMs
- Incorporate state-based images (optional)
- Render interactive choices and dynamic storytelling

---

## 🚀 Getting Started

### Installation & Setup

1. **Clone the Repository**

    ```bash
     git clone https://github.com/umbertocicciaa/QuestMasterAI.git questmaster
     cd questmaster
    ```

2. **Install CMake**
   - **macOS:**  

    ```bash
     brew install cmake
    ```

   - **Linux (Debian/Ubuntu):**  

    ```bash
     sudo apt-get install cmake
    ```

   - **Windows:**  
     [Download and install CMake](https://cmake.org/download/).

3. **Download & Set Up Fast Downward Planner**
   - [Download Fast Downward](https://www.fast-downward.org/latest/releases/24.06/).
   - Extract it into the project root: `questmaster/fast-downward-24.06.1`.
   - **Build Fast Downward:**

      ```bash
       cd fast-downward-24.06.1
       python build.py
       cd ..
      ```

4. **Set Up Python Virtual Environment (Recommended)**

    ```bash
     python3 -m venv .venv
     # Activate on macOS/Linux
     source .venv/bin/activate
     # Activate on Windows
     .venv\Scripts\activate
    ```

5. **Install Python Dependencies**

    ```bash
     pip install -r requirements.txt
    ```

6. **Start application**

    ```bash
     chmod u+x start.sh
     ./start.sh
    ```
