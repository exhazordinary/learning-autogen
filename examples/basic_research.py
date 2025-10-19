"""
Basic research example using the AutoGen Research Team.

This example demonstrates a simple research task with the team of AI agents.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.config import Config, LoggingConfig, ModelConfig
from src.autogen_research.teams import ResearchTeam
from src.autogen_research.utils import setup_logger


def main():
    """Run a basic research task."""
    # Setup logging
    setup_logger("autogen_research", log_file=Path("logs/basic_research.log"))

    # Create configuration
    config = Config(
        model=ModelConfig(
            model_type="ollama",
            model_name="llama3.2",
            temperature=0.7,
        ),
        logging=LoggingConfig(
            level="INFO",
            enable_file_logging=True,
            enable_metrics=True,
        ),
    )

    # Initialize research team
    print("\n" + "=" * 80)
    print("AUTOGEN RESEARCH ASSISTANT - Basic Example")
    print("=" * 80)

    team = ResearchTeam(config=config)

    # Define research task
    task = """Research and explain the concept of 'multi-agent systems' in AI.

Please provide:
1. A clear definition
2. Key components and characteristics
3. Real-world applications
4. Advantages and challenges

Keep the explanation concise and accessible."""

    print(f"\nResearch Task: {task}\n")
    print("=" * 80)

    # Execute research
    _ = team.run(task, verbose=True)

    # Print summary
    print("\n" + "=" * 80)
    print("RESEARCH COMPLETED")
    print("=" * 80)
    team.print_summary()

    # Export metrics
    team.export_metrics("logs/basic_research_metrics.json")


if __name__ == "__main__":
    main()
