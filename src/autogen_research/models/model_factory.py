"""Model factory for creating and managing AI model clients."""

from typing import Dict, Optional, Literal
from autogen_ext.models.openai import OpenAIChatCompletionClient
from ..utils.logger import get_logger

logger = get_logger(__name__)

ModelType = Literal["ollama", "openai", "anthropic"]


class ModelFactory:
    """Factory for creating model clients with standardized configuration."""

    @staticmethod
    def create_ollama_client(
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434/v1",
        temperature: float = 0.7,
        **kwargs,
    ) -> OpenAIChatCompletionClient:
        """
        Create an Ollama model client.

        Args:
            model: Model name (e.g., "llama3.2", "mistral")
            base_url: Ollama server URL
            temperature: Sampling temperature
            **kwargs: Additional client parameters

        Returns:
            Configured OpenAIChatCompletionClient for Ollama
        """
        logger.info(f"Creating Ollama client for model: {model}")

        # Remove api_key from kwargs if present (Ollama doesn't need it)
        kwargs.pop("api_key", None)

        return OpenAIChatCompletionClient(
            model=model,
            api_key="ollama",  # Ollama doesn't require a real API key
            base_url=base_url,
            model_info={
                "family": "unknown",
                "vision": False,
                "function_calling": True,
                "json_output": True,
            },
            temperature=temperature,
            **kwargs,
        )

    @staticmethod
    def create_openai_client(
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> OpenAIChatCompletionClient:
        """
        Create an OpenAI model client.

        Args:
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: OpenAI API key (reads from env if None)
            temperature: Sampling temperature
            **kwargs: Additional client parameters

        Returns:
            Configured OpenAIChatCompletionClient
        """
        logger.info(f"Creating OpenAI client for model: {model}")

        client_kwargs = {
            "model": model,
            "temperature": temperature,
            **kwargs,
        }

        if api_key:
            client_kwargs["api_key"] = api_key

        return OpenAIChatCompletionClient(**client_kwargs)

    @staticmethod
    def create_client(
        model_type: ModelType = "ollama",
        model: Optional[str] = None,
        **kwargs,
    ) -> OpenAIChatCompletionClient:
        """
        Create a model client based on type.

        Args:
            model_type: Type of model ("ollama", "openai", "anthropic")
            model: Model name (uses defaults if None)
            **kwargs: Additional client parameters

        Returns:
            Configured model client

        Raises:
            ValueError: If model_type is not supported
        """
        if model_type == "ollama":
            default_model = "llama3.2"
            return ModelFactory.create_ollama_client(
                model=model or default_model, **kwargs
            )
        elif model_type == "openai":
            default_model = "gpt-4"
            return ModelFactory.create_openai_client(
                model=model or default_model, **kwargs
            )
        else:
            raise ValueError(
                f"Unsupported model type: {model_type}. "
                f"Supported types: ollama, openai"
            )

    @staticmethod
    def get_model_config(model_type: ModelType) -> Dict:
        """
        Get default configuration for a model type.

        Args:
            model_type: Type of model

        Returns:
            Dictionary with default configuration
        """
        configs = {
            "ollama": {
                "model": "llama3.2",
                "base_url": "http://localhost:11434/v1",
                "temperature": 0.7,
            },
            "openai": {
                "model": "gpt-4",
                "temperature": 0.7,
            },
        }
        return configs.get(model_type, {})
