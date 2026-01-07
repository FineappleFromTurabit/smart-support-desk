import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

def get_cached(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cached(key, value, ttl=60):
    redis_client.setex(key, ttl, json.dumps(value))

def delete_cached(key):
    redis_client.delete(key)


