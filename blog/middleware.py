from blog.utils import get_redis_connection


class RedisVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = get_redis_connection()

    def __call__(self, request):
        response = self.get_response(request)

        # GET requests to posts
        if request.method == "GET" and request.resolver_match:
            if request.resolver_match.view_name == "post-detail":
                pk = request.resolver_match.kwargs.get("pk")
                if pk:
                    self.redis.incr(f"post:{pk}:visits")

        return response
