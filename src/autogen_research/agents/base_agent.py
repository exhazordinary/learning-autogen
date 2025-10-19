"""Base agent class with enhanced functionality."""

from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector

logger = get_logger(__name__)


class BaseAgent:
    """
    Enhanced base agent with logging and metrics tracking.

    This class wraps AutoGen's AssistantAgent with additional functionality
    for production use including logging, metrics, and error handling.
    """

    def __init__(
        self,
        name: str,
        description: str,
        system_message: str,
        model_client: OpenAIChatCompletionClient,
        metrics_collector: MetricsCollector | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Initialize base agent.

        Args:
            name: Agent name
            description: Agent description
            system_message: System prompt for the agent
            model_client: Model client for LLM interactions
            metrics_collector: Optional metrics collector
            metadata: Optional metadata for the agent
        """
        self.name = name
        self.description = description
        self.system_message = system_message
        self.model_client = model_client
        self.metrics_collector = metrics_collector
        self.metadata = metadata or {}

        # Create the underlying AutoGen agent
        self.agent = AssistantAgent(
            name=name,
            description=description,
            system_message=system_message,
            model_client=model_client,
        )

        logger.info(f"Initialized agent: {name}")

    def get_agent(self) -> AssistantAgent:
        """Get the underlying AutoGen AssistantAgent."""
        return self.agent

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"BaseAgent(name={self.name}, description={self.description})"
