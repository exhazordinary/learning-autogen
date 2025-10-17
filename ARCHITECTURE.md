# AutoGen Research Assistant - Architecture

## System Overview

The AutoGen Research Assistant is a production-grade, scalable multi-agent AI research system built with modern web technologies and best practices.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Frontend Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React Application (Vite)                                 │  │
│  │  - Dark/Light Theme                                       │  │
│  │  - Markdown Rendering                                     │  │
│  │  - Real-time Updates (Socket.IO)                          │  │
│  │  - Research History                                       │  │
│  │  - Export Functionality                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                       Nginx Reverse Proxy                        │
│  - Load Balancing                                                │
│  - SSL Termination                                               │
│  - Rate Limiting                                                 │
│  - Static Asset Serving                                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                       Backend Layer (Flask)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Flask API Server (Gunicorn + Eventlet)                  │  │
│  │  - RESTful API Endpoints                                 │  │
│  │  - WebSocket Support (Flask-SocketIO)                    │  │
│  │  - Rate Limiting (Flask-Limiter)                         │  │
│  │  - Authentication & Security                             │  │
│  │  - API Documentation (Swagger/OpenAPI)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────┬─────────────────────────┬────────────────────┬─────────┘
         │                         │                    │
         │                         │                    │
    ┌────▼─────┐            ┌─────▼─────┐      ┌──────▼──────┐
    │ Database │            │   Redis   │      │   Celery    │
    │PostgreSQL│            │  - Cache  │      │   Workers   │
    │ /SQLite  │            │  - Broker │      │             │
    └────┬─────┘            └─────┬─────┘      └──────┬──────┘
         │                        │                    │
         │                        │                    │
┌────────▼────────────────────────▼────────────────────▼─────────┐
│                    Persistence & Queue Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Task Queue  │  │  Cache Layer │  │  Database Models     │ │
│  │  (Celery)    │  │  (Redis)     │  │  - ResearchTask      │ │
│  │              │  │              │  │  - AgentMessage      │ │
│  │  - Async     │  │  - Results   │  │  - TaskMetrics       │ │
│  │  - Parallel  │  │  - Sessions  │  │                      │ │
│  │  - Retries   │  │  - Temp Data │  │                      │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  AutoGen Multi-Agent System                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Research Team                                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ Researcher  │→ │  Analyst    │→ │   Writer    │→     │  │
│  │  │   Agent     │  │   Agent     │  │   Agent     │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  │         ↓                                    ↓           │  │
│  │  ┌─────────────────────────────────────────────┐        │  │
│  │  │            Critic Agent                     │        │  │
│  │  │         (Quality Assurance)                 │        │  │
│  │  └─────────────────────────────────────────────┘        │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                       LLM Provider Layer                         │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │  Ollama (Local)  │              │  OpenAI (Cloud)  │         │
│  │  - llama3.2      │              │  - GPT-4         │         │
│  │  - Open Source   │              │  - GPT-4o-mini   │         │
│  │  - Privacy       │              │  - Fast & Smart  │         │
│  └──────────────────┘              └──────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React + Vite)

**Technology Stack:**
- React 19 with Hooks
- Vite for fast development
- Zustand for state management
- Socket.IO client for real-time updates
- React Markdown for rendering
- React Syntax Highlighter for code blocks

**Features:**
- Dark/Light theme toggle
- Real-time task progress updates
- Research history with localStorage persistence
- Markdown export functionality
- Copy to clipboard
- Responsive design

**File Structure:**
```
frontend/
├── src/
│   ├── App.jsx           # Main application component
│   ├── App.css           # Styles with theme support
│   ├── store.js          # Zustand state management
│   └── main.jsx          # Entry point
├── package.json
└── vite.config.js
```

### 2. Backend (Flask + Gunicorn)

