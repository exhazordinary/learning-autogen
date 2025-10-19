"""CLI entry point for AutoGen Research."""

import argparse
import sys
from pathlib import Path

from .config import Config
from .teams import ResearchTeam
from .utils import setup_logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AutoGen Research Assistant - Multi-Agent AI Research System"
    )
    parser.add_argument(
        "task",
        type=str,
        help="Research task to execute",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="ollama",
        choices=["ollama", "openai"],
        help="Model type to use (default: ollama)",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model name (default: llama3.2 for ollama, gpt-4 for openai)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=12,
        help="Maximum conversation rounds (default: 12)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--export-metrics",
        type=str,
        help="Export metrics to file (e.g., metrics.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logger(
        "autogen_research",
        level=getattr(__import__("logging"), args.log_level),
        log_file=Path("logs/autogen_research.log"),
    )

    # Create configuration
    from .config import LoggingConfig, ModelConfig, TeamConfig

    config = Config(
        model=ModelConfig(
            model_type=args.model_type,  # type: ignore
            model_name=args.model,
            temperature=args.temperature,
        ),
        logging=LoggingConfig(level=args.log_level),
        team=TeamConfig(max_rounds=args.max_rounds),
    )

    # Print header
    if not args.quiet:
        print("\n" + "=" * 80)
        print("AUTOGEN RESEARCH ASSISTANT")
        print("=" * 80)
        print(f"Model: {config.model.model_type} / {config.model.model_name}")
        print(f"Task: {args.task}")
        print("=" * 80 + "\n")

    # Initialize team and run research
    team = ResearchTeam(config=config)

    try:
        _ = team.run(args.task, verbose=not args.quiet)

        if not args.quiet:
            print("\n" + "=" * 80)
            print("RESEARCH COMPLETED")
            print("=" * 80)
            team.print_summary()

        # Export metrics if requested
        if args.export_metrics:
            team.export_metrics(args.export_metrics)
            if not args.quiet:
                print(f"\nMetrics exported to: {args.export_metrics}")

        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nResearch interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
