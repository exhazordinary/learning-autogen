"""AutoGen Research - Production-grade Multi-Agent AI Research System."""

__version__ = "2.0.0"

from .agents import AnalysisAgent, BaseAgent, CriticAgent, ResearchAgent, WriterAgent
from .config import Config, LoggingConfig, ModelConfig, TeamConfig
from .database import AgentMessage, ResearchTask, TaskMetrics, db
from .models import ModelFactory
from .teams import ResearchTeam
from .utils.logger import get_logger, setup_logger

__all__ = [
    # Version
    "__version__",
    # Agents
    "BaseAgent",
    "ResearchAgent",
    "AnalysisAgent",
    "WriterAgent",
    "CriticAgent",
    # Teams
    "ResearchTeam",
    # Configuration
    "Config",
    "ModelConfig",
    "LoggingConfig",
    "TeamConfig",
    # Models
    "ModelFactory",
    # Database
    "db",
    "ResearchTask",
    "AgentMessage",
    "TaskMetrics",
    # Utils
    "get_logger",
    "setup_logger",
]