**Technology Stack:**
- Flask 3.0+ for REST API
- Flask-SocketIO for WebSocket support
- Flask-SQLAlchemy for ORM
- Flask-Limiter for rate limiting
- Flask-CORS for cross-origin requests
- Gunicorn + Eventlet for production serving

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/research` | Submit new research task |
| GET | `/api/research` | List all tasks (paginated) |
| GET | `/api/research/{id}` | Get task details |
| GET | `/api/research/{id}/status` | Get task status |
| GET | `/api/research/{id}/export` | Export as markdown |
| GET | `/api/health` | Health check |
| GET | `/api/config` | Get configuration |
| GET | `/api/docs` | Swagger documentation |

**Security Features:**
- Rate limiting (configurable per endpoint)
- CORS configuration
- Input validation and sanitization
- Error handling with proper HTTP codes
- Secret key management

### 3. Database Layer

**PostgreSQL (Production) / SQLite (Development)**

**Models:**
- `ResearchTask`: Main task entity
- `AgentMessage`: Individual agent responses
- `TaskMetrics`: Performance metrics

**Relationships:**
- ResearchTask 1:N AgentMessage
- ResearchTask 1:1 TaskMetrics
- Cascade delete for cleanup

### 4. Cache Layer (Redis)

**Purpose:**
- Cache research results (1 hour TTL)
- Store session data
- Rate limiting counters
- Celery task queue broker

**Redis Databases:**
- DB 0: Application cache
- DB 1: Celery broker
- DB 2: Rate limiting

### 5. Task Queue (Celery)

**Configuration:**
- Workers: Configurable (default 2)
- Max task time: 10 minutes
- Retry policy: 3 attempts
- Concurrency: Async with eventlet

**Task Flow:**
1. User submits research task
2. Task queued in Celery
3. Worker picks up task
4. Runs AutoGen team
5. Stores results in database
6. Sends WebSocket notification

### 6. AutoGen Multi-Agent System

**Agents:**

1. **Researcher Agent**
   - Gathers information
   - Identifies key concepts
   - Provides sources

2. **Analyst Agent**
   - Analyzes patterns
   - Statistical interpretation
   - Identifies trends

3. **Writer Agent**
   - Synthesizes findings
   - Creates documentation
   - Structures content

4. **Critic Agent**
   - Quality assurance
   - Identifies gaps
   - Determines completion

**Communication Pattern:**
- Sequential with round-robin
- Max rounds: 12 (configurable)
- Termination on "TERMINATE" from critic

## Data Flow

### Research Task Submission

```
1. User submits task via frontend
   ↓
2. Frontend sends POST to /api/research
   ↓
3. Backend validates and creates ResearchTask
   ↓
4. Task queued in Celery
   ↓
5. Backend returns task_id (HTTP 202)
   ↓
6. Frontend subscribes to WebSocket updates
   ↓
7. Frontend polls /api/research/{id}/status
   ↓
8. Celery worker processes task
   ↓
9. AutoGen agents collaborate
   ↓
10. Results stored in database
    ↓
11. WebSocket notification sent
    ↓
12. Frontend displays results
```

### Caching Flow

```
1. Request received
   ↓
2. Generate cache key (SHA256 of task)
   ↓
3. Check Redis cache
   ↓
4. If HIT: Return cached result
   ↓
5. If MISS: Process task normally
   ↓
6. Store result in cache (1 hour TTL)
   ↓
7. Return result
```

## Deployment Architectures

### Development

```
Local Machine:
├── Python virtual environment (.venv)
├── Ollama (localhost:11434)
├── Redis (localhost:6379)
├── SQLite database
├── Flask dev server (localhost:5001)
└── Vite dev server (localhost:3000)
```

### Production (Docker)

```
Docker Network:
├── nginx (reverse proxy)
├── frontend (React container)
├── backend (Flask + Gunicorn)
├── celery-worker (background tasks)
├── postgres (database)
└── redis (cache + broker)
```

### Production (Cloud)

```
AWS/GCP/Azure:
├── Load Balancer (ALB/GLB)
├── ECS/Kubernetes Cluster
│   ├── Frontend pods
│   ├── Backend pods
│   └── Celery worker pods
├── RDS/Cloud SQL (PostgreSQL)
├── ElastiCache/MemoryStore (Redis)
└── S3/GCS (static assets)
```

## Scaling Strategies

### Horizontal Scaling

1. **Frontend**: Multiple replicas behind load balancer
2. **Backend**: Multiple Flask instances
3. **Celery**: Add more worker pods
4. **Database**: Read replicas for queries

### Vertical Scaling

1. Increase CPU/RAM for workers
2. Optimize model inference
3. Use GPU for Ollama
4. Increase database resources

### Performance Optimization

1. **Caching**: Redis for frequently requested results
2. **CDN**: CloudFlare for static assets
3. **Database**: Indexes on task_id, status, created_at
4. **API**: Response compression (gzip)
5. **Frontend**: Code splitting, lazy loading

## Monitoring & Observability

### Metrics

- Task completion rate
- Average response time
- Error rate by endpoint
- Queue length
- Cache hit ratio

### Logging

- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized logging (ELK/Datadog)

### Health Checks

- `/api/health`: Database, Redis, Celery status
- Docker healthchecks for all services
- Kubernetes liveness/readiness probes

## Security Considerations

1. **Authentication**: Add JWT/OAuth (future)
2. **Rate Limiting**: 10 requests/minute per IP
3. **Input Validation**: Max 5000 chars per task
4. **CORS**: Whitelist allowed origins
5. **Secrets**: Environment variables, not hardcoded
6. **SSL/TLS**: HTTPS in production
7. **SQL Injection**: Parameterized queries (SQLAlchemy)
8. **XSS**: Content sanitization

## Future Enhancements

1. User authentication and authorization
2. Multi-tenancy support
3. Custom agent configuration
4. Streaming responses
5. Advanced analytics dashboard
6. Email notifications
7. Webhook integration
8. API versioning
9. GraphQL API
10. Mobile app (React Native)
