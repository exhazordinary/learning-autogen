"""Unit tests for cache manager."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.autogen_research.database.cache import CacheManager


@pytest.fixture
def cache():
    """Create cache manager instance."""
    # Use a test Redis database
    cache_manager = CacheManager(redis_url='redis://localhost:6379/15', ttl=60)
    yield cache_manager
    # Clear test database
    cache_manager.clear_all()


def test_cache_set_and_get(cache):
    """Test setting and getting cache."""
    task = "Test research question"
    result = {
        'messages': ['Message 1', 'Message 2'],
        'metrics': {'duration': 30.0}
    }

    # Set cache
    success = cache.set(task, result)
    assert success is True

    # Get cache
    cached = cache.get(task)
    assert cached is not None
    assert cached['messages'] == result['messages']
    assert cached['metrics']['duration'] == 30.0


def test_cache_get_nonexistent(cache):
    """Test getting non-existent cache."""
    result = cache.get("Non-existent task")
    assert result is None


def test_cache_delete(cache):
    """Test deleting cache."""
    task = "Test task"
    result = {'data': 'test'}

    cache.set(task, result)
    assert cache.get(task) is not None

    cache.delete(task)
    assert cache.get(task) is None


def test_cache_key_generation(cache):
    """Test that same task generates same key."""
    task = "Same task"
    result1 = {'data': 'test1'}
    result2 = {'data': 'test2'}

    cache.set(task, result1)
    cached = cache.get(task)
    assert cached['data'] == 'test1'

    # Setting again with same task should overwrite
    cache.set(task, result2)
    cached = cache.get(task)
    assert cached['data'] == 'test2'


def test_cache_clear_all(cache):
    """Test clearing all cache."""
    cache.set("Task 1", {'data': 'test1'})
    cache.set("Task 2", {'data': 'test2'})
    cache.set("Task 3", {'data': 'test3'})

    cache.clear_all()

    assert cache.get("Task 1") is None
    assert cache.get("Task 2") is None
    assert cache.get("Task 3") is None


def test_cache_different_tasks(cache):
    """Test caching different tasks."""
    task1 = "First task"
    task2 = "Second task"
    result1 = {'data': 'result1'}
    result2 = {'data': 'result2'}

    cache.set(task1, result1)
    cache.set(task2, result2)

    cached1 = cache.get(task1)
    cached2 = cache.get(task2)

    assert cached1['data'] == 'result1'
    assert cached2['data'] == 'result2'
