import redis


def get_redis_connection():
    return redis.Redis(host="localhost", post=6379, db=0, decode_responses=True)
