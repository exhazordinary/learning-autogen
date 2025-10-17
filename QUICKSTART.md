# Quick Start Guide - AutoGen Research Assistant v2.0

Get up and running in 5 minutes! 🚀

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.11+ installed
- ✅ Node.js 20+ installed
- ✅ Redis installed (or Docker)

## Option 1: Docker (Easiest) 🐳

### Step 1: Install Docker
```bash
# macOS
brew install docker docker-compose

# Or download from https://www.docker.com/
```

### Step 2: Configure & Start
```bash
# Clone and configure
git clone <repo-url>
cd learning-autogen
cp .env.example .env

# Start everything
docker-compose up -d

# Check status
docker-compose ps
```

### Step 3: Access
- 🌐 Frontend: http://localhost:3000
- 🔧 API: http://localhost:5001
- 📚 API Docs: http://localhost:5001/api/docs

That's it! Skip to [Using the Application](#using-the-application) below.

---

## Option 2: Local Development 💻

### Step 1: Install Dependencies (3 minutes)

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Redis
# macOS:
brew install redis
brew services start redis

# Ubuntu:
sudo apt-get install redis-server
sudo systemctl start redis

# Windows:
# Download from https://github.com/microsoftarchive/redis/releases

# 3. Install Ollama (for local LLM)
# macOS:
brew install ollama
ollama serve &
ollama pull llama3.2

# Other platforms: https://ollama.ai/download
```

### Step 2: Set Up Project (1 minute)

```bash
# Clone repository
git clone <repo-url>
cd learning-autogen

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local dev)
```

### Step 3: Start Services (1 minute)

Open 4 terminals and run:

**Terminal 1 - Backend:**
```bash
python app.py
```

**Terminal 2 - Celery Worker:**
```bash
celery -A src.autogen_research.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 4 - Redis (if not running as service):**
```bash
redis-server
```

### Step 4: Verify Installation

Check that all services are running:
```bash
# Backend health
curl http://localhost:5001/api/health

# Redis
redis-cli ping

# Frontend
open http://localhost:3000
```

---

## Using the Application

### Web Interface

1. **Open browser** to http://localhost:3000

2. **Enter research question:**
   ```
   Example: "Explain quantum computing in simple terms"
   ```

3. **Click "Start Research"**

4. **Watch progress:**
   - Connection status (top right)
   - Real-time progress bar
   - Agent responses appear as they complete

5. **View results:**
   - Markdown-formatted responses
   - Syntax-highlighted code blocks
   - Copy individual messages
   - Export entire conversation

6. **Access history:**
   - Left sidebar shows recent tasks
   - Click any task to reload it
   - Clear history button at bottom

### API Usage

**Submit a task:**
```bash
curl -X POST http://localhost:5001/api/research \
  -H "Content-Type: application/json" \
  -d '{"task": "Explain machine learning"}'
```

**Response:**
```json
{
  "success": true,
  "task_id": 1,
  "celery_task_id": "abc-123-def",
  "status": "queued"
}
```

**Check status:**
```bash
curl http://localhost:5001/api/research/1/status
```

**Get results:**
```bash
curl http://localhost:5001/api/research/1
```

**Export as markdown:**
```bash
curl http://localhost:5001/api/research/1/export > research.md
```

### Python API

```python
from src.autogen_research.teams import ResearchTeam

# Create team
team = ResearchTeam()

# Run research
results = team.run("Explain quantum computing")

# View results
for msg in results:
    print(f"{msg.source}: {msg.content}\n")

# View metrics
team.print_summary()
```

---

## Configuration Tips

### Use OpenAI Instead of Ollama

Edit `.env`:
```bash
MODEL_TYPE=openai
MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=sk-your-api-key-here
```

### Speed Up Responses

Reduce max rounds in `.env`:
```bash
MAX_ROUNDS=6  # instead of 12
```

### Enable Dark Mode

Click the moon icon (🌙) in the top right of the web interface.

---

## Common Commands

### Docker
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose build
docker-compose up -d
```

### Local Development
```bash
# Run tests
pytest tests/ -v

# Check code quality
ruff check src/

# View logs
tail -f logs/web_app.log

# Clear cache
redis-cli FLUSHDB
```

---

## Troubleshooting

### ❌ Can't connect to backend

**Check backend is running:**
```bash
curl http://localhost:5001/api/health
```

**If not running, check logs:**
```bash
# Docker
docker-compose logs backend

# Local
tail -f logs/web_app.log
```

### ❌ Redis connection error

**Check Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

**Start Redis if needed:**
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Manual
redis-server
```

### ❌ Tasks stuck in "pending"

**Check Celery worker:**
```bash
# Docker
docker-compose logs celery-worker

# Local
celery -A src.autogen_research.tasks.celery_app inspect active
```

**Restart worker if needed:**
```bash
# Docker
docker-compose restart celery-worker

# Local
# Kill existing worker (Ctrl+C) and restart:
celery -A src.autogen_research.tasks.celery_app worker --loglevel=info
```

### ❌ Frontend shows "Disconnected"

**Check WebSocket connection:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by "WS" (WebSocket)
4. Look for socket.io connection

**Fix:**
- Ensure backend is running on port 5001
- Check CORS_ORIGINS in .env includes your frontend URL
- Restart backend

### ❌ Ollama model not found

**Pull the model:**
```bash
ollama pull llama3.2
```

**List available models:**
```bash
ollama list
```

---

## Next Steps

1. ✅ **Read the full documentation:**
   - [README.md](./README.md) - Complete guide
   - [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture

2. ✅ **Explore API documentation:**
   - http://localhost:5001/api/docs

3. ✅ **Try advanced features:**
   - Dark mode toggle
   - Export to markdown
   - Research history
   - Real-time updates

4. ✅ **Run tests:**
   ```bash
   pytest tests/ -v --cov=src/autogen_research
   ```

5. ✅ **Deploy to production:**
   ```bash
   ./start_production.sh
   ```

---

## Getting Help

- 📖 **Documentation:** See README.md and ARCHITECTURE.md
- 🐛 **Issues:** https://github.com/yourusername/learning-autogen/issues
- 💬 **Discussions:** https://github.com/yourusername/learning-autogen/discussions

---

## Quick Reference

### URLs
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
- API Docs: http://localhost:5001/api/docs
- Health Check: http://localhost:5001/api/health

### Ports
- 3000: React frontend
- 5001: Flask backend
- 6379: Redis
- 5432: PostgreSQL (if using)

### Key Files
- `app.py` - Main backend
- `frontend/src/App.jsx` - Main frontend
- `.env` - Configuration
- `docker-compose.yml` - Docker setup

### Environment Variables
```bash
MODEL_TYPE=ollama           # or openai
MODEL_NAME=llama3.2         # or gpt-4
DATABASE_URL=sqlite:///research.db
REDIS_URL=redis://localhost:6379/0
```

---

**You're all set! Enjoy using AutoGen Research Assistant v2.0! 🎉**
