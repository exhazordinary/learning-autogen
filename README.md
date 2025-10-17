# AutoGen Research Assistant

> A production-grade, scalable multi-agent AI research system built with AutoGen, featuring real-time updates, persistent storage, and modern web technologies.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/react-19-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

## ✨ Features

### Multi-Agent System
- 🤖 **4 Specialized Agents**: Researcher, Analyst, Writer, Critic
- 🔄 **Coordinated Workflow**: Sequential communication with quality checks
- 🎯 **Intelligent Termination**: Critic determines task completion

### Web Interface
- 🌐 **Modern React UI**: Built with Vite for fast development
- 🌓 **Dark/Light Theme**: Persistent theme preference
- 📝 **Markdown Support**: Rich text rendering with syntax highlighting
- 📊 **Real-time Progress**: WebSocket updates during processing
- 📂 **Research History**: Automatic saving with quick access
- 💾 **Export Functionality**: Download results as Markdown

### Backend API
- ⚡ **High Performance**: Async task processing with Celery
- 🔒 **Secure**: Rate limiting, CORS, input validation
- 📚 **Well Documented**: Interactive Swagger UI
- 💾 **Persistent**: PostgreSQL/SQLite database
- 🚀 **Scalable**: Horizontal and vertical scaling support

### DevOps
- 🐳 **Docker Ready**: Complete containerization
- 🔄 **CI/CD**: Automated testing and deployment
- 📊 **Monitoring**: Health checks and logging
- 🔧 **Configurable**: Environment-based configuration

## Project Structure

