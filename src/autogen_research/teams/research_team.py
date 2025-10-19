"""Research team orchestration with advanced features."""

import asyncio
from typing import Any

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core.tools import FunctionTool

from ..agents import AnalysisAgent, CriticAgent, ResearchAgent, WriterAgent
from ..config import Config
from ..models import ModelFactory
from ..tools import calculator, web_search
from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector
from ..utils.tokens import TokenCounter, truncate_conversation_history

logger = get_logger(__name__)


class ResearchTeam:
    """
    A coordinated team of AI agents for comprehensive research tasks.

    Features:
    - Tool calling (web_search, calculator)
    - Token counting and cost estimation
    - Context window management
    - Dynamic agent selection
    - Automatic speaker selection
    - Chain-of-thought prompting

    This team consists of:
    - Researcher: Gathers information (with web_search, calculator)
    - Analyst: Analyzes data and identifies patterns (with calculator)
    - Writer: Synthesizes findings into clear documentation
    - Critic: Reviews and ensures quality
    """

    def __init__(
        self,
        config: Config | None = None,
        metrics_collector: MetricsCollector | None = None,
        enable_tools: bool = True,
    ):
        """
        Initialize research team.

        Args:
            config: Configuration object
            metrics_collector: Optional metrics collector
            enable_tools: Whether to enable tool calling (default: True)
        """
        self.config = config or Config.from_env()
        self.metrics = metrics_collector or MetricsCollector()
        self.enable_tools = enable_tools

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

        # Initialize token counter
        self.token_counter = TokenCounter(model=self.config.model.model_name)

        # Register tools
        self.tools = []
        if enable_tools:
            self.tools = [
                FunctionTool(web_search, description="Search the web for information"),
                FunctionTool(calculator, description="Evaluate mathematical expressions"),
            ]
            logger.info(f"Registered {len(self.tools)} tools")

        # Initialize agents with tools
        # Researcher gets web search and calculator (all tools)
        self.researcher = ResearchAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
            tools=self.tools if enable_tools else None,
        )

        # Analyst gets calculator only
        self.analyst = AnalysisAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
            tools=[self.tools[1]] if enable_tools else None,  # calculator only
        )

        # Writer doesn't need tools
        self.writer = WriterAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
        )

        # Critic doesn't need tools
        self.critic = CriticAgent(
            model_client=self.model_client,
            metrics_collector=self.metrics,
        )

        # Create termination conditions
        self.termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(
            self.config.team.max_rounds
        )

        # Store for context window management
        self.max_context_tokens = 4000  # Adjust based on model

        logger.info("Research Team initialized successfully")

    def select_agents_for_task(self, task: str) -> list:
        """
        Dynamically select agents based on task content.

        Args:
            task: The research task

        Returns:
            List of agents to use for this task
        """
        task_lower = task.lower()
        agents = []

        # Researcher is always included
        agents.append(self.researcher.get_agent())

        # Check if analysis is needed
        if any(
            word in task_lower
            for word in ["analyze", "analysis", "trend", "pattern", "data", "statistics", "compare"]
        ):
            agents.append(self.analyst.get_agent())

        # Check if writing/synthesis is needed
        if any(
            word in task_lower for word in ["write", "explain", "summarize", "document", "report"]
        ):
            agents.append(self.writer.get_agent())
        elif "write" not in task_lower:
            # Include writer by default for synthesis
            agents.append(self.writer.get_agent())

        # Critic is always included for quality assurance
        agents.append(self.critic.get_agent())

        logger.info(f"Selected {len(agents)} agents for task: {[a.name for a in agents]}")
        return agents

    async def research(
        self,
        task: str,
        verbose: bool = True,
        use_dynamic_routing: bool = True,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Execute a research task with the team.

        Args:
            task: Research task description
            verbose: Whether to print messages in real-time
            use_dynamic_routing: Whether to dynamically select agents

        Returns:
            Tuple of (messages list, token statistics dict)
        """
        logger.info(f"Starting research task: {task}")

        metric = self.metrics.start_task(
            agent_name="ResearchTeam",
            task=task,
        )

        # Track tokens
        token_stats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost": 0.0,
        }

        try:
            # Select agents for this task
            if use_dynamic_routing:
                selected_agents = self.select_agents_for_task(task)
            else:
                selected_agents = [
                    self.researcher.get_agent(),
                    self.analyst.get_agent(),
                    self.writer.get_agent(),
                    self.critic.get_agent(),
                ]

            # Create team with selector for automatic speaker selection
            # This allows agents to speak when they have something to contribute
            team = SelectorGroupChat(
                participants=selected_agents,
                termination_condition=self.termination,
                model_client=self.model_client,
            )

            # Run the team
            stream = team.run_stream(task=task)

            messages: list[dict[str, Any]] = []
            conversation_history = []

            async for message in stream:
                messages.append(message)

                # Track message in history for context management
                if hasattr(message, "source") and hasattr(message, "content"):
                    conversation_history.append(
                        {"role": message.source, "content": message.content}
                    )

                    # Count tokens
                    content_tokens = self.token_counter.count_tokens(str(message.content))
                    token_stats["output_tokens"] += content_tokens

                    if verbose:
                        print(f"\n{'=' * 80}")
                        print(f"[{message.source}] ({content_tokens} tokens)")
                        print(f"{'-' * 80}")
                        print(message.content)

                # Context window management: truncate if getting too large
                if len(conversation_history) > 10:  # Every 10 messages
                    conversation_history = truncate_conversation_history(
                        conversation_history,
                        max_tokens=self.max_context_tokens,
                        model=self.config.model.model_name,
                        keep_system=True,
                    )

            # Calculate final token statistics
            input_task_tokens = self.token_counter.count_tokens(task)
            token_stats["input_tokens"] = input_task_tokens
            token_stats["total_tokens"] = token_stats["input_tokens"] + token_stats["output_tokens"]
            token_stats["estimated_cost"] = self.token_counter.estimate_cost(
                token_stats["input_tokens"],
                token_stats["output_tokens"],
                self.config.model.model_name,
            )

            # Get detailed stats
            detailed_stats = self.token_counter.get_token_stats(conversation_history)
            token_stats.update(detailed_stats)

            logger.info(
                f"Task completed. Messages: {len(messages)}, "
                f"Tokens: {token_stats['total_tokens']}, "
                f"Cost: ${token_stats['estimated_cost']:.4f}"
            )

            self.metrics.end_task(
                metric,
                success=True,
                response_length=len(messages),
                token_usage=token_stats,
            )

            return messages, token_stats

        except Exception as e:
            logger.error(f"Research task failed: {e}", exc_info=True)
            self.metrics.end_task(metric, success=False, error=str(e))
            raise

    def run(
        self,
        task: str,
        verbose: bool = True,
        use_dynamic_routing: bool = True,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """
        Synchronous wrapper for research method.

        Args:
            task: Research task description
            verbose: Whether to print messages in real-time
            use_dynamic_routing: Whether to dynamically select agents

        Returns:
            Tuple of (messages list, token statistics dict)
        """
        return asyncio.run(self.research(task, verbose, use_dynamic_routing))

    def get_summary(self) -> dict[str, Any]:
        """Get performance summary for the team."""
        return self.metrics.get_summary()

    def print_summary(self) -> None:
        """Print performance metrics summary."""
        self.metrics.print_summary()

    def export_metrics(self, filepath: str) -> None:
        """Export metrics to a file."""
        from pathlib import Path

        self.metrics.export_to_file(Path(filepath))
        logger.info(f"Metrics exported to: {filepath}")
