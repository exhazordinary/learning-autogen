"""Research team orchestration with multiple specialized agents."""

import asyncio
from typing import List, Optional
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

from ..agents import ResearchAgent, AnalysisAgent, WriterAgent, CriticAgent
from ..models import ModelFactory
from ..utils.metrics import MetricsCollector
from ..utils.logger import get_logger
from ..config import Config

logger = get_logger(__name__)


class ResearchTeam:
    """
    A coordinated team of AI agents for comprehensive research tasks.

    This team consists of:
    - Researcher: Gathers information
    - Analyst: Analyzes data and identifies patterns
    - Writer: Synthesizes findings into clear documentation
    - Critic: Reviews and ensures quality
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        """
        Initialize research team.

        Args:
            config: Configuration object
            metrics_collector: Optional metrics collector
        """
        self.config = config or Config.from_env()
        self.metrics = metrics_collector or MetricsCollector()

        logger.info("Initializing Research Team")
        logger.info(f"Configuration: {self.config.to_dict()}")

        # Create model client
        self.model_client = ModelFactory.create_client(
            model_type=self.config.model.model_type,
            model=self.config.model.model_name,
            temperature=self.config.model.temperature,
            base_url=self.config.model.base_url,
            api_key=self.config.model.api_key,
        )

        # Initialize agents
        self.researcher = ResearchAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
        )

        self.analyst = AnalysisAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
        )

        self.writer = WriterAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
        )

        self.critic = CriticAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
        )

        # Create termination conditions
        termination = (
            TextMentionTermination("TERMINATE")
            | MaxMessageTermination(self.config.team.max_rounds)
        )

        # Create team
        self.team = RoundRobinGroupChat(
            participants=[
                self.researcher.get_agent(),
                self.analyst.get_agent(),
                self.writer.get_agent(),
                self.critic.get_agent(),
            ],
            termination_condition=termination,
        )

        logger.info("Research Team initialized successfully")

    async def research(self, task: str, verbose: bool = True) -> List[dict]:
        """
        Execute a research task with the team.

        Args:
            task: Research task description
            verbose: Whether to print messages in real-time

        Returns:
            List of messages from the conversation
        """
        logger.info(f"Starting research task: {task}")

        metric = self.metrics.start_task(
            agent_name="ResearchTeam",
            task=task,
        )

        try:
            # Run the team
            stream = self.team.run_stream(task=task)

            messages = []
            async for message in stream:
                messages.append(message)

                if verbose and hasattr(message, "source") and hasattr(message, "content"):
                    print(f"\n{'=' * 80}")
                    print(f"[{message.source}]")
                    print(f"{'-' * 80}")
                    print(message.content)

            self.metrics.end_task(
                metric,
                success=True,
                response_length=len(messages),
            )

            logger.info(f"Research task completed. Total messages: {len(messages)}")
            return messages

        except Exception as e:
            logger.error(f"Research task failed: {e}")
            self.metrics.end_task(metric, success=False, error=str(e))
            raise

    def run(self, task: str, verbose: bool = True) -> List[dict]:
        """
        Synchronous wrapper for research method.

        Args:
            task: Research task description
            verbose: Whether to print messages in real-time

        Returns:
            List of messages from the conversation
        """
        return asyncio.run(self.research(task, verbose))

    def get_summary(self) -> dict:
        """Get performance summary for the team."""
        return self.metrics.get_summary()

    def print_summary(self):
        """Print performance metrics summary."""
        self.metrics.print_summary()

    def export_metrics(self, filepath: str):
        """Export metrics to a file."""
        from pathlib import Path

        self.metrics.export_to_file(Path(filepath))
        logger.info(f"Metrics exported to: {filepath}")
