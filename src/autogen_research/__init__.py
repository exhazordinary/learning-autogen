"""
AutoGen Research Assistant - A production-grade multi-agent AI system.

This package provides a robust framework for building multi-agent AI systems
using AutoGen, with built-in logging, monitoring, and configuration management.
"""

__version__ = "0.1.0"
__author__ = "AutoGen Research Team"

from .agents.base_agent import BaseAgent
from .models.model_factory import ModelFactory
from .teams.research_team import ResearchTeam

__all__ = [
    "BaseAgent",
    "ModelFactory",
    "ResearchTeam",
]
