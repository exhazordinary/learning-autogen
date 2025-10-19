"""Integration tests for Flask API endpoints."""

import json
import os
import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock Redis before any imports
os.environ["REDIS_URL"] = "redis://localhost:6379/15"

# Import after setting environment
from app import app, db  # noqa: E402
from src.autogen_research.database import AgentMessage, ResearchTask  # noqa: E402


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["RATELIMIT_ENABLED"] = False

    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()
        yield test_client
        with app.app_context():
            db.drop_all()


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    # Health check may fail if Redis is not available, which is okay in tests
    assert response.status_code in [200, 503]
    data = json.loads(response.data)
    assert "status" in data


def test_config_endpoint(client):
    """Test config endpoint."""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "model_type" in data
    assert "model_name" in data
    assert "temperature" in data


def test_create_research_task(client):
    """Test creating a research task."""
    response = client.post(
        "/api/v1/research",
        data=json.dumps({"task": "Test research question"}),
        content_type="application/json",
    )
    assert response.status_code == 202
    data = json.loads(response.data)
    assert data["success"] is True
    assert "task_id" in data
    assert data["status"] == "queued"


def test_create_research_task_invalid(client):
    """Test creating research task with invalid data."""
    response = client.post(
        "/api/v1/research", data=json.dumps({"task": ""}), content_type="application/json"
    )
    assert response.status_code == 400


def test_create_research_task_too_long(client):
    """Test creating research task with text too long."""
    response = client.post(
        "/api/v1/research", data=json.dumps({"task": "x" * 10000}), content_type="application/json"
    )
    assert response.status_code == 400


def test_get_research_task(client):
    """Test getting a research task."""
    # Create a task first
    with app.app_context():
        task = ResearchTask(task="Test task", status="completed")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.get(f"/api/v1/research/{task_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["task"]["id"] == task_id


def test_get_research_task_not_found(client):
    """Test getting non-existent task."""
    response = client.get("/api/v1/research/99999")
    assert response.status_code == 404


def test_list_research_tasks(client):
    """Test listing research tasks."""
    # Create some tasks
    with app.app_context():
        for i in range(5):
            task = ResearchTask(task=f"Test task {i}", status="completed")
            db.session.add(task)
        db.session.commit()

    response = client.get("/api/v1/research")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert len(data["tasks"]) == 5
    assert "pagination" in data


def test_list_research_tasks_pagination(client):
    """Test pagination."""
    # Create some tasks
    with app.app_context():
        for i in range(15):
            task = ResearchTask(task=f"Test task {i}", status="completed")
            db.session.add(task)
        db.session.commit()

    response = client.get("/api/v1/research?page=1&per_page=10")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["tasks"]) == 10

    response = client.get("/api/v1/research?page=2&per_page=10")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["tasks"]) == 5


def test_list_research_tasks_filter_status(client):
    """Test filtering by status."""
    # Create tasks with different statuses
    with app.app_context():
        task1 = ResearchTask(task="Task 1", status="completed")
        task2 = ResearchTask(task="Task 2", status="failed")
        task3 = ResearchTask(task="Task 3", status="completed")
        db.session.add_all([task1, task2, task3])
        db.session.commit()

    response = client.get("/api/v1/research?status=completed")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["tasks"]) == 2


def test_export_research_task(client):
    """Test exporting research task."""
    # Create a task with messages
    with app.app_context():
        task = ResearchTask(task="Test task", status="completed")
        db.session.add(task)
        db.session.commit()

        msg = AgentMessage(task_id=task.id, agent="Researcher", content="Test content", order=0)
        db.session.add(msg)
        db.session.commit()
        task_id = task.id

    response = client.get(f"/api/v1/research/{task_id}/export")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "markdown" in data
    assert "# Research Task" in data["markdown"]
    assert "Test content" in data["markdown"]


def test_get_task_status(client):
    """Test getting task status."""
    # Create a task
    with app.app_context():
        task = ResearchTask(task="Test task", status="pending")
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.get(f"/api/v1/research/{task_id}/status")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["status"] == "pending"
