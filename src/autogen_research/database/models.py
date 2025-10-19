"""Database models for research tasks and messages."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Index

db = SQLAlchemy()


class ResearchTask(db.Model):
    """Research task model."""

    __tablename__ = "research_tasks"

    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.String(100), nullable=True)  # For future authentication

    # Relationships
    messages = db.relationship(
        "AgentMessage", backref="task", lazy="dynamic", cascade="all, delete-orphan"
    )
    metrics = db.relationship(
        "TaskMetrics", backref="task", uselist=False, cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_status_created", "status", "created_at"),
        Index("idx_user_created", "user_id", "created_at"),
    )

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "task": self.task,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "messages": [msg.to_dict() for msg in self.messages],
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }

    def __repr__(self):
        return f"<ResearchTask {self.id}: {self.status}>"


class AgentMessage(db.Model):
    """Agent message model."""

    __tablename__ = "agent_messages"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("research_tasks.id"), nullable=False)
    agent = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.Column(db.Integer, default=0)
    token_count = db.Column(db.Integer, nullable=True)  # Token count for this message

    # Index for querying messages by task
    __table_args__ = (Index("idx_task_order", "task_id", "order"),)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "agent": self.agent,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "order": self.order,
            "token_count": self.token_count,
        }

    def __repr__(self):
        return f"<AgentMessage {self.id}: {self.agent}>"


class TaskMetrics(db.Model):
    """Task metrics model."""

    __tablename__ = "task_metrics"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("research_tasks.id"), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # in seconds
    total_messages = db.Column(db.Integer, default=0)
    token_usage = db.Column(JSON, nullable=True)
    model_info = db.Column(JSON, nullable=True)

    # Detailed token tracking
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    total_tokens = db.Column(db.Integer, default=0)
    estimated_cost = db.Column(db.Float, default=0.0)  # USD

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "duration": self.duration,
            "total_messages": self.total_messages,
            "token_usage": self.token_usage,
            "model_info": self.model_info,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
        }

    def __repr__(self):
        return f"<TaskMetrics {self.id}: {self.duration}s>"
