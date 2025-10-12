# blog/utils.py
import redis
from django.conf import settings

_pool = None


def get_redis_connection():
    """Returns a Redis client that uses a single shared connection pool."""
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
            decode_responses=True,
        )
    return redis.Redis(connection_pool=_pool)
