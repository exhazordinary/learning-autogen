"""Tests for research team."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.config import Config, ModelConfig
from src.autogen_research.teams import ResearchTeam


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return Config(model=ModelConfig(model_type="ollama", model_name="test-model", temperature=0.7))


def test_research_team_creation(mock_config):
    """Test creating a research team."""
    with patch(
        "src.autogen_research.teams.research_team.ModelFactory.create_client"
    ) as mock_factory:
        mock_client = Mock()
        mock_client.model_info = {"function_calling": True}
        mock_factory.return_value = mock_client

        team = ResearchTeam(config=mock_config)

        assert team is not None
        assert team.researcher is not None
        assert team.analyst is not None
        assert team.writer is not None
        assert team.critic is not None
        assert team.config is not None
        assert team.token_counter is not None


def test_research_team_default_config():
    """Test creating a research team with default config."""
    with patch(
        "src.autogen_research.teams.research_team.ModelFactory.create_client"
    ) as mock_factory:
        mock_client = Mock()
        mock_client.model_info = {"function_calling": True}
        mock_factory.return_value = mock_client

        team = ResearchTeam()

        assert team is not None
        assert team.config is not None


def test_research_team_has_summary_methods(mock_config):
    """Test that research team has summary methods."""
    with patch(
        "src.autogen_research.teams.research_team.ModelFactory.create_client"
    ) as mock_factory:
        mock_client = Mock()
        mock_client.model_info = {"function_calling": True}
        mock_factory.return_value = mock_client

        team = ResearchTeam(config=mock_config)

        assert hasattr(team, "get_summary")
        assert hasattr(team, "print_summary")
        assert hasattr(team, "export_metrics")


def test_research_team_get_summary(mock_config):
    """Test getting summary from research team."""
    with patch(
        "src.autogen_research.teams.research_team.ModelFactory.create_client"
    ) as mock_factory:
        mock_client = Mock()
        mock_client.model_info = {"function_calling": True}
        mock_factory.return_value = mock_client

        team = ResearchTeam(config=mock_config)
        summary = team.get_summary()

        assert isinstance(summary, dict)
