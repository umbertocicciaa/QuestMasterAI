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

## 🔧 Configuration

Configuration is managed through environment variables and the `src/questmaster/core/config.py` file:

You must configure environment variable with this template [Env template](.env.template)

```python
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
OPENAI_MODEL=gpt-4  # Default model
LOG_LEVEL=INFO      # Logging level
DEBUG=false         # Debug mode
```

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
   - Web Interface: <http://localhost:8501> (if frontend is generated and started)
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

## 🧠 AI Agents description

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

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/umbertocicciaa/QuestMasterAI/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/umbertocicciaa/QuestMasterAI/discussions)

---

**Happy Quest Building!** 🏰✨

- Generate an HTML-based interface using LLMs
- Incorporate state-based images (optional)
- Render interactive choices and dynamic storytelling

---
