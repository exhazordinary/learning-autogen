"""Configuration management for AutoGen Research."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class ModelConfig:
    """Configuration for AI models."""

    model_type: Literal["ollama", "openai"] = "ollama"
    model_name: str | None = None
    temperature: float = 0.7
    base_url: str | None = None
    api_key: str | None = None

    def __post_init__(self):
        """Set defaults based on model type."""
        if self.model_name is None:
            self.model_name = "llama3.2" if self.model_type == "ollama" else "gpt-4"

        if self.model_type == "ollama" and self.base_url is None:
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        if self.model_type == "openai" and self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")


@dataclass
class LoggingConfig:
    """Configuration for logging."""

    level: str = "INFO"
    log_dir: Path = field(default_factory=lambda: Path("logs"))
    enable_file_logging: bool = True
    enable_metrics: bool = True

    def __post_init__(self):
        """Ensure log directory exists."""
        if self.enable_file_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class TeamConfig:
    """Configuration for agent teams."""

    max_rounds: int = 12
    enable_round_robin: bool = True
    timeout: int | None = None  # seconds


@dataclass
class Config:
    """Main configuration class."""

    model: ModelConfig = field(default_factory=ModelConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    team: TeamConfig = field(default_factory=TeamConfig)
    project_root: Path = field(default_factory=lambda: Path.cwd())

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        model_type = os.getenv("MODEL_TYPE", "ollama")
        model_config = ModelConfig(
            model_type=model_type,  # type: ignore
            model_name=os.getenv("MODEL_NAME"),
            temperature=float(os.getenv("TEMPERATURE", "0.7")),
        )

        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            enable_file_logging=os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true",
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
        )

        team_config = TeamConfig(
            max_rounds=int(os.getenv("MAX_ROUNDS", "12")),
            enable_round_robin=os.getenv("ENABLE_ROUND_ROBIN", "true").lower() == "true",
        )

        return cls(
            model=model_config,
            logging=logging_config,
            team=team_config,
        )

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "model": {
                "type": self.model.model_type,
                "name": self.model.model_name,
                "temperature": self.model.temperature,
            },
            "logging": {
                "level": self.logging.level,
                "enable_file_logging": self.logging.enable_file_logging,
                "enable_metrics": self.logging.enable_metrics,
            },
            "team": {
                "max_rounds": self.team.max_rounds,
                "enable_round_robin": self.team.enable_round_robin,
            },
        }
