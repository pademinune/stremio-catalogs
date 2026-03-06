
import redis
from dotenv import load_dotenv
import os
import json

load_dotenv()

REDIS_URL = str(os.getenv("REDIS_URL"))

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def get_cache(key):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached) #type: ignore
    return None

def set_cache(key: str, data: dict):
    redis_client.setex(key, 86400, json.dumps(data))


if __name__ == "__main__":

    keys = redis_client.keys("*")

    # set_cache("foo", {"foo": "yes"})
    print(get_cache("foo"))
    for key in keys: # type: ignore
        # val = redis_client.get(key)
        # print(val)
        # if key == b"name":
        #     print(type(json.loads(val)))
        print(key)
        # print(redis_client.get(key))

    # print(redis_client.get("flask_cache_drama_movies"))
    # redis_client.setex("name", 1000, json.dumps({"name": "justin"}))
