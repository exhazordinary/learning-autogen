"""Redis cache manager for research results."""

import hashlib
import json
from functools import wraps

import redis


class CacheManager:
    """Manages caching of research results."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl: int = 3600):
        """
        Initialize cache manager.

        Args:
            redis_url: Redis connection URL
            ttl: Time to live in seconds (default 1 hour)
        """
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl

    def _generate_key(self, task: str) -> str:
        """Generate cache key from task string."""
        task_hash = hashlib.sha256(task.encode()).hexdigest()
        return f"research:task:{task_hash}"

    def get(self, task: str) -> dict | None:
        """
        Get cached result for a task.

        Args:
            task: Research task string

        Returns:
            Cached result or None
        """
        try:
            key = self._generate_key(task)
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except (redis.RedisError, json.JSONDecodeError):
            return None
        return None

    def set(self, task: str, result: dict) -> bool:
        """
        Cache result for a task.

        Args:
            task: Research task string
            result: Result dictionary to cache

        Returns:
            True if successful
        """
        try:
            key = self._generate_key(task)
            self.redis_client.setex(key, self.ttl, json.dumps(result))
            return True
        except (redis.RedisError, json.JSONDecodeError):
            return False

    def delete(self, task: str) -> bool:
        """
        Delete cached result for a task.

        Args:
            task: Research task string

        Returns:
            True if successful
        """
        try:
            key = self._generate_key(task)
            self.redis_client.delete(key)
            return True
        except redis.RedisError:
            return False

    def clear_all(self) -> bool:
        """Clear all cached results."""
        try:
            for key in self.redis_client.scan_iter("research:task:*"):
                self.redis_client.delete(key)
            return True
        except redis.RedisError:
            return False


# Global cache manager instance
cache_manager = CacheManager()


def cached_research(ttl: int | None = None):
    """
    Decorator to cache research results.

    Args:
        ttl: Time to live in seconds (uses default if None)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(task: str, *args, **kwargs):
            # Try to get from cache
            cached_result = cache_manager.get(task)
            if cached_result:
                return cached_result

            # Execute function
            result = func(task, *args, **kwargs)

            # Cache result
            if ttl:
                old_ttl = cache_manager.ttl
                cache_manager.ttl = ttl
                cache_manager.set(task, result)
                cache_manager.ttl = old_ttl
            else:
                cache_manager.set(task, result)

            return result

        return wrapper

    return decorator
