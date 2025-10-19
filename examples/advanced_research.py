"""
Advanced research example with custom configuration and multiple tasks.

This demonstrates more sophisticated usage of the research team.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.config import Config
from src.autogen_research.teams import ResearchTeam
from src.autogen_research.utils import setup_logger


def run_research_pipeline():
    """Run a multi-stage research pipeline."""
    # Setup logging
    logger = setup_logger("autogen_research", log_file=Path("logs/advanced_research.log"))

    # Load configuration from environment
    config = Config.from_env()

    print("\n" + "=" * 80)
    print("AUTOGEN RESEARCH ASSISTANT - Advanced Pipeline")
    print("=" * 80)
    print("\nConfiguration:")
    print(f"  Model: {config.model.model_type} / {config.model.model_name}")
    print(f"  Temperature: {config.model.temperature}")
    print(f"  Max Rounds: {config.team.max_rounds}")
    print("=" * 80)

    # Initialize team
    team = ResearchTeam(config=config)

    # Define multiple research tasks
    tasks = [
        {
            "title": "Market Analysis",
            "task": """Analyze the current state of AI agent frameworks in 2024.

Focus on:
1. Leading frameworks and their features
2. Market adoption and trends
3. Key differentiators
4. Future outlook

Provide a concise analysis with key takeaways.""",
        },
        {
            "title": "Technical Deep-Dive",
            "task": """Explain how AutoGen implements multi-agent communication.

Cover:
1. Core architecture
2. Message passing mechanisms
3. Agent coordination strategies
4. Advantages of the approach

Keep it technical but clear.""",
        },
    ]

    results = []

    # Execute each task
    for idx, task_info in enumerate(tasks, 1):
        print(f"\n{'=' * 80}")
        print(f"TASK {idx}/{len(tasks)}: {task_info['title']}")
        print("=" * 80)
        print(f"\n{task_info['task']}\n")
        print("-" * 80)

        try:
            messages = team.run(task_info["task"], verbose=True)
            results.append(
                {
                    "title": task_info["title"],
                    "success": True,
                    "message_count": len(messages),
                }
            )
            logger.info(f"Task '{task_info['title']}' completed successfully")

        except Exception as e:
            logger.error(f"Task '{task_info['title']}' failed: {e}")
            results.append(
                {
                    "title": task_info["title"],
                    "success": False,
                    "error": str(e),
                }
            )

        print("\n" + "=" * 80)

    # Print final summary
    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)

    for idx, result in enumerate(results, 1):
        status = "✓ SUCCESS" if result["success"] else "✗ FAILED"
        print(f"{idx}. {result['title']}: {status}")
        if result["success"]:
            print(f"   Messages: {result['message_count']}")

    print("\n")
    team.print_summary()

    # Export metrics
    metrics_file = "logs/advanced_research_metrics.json"
    team.export_metrics(metrics_file)
    print(f"\nMetrics exported to: {metrics_file}")


def main():
    """Main entry point."""
    # Set default environment variables if not set
    if "MODEL_TYPE" not in os.environ:
        os.environ["MODEL_TYPE"] = "ollama"
    if "MODEL_NAME" not in os.environ:
        os.environ["MODEL_NAME"] = "llama3.2"

    run_research_pipeline()


if __name__ == "__main__":
    main()
