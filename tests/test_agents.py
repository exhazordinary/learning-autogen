"""Tests for agent implementations."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.agents import (
    AnalysisAgent,
    CriticAgent,
    ResearchAgent,
    WriterAgent,
)
from src.autogen_research.utils.metrics import MetricsCollector


@pytest.fixture
def mock_model_client():
    """Create a mock model client."""
    client = Mock()
    client.model = "test-model"
    return client


@pytest.fixture
def metrics_collector():
    """Create a metrics collector."""
    return MetricsCollector()


def test_research_agent_creation(mock_model_client, metrics_collector):
    """Test creating a research agent."""
    agent = ResearchAgent(model_client=mock_model_client, metrics_collector=metrics_collector)

    assert agent is not None
    assert agent.name == "Researcher"
    assert "research" in agent.description.lower()


def test_analysis_agent_creation(mock_model_client, metrics_collector):
    """Test creating an analysis agent."""
    agent = AnalysisAgent(model_client=mock_model_client, metrics_collector=metrics_collector)

    assert agent is not None
    assert agent.name == "Analyst"
    assert "analysis" in agent.description.lower() or "analyze" in agent.description.lower()


def test_writer_agent_creation(mock_model_client, metrics_collector):
    """Test creating a writer agent."""
    agent = WriterAgent(model_client=mock_model_client, metrics_collector=metrics_collector)

    assert agent is not None
    assert agent.name == "Writer"
    assert "write" in agent.description.lower() or "document" in agent.description.lower()


def test_critic_agent_creation(mock_model_client, metrics_collector):
    """Test creating a critic agent."""
    agent = CriticAgent(model_client=mock_model_client, metrics_collector=metrics_collector)

    assert agent is not None
    assert agent.name == "Critic"
    assert "review" in agent.description.lower() or "critic" in agent.description.lower()


def test_agent_has_system_message(mock_model_client, metrics_collector):
    """Test that agents have system messages."""
    agent = ResearchAgent(model_client=mock_model_client, metrics_collector=metrics_collector)

    assert hasattr(agent, "system_message")
    assert len(agent.system_message) > 0


def test_agent_get_agent_method(mock_model_client, metrics_collector):
    """Test that agents can return their AutoGen agent instance."""
    agent = ResearchAgent(model_client=mock_model_client, metrics_collector=metrics_collector)

    autogen_agent = agent.get_agent()
    assert autogen_agent is not None
