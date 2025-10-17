"""Flask web application for AutoGen Research Team."""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.autogen_research.teams import ResearchTeam
from src.autogen_research.config import Config, ModelConfig, LoggingConfig
from src.autogen_research.utils import setup_logger

app = Flask(__name__)
CORS(app)

# Setup logging
setup_logger("autogen_research", log_file=Path("logs/web_app.log"))

# Global team instance
research_team = None


def get_team():
    """Get or create research team instance."""
    global research_team
    if research_team is None:
        config = Config(
            model=ModelConfig(
                model_type="ollama",
                model_name="llama3.2",
                temperature=0.7,
            ),
            logging=LoggingConfig(
                level="INFO",
                enable_file_logging=True,
                enable_metrics=True,
            ),
        )
        research_team = ResearchTeam(config=config)
    return research_team


@app.route('/api/research', methods=['POST'])
def research():
    """
    Execute a research task.

    Request body:
    {
        "task": "Your research question here"
    }
    """
    try:
        data = request.get_json()
        task = data.get('task')

        if not task:
            return jsonify({'error': 'Task is required'}), 400

        # Get team instance
        team = get_team()

        # Execute research (this will be synchronous)
        messages = team.run(task, verbose=False)

        # Format response
        formatted_messages = []
        for msg in messages:
            if hasattr(msg, 'source') and hasattr(msg, 'content'):
                formatted_messages.append({
                    'agent': msg.source,
                    'content': msg.content
                })

        # Get metrics
        summary = team.get_summary()

        return jsonify({
            'success': True,
            'messages': formatted_messages,
            'metrics': summary
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'autogen-research-api'
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    team = get_team()
    return jsonify(team.config.to_dict())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
