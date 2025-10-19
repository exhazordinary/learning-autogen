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


def emit_message(task_id: int, agent: str, content: str, order: int) -> None:
    """Emit individual agent message via WebSocket."""
    try:
        from app import socketio

        socketio.emit(
            "agent_message",
            {"task_id": task_id, "agent": agent, "content": content, "order": order},
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

            # Run research with streaming
            start_time = datetime.now(timezone.utc)

            # Use async streaming to emit messages in real-time
            import asyncio

            async def stream_and_save_messages():
                """Stream messages and emit them in real-time."""
                # Use the new v2.0 API - research() method returns (messages, stats)
                messages, stats = await team.research(task=task_text)
                idx = 0

                # Process all messages
                for message in messages:
                    # Emit and save each message as it arrives
                    if hasattr(message, "source") and hasattr(message, "content"):
                        # Save to database immediately
                        agent_message = AgentMessage(
                            task_id=task_id,
                            agent=message.source,
                            content=message.content,
                            order=idx,
                        )
                        db.session.add(agent_message)
                        db.session.commit()

                        # Emit message to frontend in real-time
                        emit_message(task_id, message.source, message.content, idx)
                        idx += 1

                return messages, stats

            messages, stats = asyncio.run(stream_and_save_messages())
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()

            # Update progress
            self.update_state(
                state="PROCESSING", meta={"status": "Saving results...", "progress": 90}
            )
            emit_progress(task_id, "Saving results...", 90)

            # Save metrics with v2.0 token stats
            task_metrics = TaskMetrics(
                task_id=task_id,
                duration=duration,
                total_messages=len(messages),
                input_tokens=stats.get("input_tokens", 0),
                output_tokens=stats.get("output_tokens", 0),
                total_tokens=stats.get("total_tokens", 0),
                estimated_cost=stats.get("estimated_cost", 0.0),
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
