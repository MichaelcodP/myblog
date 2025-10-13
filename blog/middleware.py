import logging
from django.utils.deprecation import MiddlewareMixin
from blog.utils import get_redis_connection

logger = logging.getLogger(__name__)


class RedisVisitMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        try:
            self.redis = get_redis_connection()
        except Exception as e:
            # Log connection failure but keep middleware functional
            logger.error(
                f"Failed to connect to Redis in middleware initialization: {e}"
            )
            self.redis = (
                None  # Redis may be unavailable, but the server should not go down
            )

    def __call__(self, request):
        response = self.get_response(request)

        if (
            request.method == "GET"
            and request.resolver_match
            and request.resolver_match.view_name == "post-detail"
            and response.status_code == 200
        ):
            pk = request.resolver_match.kwargs.get("pk")
            if pk and self.redis:
                try:
                    self.redis.incr(f"post:{pk}:visits")
                except Exception as e:
                    logger.error(f"Redis increment failed for post {pk}: {e}")

        return response