```
learning-autogen/
├── src/autogen_research/
│   ├── agents/          # Agent implementations
│   ├── models/          # Model factory
│   ├── teams/           # Team orchestration
│   ├── database/        # Database models & cache
│   ├── tasks/           # Celery async tasks
│   └── utils/           # Logging, metrics
├── frontend/            # React application
│   └── src/
│       ├── App.jsx      # Main component
│       ├── App.css      # Styles
│       └── store.js     # State management
├── tests/               # Test suite
├── static/              # API documentation
├── app.py              # Flask API server
├── docker-compose.yml  # Docker configuration
└── start_production.sh # Production deployment
```

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ and npm (for React frontend)
- [ngrok](https://ngrok.com/) (for public access)
- Ollama (if using local models)

### Setup

1. Clone the repository:
```bash
git clone <this repo url>
cd learning-autogen
```

2. Install Python dependencies:
```bash
uv sync
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Install ngrok:
```bash
brew install ngrok
# or download from https://ngrok.com/
```

5. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

6. If using Ollama, start it and pull the model:
```bash
ollama serve
ollama pull llama3.2
```

## Quick Start

### Web Interface (Recommended)

Start the full stack application with one command:

```bash
./start.sh
```

This starts:
- Flask API backend on port 5001
- React frontend on port 3000
- ngrok tunnel for public access

Then open **http://localhost:3000** in your browser.

**Manual Start:**

```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: ngrok (optional)
ngrok http 5001
```

### Python API Usage

```python
from src.autogen_research.teams import ResearchTeam
from src.autogen_research.config import Config

# Create team with default configuration
team = ResearchTeam()

# Run a research task
results = team.run("Explain quantum computing in simple terms")

# View performance metrics
team.print_summary()
```

### Running Examples

**Basic Research:**
```bash
uv run examples/basic_research.py
```

**Advanced Pipeline:**
```bash
uv run examples/advanced_research.py
```

**Original Demo:**
```bash
uv run autogen_demo.py
```

## Configuration

### Environment Variables

```bash
# Model Settings
MODEL_TYPE=ollama           # ollama or openai
MODEL_NAME=llama3.2        # Model to use
TEMPERATURE=0.7            # Sampling temperature

# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434/v1

# OpenAI Settings (if using OpenAI)
OPENAI_API_KEY=your-key

# Logging
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
ENABLE_FILE_LOGGING=true
ENABLE_METRICS=true

# Team Configuration
MAX_ROUNDS=12              # Max conversation rounds
```

### Programmatic Configuration

```python
from src.autogen_research.config import Config, ModelConfig

config = Config(
    model=ModelConfig(
        model_type="ollama",
        model_name="llama3.2",
        temperature=0.7,
    )
)

team = ResearchTeam(config=config)
```

## Architecture

### Agent Roles

1. **Research Agent**: Gathers information, identifies key concepts, and provides well-sourced data
2. **Analysis Agent**: Analyzes patterns, trends, and provides statistical interpretations
3. **Writer Agent**: Synthesizes findings into clear, structured documentation
4. **Critic Agent**: Reviews work, identifies gaps, and ensures quality standards

### Communication Flow

```
Task → Researcher → Analyst → Writer → Critic → [Repeat until complete or max rounds]
```

The critic agent terminates the conversation by saying "TERMINATE" when quality standards are met.

## Advanced Usage

### Custom Agents

```python
from src.autogen_research.agents import BaseAgent
from src.autogen_research.models import ModelFactory

model_client = ModelFactory.create_ollama_client()

custom_agent = BaseAgent(
    name="CustomAgent",
    description="Specialized agent",
    system_message="You are an expert in...",
    model_client=model_client,
)
```

### Metrics and Monitoring

```python
team = ResearchTeam()
results = team.run("Research task")

# Get metrics summary
summary = team.get_summary()
print(summary)

# Export to file
team.export_metrics("metrics.json")
```

## Development

### Project Dependencies

```bash
# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Sync dependencies
uv sync
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Type checking
uv run mypy src/

# Linting
uv run ruff check src/

# Formatting
uv run ruff format src/
```

## Examples

### Research Task Example

```python
team = ResearchTeam()

task = """
Analyze the impact of transformer models on NLP.

Include:
1. Historical context
2. Key innovations
3. Current applications
4. Future directions
"""

results = team.run(task, verbose=True)
```

### Multi-Task Pipeline

```python
team = ResearchTeam()

tasks = [
    "Explain neural networks",
    "Compare CNNs vs Transformers",
    "Summarize recent advances in LLMs"
]

for task in tasks:
    results = team.run(task)
    print(f"Completed: {task}")

team.print_summary()
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Model Not Found

```bash
# Pull the model
ollama pull llama3.2

# List available models
ollama list
```

### Import Errors

```bash
# Ensure dependencies are installed
uv sync

# Check Python path
uv run python -c "import sys; print(sys.path)"
```

## REST API

### Endpoints

**POST /api/research**
Execute a research task with the agent team.

Request:
```json
{
  "task": "Your research question here"
}
```

Response:
```json
{
  "success": true,
  "messages": [
    {"agent": "Researcher", "content": "..."},
    {"agent": "Analyst", "content": "..."}
  ],
  "metrics": {
    "total_tasks": 1,
    "successful_tasks": 1,
    "average_duration": 15.3
  }
}
```

**GET /api/health**
Health check endpoint.

**GET /api/config**
Get current configuration.

## Performance Tips

### Speed Optimization

The multi-agent system can take **30-120 seconds** depending on complexity. To make it faster:

1. **Reduce max rounds** (in `app.py` or via environment):
   ```python
   team: TeamConfig(max_rounds=6)  # Default is 12
   ```

2. **Use smaller/faster models**:
   ```bash
   MODEL_NAME=llama3.2:1b  # Smaller, faster variant
   ```

3. **Switch to OpenAI** (faster but costs money):
   ```bash
   MODEL_TYPE=openai
   MODEL_NAME=gpt-4o-mini  # Fast and affordable
   OPENAI_API_KEY=your-key
   ```

4. **Use appropriate temperature**: Lower (0.1-0.3) for factual tasks, higher (0.7-0.9) for creative tasks

5. **Write specific tasks**: Shorter, focused questions finish faster

### Typical Response Times

- **Ollama (local llama3.2)**: 30-120 seconds
- **Ollama (llama3.2:1b)**: 15-60 seconds
- **OpenAI GPT-4**: 10-30 seconds
- **OpenAI GPT-4o-mini**: 5-15 seconds

### Resource Usage

- **CPU**: High during local model inference
- **RAM**: 8GB+ recommended for llama3.2
- **GPU**: Optional but significantly speeds up Ollama

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Acknowledgments

Built with:
- [AutoGen](https://github.com/microsoft/autogen) - Multi-agent framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
