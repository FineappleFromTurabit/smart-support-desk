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
    redis_client.setex(key, ttl, json.dumps(value))  # used to set a string value for a specific key along with a timeout (expiration time) in seconds, all in a single, atomic operation.

def delete_cached(key):
    redis_client.delete(key)