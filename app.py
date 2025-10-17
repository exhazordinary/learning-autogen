"""Enhanced Flask web application for AutoGen Research Team."""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_swagger_ui import get_swaggerui_blueprint
from pathlib import Path
from datetime import datetime
import sys
import os
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.autogen_research.teams import ResearchTeam
from src.autogen_research.config import Config, ModelConfig, LoggingConfig
from src.autogen_research.utils import setup_logger
from src.autogen_research.database import db, ResearchTask, AgentMessage, TaskMetrics, cache_manager
from src.autogen_research.tasks import celery_app, process_research_task

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///research.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Initialize extensions
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv('REDIS_URL', 'redis://localhost:6379/2')
)

# Initialize database
db.init_app(app)

# Setup logging
logger = setup_logger("autogen_research", log_file=Path("logs/web_app.log"))

# Create tables
with app.app_context():
    db.create_all()

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "AutoGen Research API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/static/swagger.json')
def swagger_spec():
    """Serve Swagger specification."""
    return send_from_directory('static', 'swagger.json')


@app.errorhandler(400)
def bad_request(e):
    """Handle bad request errors."""
    return jsonify({'error': 'Bad request', 'message': str(e)}), 400


@app.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit errors."""
    return jsonify({'error': 'Rate limit exceeded', 'message': str(e)}), 429


@app.errorhandler(500)
def internal_error(e):
    """Handle internal errors."""
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/research', methods=['POST'])
@limiter.limit("10 per minute")
def research():
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
            return jsonify({'error': 'Request body is required'}), 400

        task_text = data.get('task', '').strip()
        use_cache = data.get('use_cache', True)

        if not task_text:
            return jsonify({'error': 'Task is required'}), 400

        if len(task_text) > 5000:
            return jsonify({'error': 'Task text too long (max 5000 characters)'}), 400

        # Check cache first
        if use_cache:
            cached_result = cache_manager.get(task_text)
            if cached_result:
                logger.info(f"Cache hit for task: {task_text[:50]}...")
                return jsonify({
                    'success': True,
                    'from_cache': True,
                    'task_id': cached_result.get('task_id'),
                    'messages': cached_result.get('messages', []),
                    'metrics': cached_result.get('metrics', {})
                })

        # Create database task
        research_task = ResearchTask(task=task_text, status='pending')
        db.session.add(research_task)
        db.session.commit()

        # Queue async task
        celery_task = process_research_task.apply_async(
            args=[research_task.id, task_text],
            task_id=f'research_{research_task.id}'
        )

        logger.info(f"Queued research task {research_task.id}: {task_text[:50]}...")

        return jsonify({
            'success': True,
            'task_id': research_task.id,
            'celery_task_id': celery_task.id,
            'status': 'queued',
            'message': 'Research task queued successfully'
        }), 202

    except Exception as e:
        logger.error(f"Error queuing research task: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/research/<int:task_id>', methods=['GET'])
def get_research_task(task_id: int):
    """Get research task by ID."""
    try:
        task = db.session.get(ResearchTask, task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        return jsonify({
            'success': True,
            'task': task.to_dict()
        })

    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/research/<int:task_id>/status', methods=['GET'])
def get_task_status(task_id: int):
    """Get task status and progress."""
    try:
        task = db.session.get(ResearchTask, task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # Get Celery task status
        celery_task = celery_app.AsyncResult(f'research_{task_id}')

        response = {
            'success': True,
            'task_id': task_id,
            'status': task.status,
            'celery_status': celery_task.state,
        }

        if celery_task.state == 'PROCESSING':
            response['meta'] = celery_task.info

        if task.status == 'completed':
            response['result'] = task.to_dict()

        if task.status == 'failed':
            response['error'] = task.error

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error fetching task status {task_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/research', methods=['GET'])
@limiter.limit("30 per minute")
def list_research_tasks():
    """List all research tasks with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')

        query = ResearchTask.query.order_by(ResearchTask.created_at.desc())

        if status:
            query = query.filter_by(status=status)

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        })

    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/research/<int:task_id>/export', methods=['GET'])
def export_research(task_id: int):
    """Export research task as markdown."""
    try:
        task = db.session.get(ResearchTask, task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        # Generate markdown
        markdown = f"# Research Task\n\n"
        markdown += f"**Task:** {task.task}\n\n"
        markdown += f"**Status:** {task.status}\n\n"
        markdown += f"**Created:** {task.created_at}\n\n"

        if task.completed_at:
            markdown += f"**Completed:** {task.completed_at}\n\n"

        if task.metrics:
            markdown += f"**Duration:** {task.metrics.duration:.2f}s\n\n"

        markdown += f"## Agent Messages\n\n"

        for msg in task.messages.order_by(AgentMessage.order):
            markdown += f"### {msg.agent}\n\n"
            markdown += f"{msg.content}\n\n"

        return jsonify({
            'success': True,
            'markdown': markdown
        })

    except Exception as e:
        logger.error(f"Error exporting task {task_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        # Check database
        db.session.execute(db.text('SELECT 1'))

        # Check Redis
        cache_manager.redis_client.ping()

        return jsonify({
            'status': 'healthy',
            'service': 'autogen-research-api',
            'database': 'connected',
            'redis': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration (sanitized)."""
    return jsonify({
        'model_type': os.getenv('MODEL_TYPE', 'ollama'),
        'model_name': os.getenv('MODEL_NAME', 'llama3.2'),
        'temperature': float(os.getenv('TEMPERATURE', '0.7')),
        'max_rounds': int(os.getenv('MAX_ROUNDS', '12'))
    })


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to research server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('subscribe_task')
def handle_subscribe_task(data):
    """Subscribe to task updates."""
    task_id = data.get('task_id')
    if task_id:
        logger.info(f"Client {request.sid} subscribed to task {task_id}")
        emit('subscribed', {'task_id': task_id})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
