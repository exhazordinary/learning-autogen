"""Unit tests for database models."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, db
from src.autogen_research.database import AgentMessage, ResearchTask, TaskMetrics


@pytest.fixture
def db_session():
    """Create test database session."""
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield db.session
        db.drop_all()


def test_create_research_task(db_session):
    """Test creating a research task."""
    task = ResearchTask(task="Test task", status="pending")
    db_session.add(task)
    db_session.commit()

    assert task.id is not None
    assert task.task == "Test task"
    assert task.status == "pending"
    assert task.created_at is not None


def test_research_task_to_dict(db_session):
    """Test converting research task to dictionary."""
    task = ResearchTask(task="Test task", status="completed")
    db_session.add(task)
    db_session.commit()

    task_dict = task.to_dict()
    assert task_dict["id"] == task.id
    assert task_dict["task"] == "Test task"
    assert task_dict["status"] == "completed"
    assert "messages" in task_dict
    assert "metrics" in task_dict


def test_agent_message(db_session):
    """Test creating agent messages."""
    task = ResearchTask(task="Test task", status="pending")
    db_session.add(task)
    db_session.commit()

    message = AgentMessage(task_id=task.id, agent="Researcher", content="Test content", order=0)
    db_session.add(message)
    db_session.commit()

    assert message.id is not None
    assert message.agent == "Researcher"
    assert message.content == "Test content"
    assert message.timestamp is not None


def test_task_messages_relationship(db_session):
    """Test task-messages relationship."""
    task = ResearchTask(task="Test task", status="pending")
    db_session.add(task)
    db_session.commit()

    msg1 = AgentMessage(task_id=task.id, agent="Agent1", content="Content1", order=0)
    msg2 = AgentMessage(task_id=task.id, agent="Agent2", content="Content2", order=1)
    db_session.add_all([msg1, msg2])
    db_session.commit()

    assert task.messages.count() == 2
    assert msg1.task == task
    assert msg2.task == task


def test_task_metrics(db_session):
    """Test task metrics."""
    task = ResearchTask(task="Test task", status="completed")
    db_session.add(task)
    db_session.commit()

    metrics = TaskMetrics(
        task_id=task.id,
        duration=45.5,
        total_messages=5,
        token_usage={"total": 1000},
        model_info={"name": "llama3.2"},
    )
    db_session.add(metrics)
    db_session.commit()

    assert metrics.id is not None
    assert metrics.duration == 45.5
    assert metrics.total_messages == 5
    assert metrics.token_usage["total"] == 1000


def test_task_metrics_relationship(db_session):
    """Test task-metrics relationship."""
    task = ResearchTask(task="Test task", status="completed")
    db_session.add(task)
    db_session.commit()

    metrics = TaskMetrics(task_id=task.id, duration=30.0, total_messages=3)
    db_session.add(metrics)
    db_session.commit()

    assert task.metrics == metrics
    assert metrics.task == task


def test_cascade_delete(db_session):
    """Test cascade deletion."""
    task = ResearchTask(task="Test task", status="completed")
    db_session.add(task)
    db_session.commit()

    msg = AgentMessage(task_id=task.id, agent="Agent1", content="Content1", order=0)
    metrics = TaskMetrics(task_id=task.id, duration=30.0, total_messages=1)
    db_session.add_all([msg, metrics])
    db_session.commit()

    # Store IDs before deletion
    msg_id = msg.id
    metrics_id = metrics.id

    # Delete task
    db_session.delete(task)
    db_session.commit()

    # Check that related objects are also deleted
    assert db_session.get(AgentMessage, msg_id) is None
    assert db_session.get(TaskMetrics, metrics_id) is None
