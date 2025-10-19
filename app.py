"""Enhanced Flask web application for AutoGen Research Team."""

import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO, emit
from flask_swagger_ui import get_swaggerui_blueprint

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.autogen_research.auth import (
    create_access_token,
    create_user,
    init_jwt,
    jwt_required_optional,
    verify_user,
)
from src.autogen_research.database import AgentMessage, ResearchTask, cache_manager, db
from src.autogen_research.tasks import celery_app, process_research_task
from src.autogen_research.utils import setup_logger
from src.autogen_research.utils.observability import (
    instrument_flask_app,
    setup_opentelemetry,
    setup_sentry,
)

# Initialize Flask app
app = Flask(__name__)

# Setup logging early
logger = setup_logger("autogen_research", log_file=Path("logs/web_app.log"))

# Setup observability
logger.info("Initializing observability...")
sentry_enabled = setup_sentry(environment=os.getenv("FLASK_ENV", "production"))
otel_enabled = setup_opentelemetry()

if otel_enabled:
    instrument_flask_app(app)

logger.info(f"Sentry: {'enabled' if sentry_enabled else 'disabled'}")
logger.info(f"OpenTelemetry: {'enabled' if otel_enabled else 'disabled'}")

# Configuration
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    import secrets

    secret_key = secrets.token_hex(32)
    if not os.getenv("FLASK_ENV") == "development":
        logger.warning("SECRET_KEY not set! Using random key. Set SECRET_KEY in production!")

app.config["SECRET_KEY"] = secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///research.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
    "pool_pre_ping": True,
}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000  # 1 year cache for static files
app.config["SOCKETIO_TIMEOUT"] = int(os.getenv("SOCKETIO_TIMEOUT", "300"))  # 5 min default
app.config["REQUEST_TIMEOUT"] = int(os.getenv("REQUEST_TIMEOUT", "120"))  # 2 min default

# Initialize extensions
CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Initialize rate limiter with fallback
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/2")
try:
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["10000 per day", "1000 per hour"],
        storage_uri=redis_url,
    )
except Exception as e:
    logger.warning(f"Redis not available for rate limiting: {e}. Using memory storage.")
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["10000 per day", "1000 per hour"],
        storage_uri="memory://",
    )

# Initialize database
db.init_app(app)

# Initialize JWT
jwt = init_jwt(app)

# Create tables
with app.app_context():
    db.create_all()

    # Create a default user for testing (remove in production!)
    if os.getenv("CREATE_DEFAULT_USER", "false").lower() == "true":
        username = os.getenv("DEFAULT_USER", "admin")
        password = os.getenv("DEFAULT_PASSWORD", "changeme")
        if create_user(username, password):
            logger.info(f"Created default user: {username}")
        else:
            logger.info(f"Default user already exists: {username}")

# Swagger UI configuration
SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "AutoGen Research API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/static/swagger.json")
def swagger_spec():
    """Serve Swagger specification."""
    return send_from_directory("static", "swagger.json")


