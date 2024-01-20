import redis
import json
import time

# r = redis.Redis(host="localhost", port=6379, decode_responses=True)
# # Создайте объект соединения с Redis
# # r = redis.StrictRedis(host="localhost", port=6379)
# # Примеры операций
# r.set("foo", "bar")
# # True
# r.get("foo")
# print(r.get("foo"))
# # bar


class RedisStore:
    def __init__(self, host="localhost", port=6379, max_retries=3, timeout=5):
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.timeout = timeout
        self.connection = None

    def connect(self):
        return redis.StrictRedis(host=self.host, port=self.port)

    def get(self, key):
        for _ in range(self.max_retries):
            try:
                if not self.connection:
                    self.connection = self.connect()
                return self.connection.get(key)
            except redis.ConnectionError:
                time.sleep(self.timeout)
        raise Exception("Failed to connect to Redis after multiple retries.")

    def cache_get(self, key):
        # Assuming cache storage and key-value storage are the same in this example
        return self.get(key)

    def cache_set(self, key, value, timeout=5):
        for _ in range(self.max_retries):
            try:
                if not self.connection:
                    self.connection = self.connect()
                self.connection.setex(key, timeout, value)
                return
            except redis.ConnectionError:
                time.sleep(self.timeout)
        raise Exception("Failed to connect to Redis after multiple retries.")


# store = RedisStore(host="localhost")
# store.cache_set("foo", bytes({"a": "b"}))
# print(store.cache_get("foo"))
# print(store.cache_get("far"))
# score = get_score(store, phone="123456789", email="example@example.com")
# interests = get_interests(store, cid="your_customer_id")
