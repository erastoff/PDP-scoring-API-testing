import datetime
import functools
import hashlib
import subprocess
import time
import unittest
from unittest.mock import patch

import redis

import app.api as api
from app.scoring import get_score
from app.store import RedisStore


def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)

        return wrapper

    return decorator


class TestIntegrationSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}

        self.redis_process = subprocess.Popen(["redis-server", "--port", "6380"])
        time.sleep(2)

        self.redis_conn = redis.StrictRedis(host="localhost", port=6380)
        self.store = RedisStore(port=6380)

        self.redis_conn.flushall()

    def tearDown(self):
        self.redis_conn.flushall()
        self.redis_process.terminate()
        self.redis_process.wait()

    def get_response(self, request):
        return api.method_handler(
            {"body": request, "headers": self.headers}, self.context, self.store
        )

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512(
                bytes(
                    datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT,
                    "utf-8",
                )
            ).hexdigest()
        else:
            msg = request.get("account", "") + request.get("login", "") + api.SALT
            request["token"] = hashlib.sha512(bytes(msg, "utf-8")).hexdigest()

    @cases(
        [
            {
                "phone": "79175002040",
                "email": "erastov@otus.ru",
                "gender": 1,
                "birthday": "01.01.1990",
                "first_name": "Юрий",
                "last_name": "Ерастов",
            },
            {"phone": "79175002040", "email": "stupnikov@otus.ru"},
            {"phone": 79175002040, "email": "stupnikov@otus.ru"},
            {
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": "a",
                "last_name": "b",
            },
            {"gender": 0, "birthday": "01.01.2000"},
            {"gender": 2, "birthday": "01.01.2000"},
            {"first_name": "a", "last_name": "b"},
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": "a",
                "last_name": "b",
            },
        ]
    )
    def test_ok_score_request(self, arguments):
        request = {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "arguments": arguments,
        }
        self.set_valid_auth(request)

        key_parts = [
            arguments.get("first_name", None) or "",
            arguments.get("last_name", None) or "",
            str(arguments.get("phone", None)) or "",
            datetime.datetime.strptime(
                arguments.get("birthday", None), "%d.%m.%Y"
            ).strftime("%Y%m%d")
            if arguments.get("birthday", None) is not None
            else "",
        ]

        key = "uid:" + hashlib.md5(bytes("".join(key_parts), "utf-8")).hexdigest()
        value = get_score(self.store, **arguments)
        self.redis_conn.set(key, value)

        response, code = self.get_response(request)

        expected_response = {"score": value}
        self.assertEqual(response, expected_response)

    @cases(
        [
            {
                "client_ids": [1, 2, 3],
                "date": datetime.datetime.today().strftime("%d.%m.%Y"),
            },
            {"client_ids": [1, 2], "date": "19.07.2017"},
            {"client_ids": [0]},
        ]
    )
    def test_ok_interest_request(self, arguments):
        request = {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "clients_interests",
            "arguments": arguments,
        }
        self.set_valid_auth(request)

        expected_response = {}
        for i in arguments["client_ids"]:
            key = "i:" + str(i)
            value = str(["sport" + str(i), "misic" + str(i)])
            expected_response["client" + str(i)] = eval(value)
            self.redis_conn.set(key, value)

        response, code = self.get_response(request)

        self.assertEqual(response, expected_response)

    @cases(
        [
            {
                "client_ids": [1, 2, 3],
                "date": datetime.datetime.today().strftime("%d.%m.%Y"),
            },
            {"client_ids": [1, 2], "date": "19.07.2017"},
            {"client_ids": [0]},
        ]
    )
    def test_invalid_conn_interest_request(self, arguments):
        with patch.object(self.store, "get", side_effect=redis.ConnectionError):
            request = {
                "account": "horns&hoofs",
                "login": "h&f",
                "method": "clients_interests",
                "arguments": arguments,
            }
            self.set_valid_auth(request)

            response, code = self.get_response(request)

            self.assertEqual(code, 500)

    @cases(
        [
            {
                "phone": "79175002040",
                "email": "erastov@otus.ru",
                "gender": 1,
                "birthday": "01.01.1990",
                "first_name": "Юрий",
                "last_name": "Ерастов",
            },
            {"phone": "79175002040", "email": "stupnikov@otus.ru"},
            {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        ]
    )
    def test_invalid_conn_score_request(self, arguments):
        with patch.object(self.store, "get", side_effect=redis.ConnectionError):
            request = {
                "account": "horns&hoofs",
                "login": "h&f",
                "method": "online_score",
                "arguments": arguments,
            }
            self.set_valid_auth(request)

            response, code = self.get_response(request)

            self.assertEqual(code, 200)


if __name__ == "__main__":
    unittest.main()
