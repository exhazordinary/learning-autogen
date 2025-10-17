"""Tests for metrics collection."""

import time
import pytest
from pathlib import Path
import tempfile
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.utils.metrics import MetricsCollector, AgentMetrics


class TestAgentMetrics:
    """Tests for AgentMetrics class."""

    def test_metric_creation(self):
        """Test creating a metric."""
        metric = AgentMetrics(
            agent_name="TestAgent",
            task="Test task",
            start_time=time.time(),
        )
        assert metric.agent_name == "TestAgent"
        assert metric.task == "Test task"
        assert metric.success is False

    def test_duration_calculation(self):
        """Test duration calculation."""
        start = time.time()
        metric = AgentMetrics(
            agent_name="TestAgent",
            task="Test task",
            start_time=start,
        )
        time.sleep(0.1)
        metric.end_time = time.time()
        assert metric.duration >= 0.1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        metric = AgentMetrics(
            agent_name="TestAgent",
            task="Test task",
            start_time=time.time(),
            end_time=time.time(),
            success=True,
        )
        metric_dict = metric.to_dict()
        assert metric_dict["agent_name"] == "TestAgent"
        assert metric_dict["success"] is True


class TestMetricsCollector:
    """Tests for MetricsCollector class."""

    def test_collector_initialization(self):
        """Test collector initialization."""
        collector = MetricsCollector()
        assert len(collector.metrics) == 0
        assert collector.session_start > 0

    def test_start_task(self):
        """Test starting a task."""
        collector = MetricsCollector()
        metric = collector.start_task("TestAgent", "Test task")
        assert len(collector.metrics) == 1
        assert metric.agent_name == "TestAgent"

    def test_end_task(self):
        """Test ending a task."""
        collector = MetricsCollector()
        metric = collector.start_task("TestAgent", "Test task")
        collector.end_task(
            metric,
            success=True,
            tokens_used=100,
            response_length=500,
        )
        assert metric.success is True
        assert metric.tokens_used == 100
        assert metric.response_length == 500
        assert metric.end_time is not None

    def test_get_summary(self):
        """Test getting summary statistics."""
        collector = MetricsCollector()

        # Add successful task
        metric1 = collector.start_task("Agent1", "Task 1")
        collector.end_task(metric1, success=True, tokens_used=100)

        # Add failed task
        metric2 = collector.start_task("Agent2", "Task 2")
        collector.end_task(metric2, success=False)

        summary = collector.get_summary()
        assert summary["total_tasks"] == 2
        assert summary["successful_tasks"] == 1
        assert summary["failed_tasks"] == 1
        assert summary["success_rate"] == 0.5
        assert summary["total_tokens"] == 100

    def test_export_to_file(self):
        """Test exporting metrics to file."""
        collector = MetricsCollector()
        metric = collector.start_task("TestAgent", "Test task")
        collector.end_task(metric, success=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "metrics.json"
            collector.export_to_file(filepath)

            assert filepath.exists()

            # Verify content
            with open(filepath) as f:
                data = json.load(f)
                assert "summary" in data
                assert "metrics" in data
                assert len(data["metrics"]) == 1

    def test_agent_statistics(self):
        """Test agent-specific statistics."""
        collector = MetricsCollector()

        # Add tasks for Agent1
        for i in range(3):
            metric = collector.start_task("Agent1", f"Task {i}")
            collector.end_task(metric, success=True, tokens_used=50)

        # Add tasks for Agent2
        for i in range(2):
            metric = collector.start_task("Agent2", f"Task {i}")
            collector.end_task(metric, success=True, tokens_used=30)

        summary = collector.get_summary()
        agent_stats = summary["agent_statistics"]

        assert "Agent1" in agent_stats
        assert "Agent2" in agent_stats
        assert agent_stats["Agent1"]["total_tasks"] == 3
        assert agent_stats["Agent2"]["total_tasks"] == 2
        assert agent_stats["Agent1"]["total_tokens"] == 150
        assert agent_stats["Agent2"]["total_tokens"] == 60
