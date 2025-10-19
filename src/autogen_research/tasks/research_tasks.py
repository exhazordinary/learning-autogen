"""Celery tasks for research operations."""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.autogen_research.config import Config, LoggingConfig, ModelConfig
from src.autogen_research.tasks.celery_app import celery_app
from src.autogen_research.teams import ResearchTeam


def emit_progress(task_id: int, status: str, progress: int) -> None:
    """Emit progress update via WebSocket."""
    try:
        from app import socketio

        socketio.emit(
            "task_progress",
            {"task_id": task_id, "status": status, "progress": progress},
            namespace="/",
            room=f"task_{task_id}",
        )
    except Exception:
        # Silently fail if socketio not available
        pass


@celery_app.task(bind=True, name="research.process_task")
def process_research_task(self, task_id: int, task_text: str, config_dict: dict = None):
    """
    Process a research task asynchronously.

    Args:
        self: Celery task instance
        task_id: Database task ID
        task_text: Research task description
        config_dict: Optional configuration dictionary

    Returns:
        Dictionary with results and metrics
    """
    from app import app
    from src.autogen_research.database import AgentMessage, ResearchTask, TaskMetrics, db

    with app.app_context():
        # Get task from database
        research_task = db.session.get(ResearchTask, task_id)
        if not research_task:
            return {"error": "Task not found"}

        try:
            # Update status to processing
            research_task.status = "processing"
            db.session.commit()

            # Update task progress
            self.update_state(
                state="PROCESSING", meta={"status": "Starting research agents...", "progress": 10}
            )
            emit_progress(task_id, "Starting research agents...", 10)

            # Create research team
            if config_dict:
                config = Config(**config_dict)
            else:
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

            team = ResearchTeam(config=config)

            # Update progress
            self.update_state(
                state="PROCESSING", meta={"status": "Research agents working...", "progress": 30}
            )
            emit_progress(task_id, "Research agents working...", 30)

            # Run research
            start_time = datetime.now(timezone.utc)
            messages = team.run(task_text, verbose=False)
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            # Update progress
            self.update_state(
                state="PROCESSING", meta={"status": "Saving results...", "progress": 90}
            )
            emit_progress(task_id, "Saving results...", 90)

            # Save messages
            for idx, msg in enumerate(messages):
                if hasattr(msg, "source") and hasattr(msg, "content"):
                    agent_message = AgentMessage(
                        task_id=task_id, agent=msg.source, content=msg.content, order=idx
                    )
                    db.session.add(agent_message)

            # Save metrics
            summary = team.get_summary()
            task_metrics = TaskMetrics(
                task_id=task_id,
                duration=duration,
                total_messages=len(messages),
                token_usage=summary.get("token_usage"),
                model_info=summary.get("model_info"),
            )
            db.session.add(task_metrics)

            # Update task status
            research_task.status = "completed"
            research_task.completed_at = end_time
            db.session.commit()

            # Emit completion
            emit_progress(task_id, "Completed", 100)

            return {
                "success": True,
                "task_id": task_id,
                "duration": duration,
                "message_count": len(messages),
            }

        except Exception as e:
            # Update task with error
            research_task.status = "failed"
            research_task.error = str(e)
            research_task.completed_at = datetime.now(timezone.utc)
            db.session.commit()

            # Emit failure
            emit_progress(task_id, f"Failed: {str(e)}", 0)

            return {"success": False, "error": str(e)}