# Authentication endpoints
@app.route("/api/v1/auth/register", methods=["POST"])
def register():
    """
    Register a new user.

    Request body:
    {
        "username": "user",
        "password": "password"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400

        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400

        if create_user(username, password):
            access_token = create_access_token(username)
            return jsonify(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "access_token": access_token,
                    "username": username,
                }
            ), 201
        else:
            return jsonify({"error": "User already exists"}), 409

    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """
    Login and get access token.

    Request body:
    {
        "username": "user",
        "password": "password"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        username = data.get("username", "").strip()
        password = data.get("password", "")

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        if verify_user(username, password):
            access_token = create_access_token(username)
            return jsonify(
                {
                    "success": True,
                    "access_token": access_token,
                    "username": username,
                }
            )
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(400)
def bad_request(e):
    """Handle bad request errors."""
    return jsonify({"error": "Bad request", "message": str(e)}), 400


@app.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit errors."""
    return jsonify({"error": "Rate limit exceeded", "message": str(e)}), 429


@app.errorhandler(500)
def internal_error(e):
    """Handle internal errors."""
    logger.error(f"Internal error: {e}")
    return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/research", methods=["POST"])
@limiter.limit("100 per minute")
@jwt_required_optional
def research_v1():
    """
    Execute a research task asynchronously.

    Request body:
    {
        "task": "Your research question here",
        "use_cache": true  // optional, default true
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        task_text = data.get("task", "").strip()
        use_cache = data.get("use_cache", True)

        if not task_text:
            return jsonify({"error": "Task is required"}), 400

        if len(task_text) > 5000:
            return jsonify({"error": "Task text too long (max 5000 characters)"}), 400

        # Check cache first
        if use_cache:
            cached_result = cache_manager.get(task_text)
            if cached_result:
                logger.info(f"Cache hit for task: {task_text[:50]}...")
                return jsonify(
                    {
                        "success": True,
                        "from_cache": True,
                        "task_id": cached_result.get("task_id"),
                        "messages": cached_result.get("messages", []),
                        "metrics": cached_result.get("metrics", {}),
                    }
                )

        # Create database task with optional user_id
        user_id = getattr(request, "user_id", None)
        research_task = ResearchTask(task=task_text, status="pending", user_id=user_id)
        db.session.add(research_task)
        db.session.commit()

        # Queue async task
        celery_task = process_research_task.apply_async(
            args=[research_task.id, task_text], task_id=f"research_{research_task.id}"
        )

        logger.info(f"Queued research task {research_task.id}: {task_text[:50]}...")

        return jsonify(
            {
                "success": True,
                "task_id": research_task.id,
                "celery_task_id": celery_task.id,
                "status": "queued",
                "message": "Research task queued successfully",
            }
        ), 202

    except Exception as e:
        logger.error(f"Error queuing research task: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/research/<int:task_id>", methods=["GET"])
def get_research_task_v1(task_id: int):
    """Get research task by ID."""
    try:
        task = db.session.get(ResearchTask, task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"success": True, "task": task.to_dict()})

    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/research/<int:task_id>/status", methods=["GET"])
def get_task_status_v1(task_id: int):
    """Get task status and progress."""
    try:
        task = db.session.get(ResearchTask, task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Get Celery task status
        celery_task = celery_app.AsyncResult(f"research_{task_id}")

        response = {
            "success": True,
            "task_id": task_id,
            "status": task.status,
            "celery_status": celery_task.state,
        }

        if celery_task.state == "PROCESSING":
            response["meta"] = celery_task.info

        if task.status == "completed":
            response["result"] = task.to_dict()

        if task.status == "failed":
            response["error"] = task.error

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error fetching task status {task_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/research", methods=["GET"])
@limiter.limit("500 per minute")
def list_research_tasks_v1():
    """List all research tasks with pagination."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        status = request.args.get("status")

        query = ResearchTask.query.order_by(ResearchTask.created_at.desc())

        if status:
            query = query.filter_by(status=status)

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify(
            {
                "success": True,
                "tasks": [task.to_dict() for task in paginated.items],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": paginated.total,
                    "pages": paginated.pages,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/v1/research/<int:task_id>/export", methods=["GET"])
def export_research_v1(task_id: int):
    """Export research task as markdown."""
    try:
        task = db.session.get(ResearchTask, task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Generate markdown
        markdown = "# Research Task\n\n"
        markdown += f"**Task:** {task.task}\n\n"
        markdown += f"**Status:** {task.status}\n\n"
        markdown += f"**Created:** {task.created_at}\n\n"

        if task.completed_at:
            markdown += f"**Completed:** {task.completed_at}\n\n"

        if task.metrics:
            markdown += f"**Duration:** {task.metrics.duration:.2f}s\n\n"

        markdown += "## Agent Messages\n\n"

        for msg in task.messages.order_by(AgentMessage.order):
            markdown += f"### {msg.agent}\n\n"
            markdown += f"{msg.content}\n\n"

        return jsonify({"success": True, "markdown": markdown})

    except Exception as e:
        logger.error(f"Error exporting task {task_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Backward compatibility - redirect old endpoints to v1
@app.route("/api/research", methods=["POST", "GET"])
def research_legacy():
    """Legacy endpoint - redirects to v1."""
    return jsonify(
        {
            "error": "This endpoint is deprecated. Please use /api/v1/research",
            "new_endpoint": "/api/v1/research",
        }
    ), 301


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        # Check database
        db.session.execute(db.text("SELECT 1"))

        # Check Redis
        cache_manager.redis_client.ping()

        return jsonify(
            {
                "status": "healthy",
                "service": "autogen-research-api",
                "database": "connected",
                "redis": "connected",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current configuration (sanitized)."""
    return jsonify(
        {
            "model_type": os.getenv("MODEL_TYPE", "ollama"),
            "model_name": os.getenv("MODEL_NAME", "llama3.2"),
            "temperature": float(os.getenv("TEMPERATURE", "0.7")),
            "max_rounds": int(os.getenv("MAX_ROUNDS", "12")),
        }
    )


# WebSocket events
@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    emit("connected", {"message": "Connected to research server"})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on("subscribe_task")
def handle_subscribe_task(data):
    """Subscribe to task updates."""
    from flask_socketio import join_room

    task_id = data.get("task_id")
    if task_id:
        room = f"task_{task_id}"
        join_room(room)
        logger.info(f"Client {request.sid} subscribed to task {task_id}")
        emit("subscribed", {"task_id": task_id, "room": room})


if __name__ == "__main__":
    import atexit
    import signal

    def cleanup():
        """Cleanup function for graceful shutdown."""
        logger.info("Shutting down gracefully...")
        try:
            # Close database connections
            db.session.remove()
            db.engine.dispose()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGTERM, lambda sig, frame: cleanup())
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
