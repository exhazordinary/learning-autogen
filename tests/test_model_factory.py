"""Tests for model factory."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.models import ModelFactory


class TestModelFactory:
    """Tests for ModelFactory class."""

    def test_create_ollama_client(self):
        """Test creating Ollama client."""
        client = ModelFactory.create_ollama_client()
        assert client is not None

    def test_create_ollama_client_custom(self):
        """Test creating Ollama client with custom settings."""
        client = ModelFactory.create_ollama_client(
            model="mistral",
            temperature=0.5,
        )
        assert client is not None

    def test_create_client_ollama(self):
        """Test creating client with model_type."""
        client = ModelFactory.create_client(model_type="ollama")
        assert client is not None

    def test_create_client_invalid_type(self):
        """Test creating client with invalid type."""
        with pytest.raises(ValueError, match="Unsupported model type"):
            ModelFactory.create_client(model_type="invalid")  # type: ignore

    def test_get_model_config(self):
        """Test getting model configuration."""
        config = ModelFactory.get_model_config("ollama")
        assert "model" in config
        assert "temperature" in config
        assert config["model"] == "llama3.2"
