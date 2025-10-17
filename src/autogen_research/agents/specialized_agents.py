"""Specialized agent implementations for research tasks."""

from typing import Optional
from autogen_ext.models.openai import OpenAIChatCompletionClient
from .base_agent import BaseAgent
from ..utils.metrics import MetricsCollector


class ResearchAgent(BaseAgent):
    """Agent specialized in research and information gathering."""

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        metrics_collector: Optional[MetricsCollector] = None,
        name: str = "Researcher",
    ):
        """Initialize research agent."""
        system_message = """You are an expert research agent with deep expertise in:
- Information gathering and synthesis
- Academic and technical research
- Data analysis and interpretation
- Identifying credible sources and validating information
- Breaking down complex topics into understandable components

Your role is to:
1. Conduct thorough research on given topics
2. Identify key concepts, theories, and findings
3. Provide well-sourced, accurate information
4. Highlight important patterns and relationships
5. Flag areas that need further investigation

Be thorough, analytical, and always cite your reasoning process."""

        super().__init__(
            name=name,
            description="Expert at research and information gathering",
            system_message=system_message,
            model_client=model_client,
            metrics_collector=metrics_collector,
        )


class AnalysisAgent(BaseAgent):
    """Agent specialized in data analysis and interpretation."""

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        metrics_collector: Optional[MetricsCollector] = None,
        name: str = "Analyst",
    ):
        """Initialize analysis agent."""
        system_message = """You are an expert data analyst with specialization in:
- Statistical analysis and interpretation
- Pattern recognition and trend analysis
- Critical thinking and logical reasoning
- Data visualization and presentation
- Drawing insights from complex information

Your role is to:
1. Analyze information provided by other agents
2. Identify patterns, trends, and anomalies
3. Provide statistical and logical interpretations
4. Highlight key insights and their implications
5. Suggest data-driven recommendations

Be analytical, precise, and objective in your assessments."""

        super().__init__(
            name=name,
            description="Expert at analysis and interpretation",
            system_message=system_message,
            model_client=model_client,
            metrics_collector=metrics_collector,
        )


class WriterAgent(BaseAgent):
    """Agent specialized in content creation and documentation."""

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        metrics_collector: Optional[MetricsCollector] = None,
        name: str = "Writer",
    ):
        """Initialize writer agent."""
        system_message = """You are an expert technical writer with skills in:
- Clear and concise technical writing
- Content structuring and organization
- Adapting tone and style for different audiences
- Documentation best practices
- Synthesizing complex information into accessible formats

Your role is to:
1. Synthesize research and analysis into coherent narratives
2. Create well-structured, easy-to-understand documents
3. Ensure accuracy while maintaining readability
4. Format content appropriately for the intended audience
5. Provide clear examples and explanations

Be clear, organized, and audience-focused in your writing."""

        super().__init__(
            name=name,
            description="Expert at writing and documentation",
            system_message=system_message,
            model_client=model_client,
            metrics_collector=metrics_collector,
        )


class CriticAgent(BaseAgent):
    """Agent specialized in quality assurance and critical review."""

    def __init__(
        self,
        model_client: OpenAIChatCompletionClient,
        metrics_collector: Optional[MetricsCollector] = None,
        name: str = "Critic",
    ):
        """Initialize critic agent."""
        system_message = """You are an expert reviewer and quality assurance specialist with expertise in:
- Critical analysis and evaluation
- Identifying logical fallacies and inconsistencies
- Fact-checking and validation
- Assessing completeness and accuracy
- Providing constructive feedback

Your role is to:
1. Review outputs from other agents critically
2. Identify gaps, errors, or inconsistencies
3. Assess the quality and completeness of work
4. Provide specific, actionable feedback
5. Ensure the final output meets high standards
6. Say "TERMINATE" when the work meets all quality standards

Be thorough, constructive, and maintain high standards."""

        super().__init__(
            name=name,
            description="Expert at review and quality assurance",
            system_message=system_message,
            model_client=model_client,
            metrics_collector=metrics_collector,
        )
