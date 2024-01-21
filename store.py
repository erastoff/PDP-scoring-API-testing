import logging
import time

import redis


class RedisStore:
    """
    Redis storage is implemented by this class.
    """

    def __init__(self, host="localhost", port=6379, max_retries=3, timeout=2):
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.timeout = timeout
        self.connection = None

    def connect(self):
        return redis.StrictRedis(host=self.host, port=self.port)

    def get(self, key):
        """
        Method to obtain client_interest from persistent cache
        """
        for _ in range(self.max_retries):
            try:
                if not self.connection:
                    self.connection = self.connect()
                return self.connection.get(key)
            except redis.ConnectionError:
                time.sleep(self.timeout)
        raise Exception("Failed to connect to Redis after multiple retries.")

    def cache_get(self, key):
        """
        Method to obtain online_score from cache
        """
        try:
            res = self.get(key)
        except Exception:
            logging.exception("Could't connect to redis server to read value")
            return None
        return res

    def cache_set(self, key, value, timeout=5):
        """
        Method to set up value
        """
        for _ in range(self.max_retries):
            try:
                if not self.connection:
                    self.connection = self.connect()
                self.connection.setex(key, timeout, value)
                return
            except redis.ConnectionError:
                time.sleep(self.timeout)
        raise Exception("Failed to connect to Redis after multiple retries.")
