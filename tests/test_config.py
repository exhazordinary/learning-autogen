"""Tests for configuration management."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.config import Config, LoggingConfig, ModelConfig, TeamConfig


class TestModelConfig:
    """Tests for ModelConfig."""

    def test_default_ollama_config(self):
        """Test default Ollama configuration."""
        config = ModelConfig(model_type="ollama")
        assert config.model_name == "llama3.2"
        assert config.model_type == "ollama"
        assert config.temperature == 0.7

    def test_default_openai_config(self):
        """Test default OpenAI configuration."""
        config = ModelConfig(model_type="openai")
        assert config.model_name == "gpt-4"
        assert config.model_type == "openai"

    def test_custom_config(self):
        """Test custom configuration."""
        config = ModelConfig(
            model_type="ollama",
            model_name="custom-model",
            temperature=0.5,
        )
        assert config.model_name == "custom-model"
        assert config.temperature == 0.5


class TestLoggingConfig:
    """Tests for LoggingConfig."""

    def test_default_config(self):
        """Test default logging configuration."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.enable_file_logging is True
        assert config.enable_metrics is True


class TestTeamConfig:
    """Tests for TeamConfig."""

    def test_default_config(self):
        """Test default team configuration."""
        config = TeamConfig()
        assert config.max_rounds == 12
        assert config.enable_round_robin is True
        assert config.timeout is None


class TestConfig:
    """Tests for main Config class."""

    def test_default_config(self):
        """Test default configuration."""
        config = Config()
        assert config.model.model_type == "ollama"
        assert config.logging.level == "INFO"
        assert config.team.max_rounds == 12

    def test_from_env(self):
        """Test configuration from environment."""
        # Set environment variables
        os.environ["MODEL_TYPE"] = "openai"
        os.environ["MODEL_NAME"] = "gpt-4"
        os.environ["TEMPERATURE"] = "0.5"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["MAX_ROUNDS"] = "20"

        config = Config.from_env()

        assert config.model.model_type == "openai"
        assert config.model.model_name == "gpt-4"
        assert config.model.temperature == 0.5
        assert config.logging.level == "DEBUG"
        assert config.team.max_rounds == 20

        # Cleanup
        for key in ["MODEL_TYPE", "MODEL_NAME", "TEMPERATURE", "LOG_LEVEL", "MAX_ROUNDS"]:
            os.environ.pop(key, None)

    def test_to_dict(self):
        """Test configuration serialization."""
        config = Config()
        config_dict = config.to_dict()

        assert "model" in config_dict
        assert "logging" in config_dict
        assert "team" in config_dict
        assert config_dict["model"]["type"] == "ollama"
