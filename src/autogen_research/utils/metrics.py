"""Metrics collection and monitoring for agent performance."""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


@dataclass
class AgentMetrics:
    """Metrics for a single agent interaction."""

    agent_name: str
    task: str
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    tokens_used: int = 0
    response_length: int = 0
    metadata: Dict = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Calculate duration in seconds."""
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "agent_name": self.agent_name,
            "task": self.task,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration": self.duration,
            "success": self.success,
            "error": self.error,
            "tokens_used": self.tokens_used,
            "response_length": self.response_length,
            "metadata": self.metadata,
        }


class MetricsCollector:
    """Collects and manages metrics for agent operations."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[AgentMetrics] = []
        self.session_start = time.time()

    def start_task(self, agent_name: str, task: str) -> AgentMetrics:
        """Start tracking a new task."""
        metric = AgentMetrics(
            agent_name=agent_name,
            task=task,
            start_time=time.time(),
        )
        self.metrics.append(metric)
        return metric

    def end_task(
        self,
        metric: AgentMetrics,
        success: bool = True,
        error: Optional[str] = None,
        tokens_used: int = 0,
        response_length: int = 0,
        metadata: Optional[Dict] = None,
    ):
        """End tracking a task and record results."""
        metric.end_time = time.time()
        metric.success = success
        metric.error = error
        metric.tokens_used = tokens_used
        metric.response_length = response_length
        if metadata:
            metric.metadata.update(metadata)

    def get_summary(self) -> Dict:
        """Get summary statistics of all metrics."""
        total_tasks = len(self.metrics)
        successful_tasks = sum(1 for m in self.metrics if m.success)
        failed_tasks = total_tasks - successful_tasks
        total_duration = sum(m.duration for m in self.metrics if m.end_time)
        total_tokens = sum(m.tokens_used for m in self.metrics)

        agent_stats = {}
        for metric in self.metrics:
            if metric.agent_name not in agent_stats:
                agent_stats[metric.agent_name] = {
                    "total_tasks": 0,
                    "successful_tasks": 0,
                    "total_duration": 0.0,
                    "total_tokens": 0,
                }
            stats = agent_stats[metric.agent_name]
            stats["total_tasks"] += 1
            stats["successful_tasks"] += 1 if metric.success else 0
            stats["total_duration"] += metric.duration
            stats["total_tokens"] += metric.tokens_used

        return {
            "session_duration": time.time() - self.session_start,
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "total_duration": total_duration,
            "total_tokens": total_tokens,
            "avg_task_duration": total_duration / total_tasks if total_tasks > 0 else 0,
            "agent_statistics": agent_stats,
        }

    def export_to_file(self, filepath: Path):
        """Export metrics to a JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "summary": self.get_summary(),
            "metrics": [m.to_dict() for m in self.metrics],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def print_summary(self):
        """Print a formatted summary of metrics."""
        summary = self.get_summary()
        print("\n" + "=" * 80)
        print("METRICS SUMMARY")
        print("=" * 80)
        print(f"Session Duration: {summary['session_duration']:.2f}s")
        print(f"Total Tasks: {summary['total_tasks']}")
        print(f"Successful: {summary['successful_tasks']} | Failed: {summary['failed_tasks']}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Avg Task Duration: {summary['avg_task_duration']:.2f}s")
        print(f"Total Tokens: {summary['total_tokens']}")
        print("\nAgent Statistics:")
        for agent_name, stats in summary["agent_statistics"].items():
            print(f"  {agent_name}:")
            print(f"    Tasks: {stats['total_tasks']}")
            print(f"    Success Rate: {stats['successful_tasks']}/{stats['total_tasks']}")
            print(f"    Total Duration: {stats['total_duration']:.2f}s")
            print(f"    Total Tokens: {stats['total_tokens']}")
        print("=" * 80)
