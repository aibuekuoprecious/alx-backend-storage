import redis
from typing import Callable, Optional
from functools import wraps

class Cache:
    def __init__(self):
        self.redis_client = redis.Redis()

    def count_calls(self, method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            key = method.__qualname__
            self.redis_client.incr(key)
            return method(*args, **kwargs)
        return wrapper

    def call_history(self, method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            inputs_key = "{}:inputs".format(method.__qualname__)
            outputs_key = "{}:outputs".format(method.__qualname__)
            self.redis_client.rpush(inputs_key, str(args))
            output = method(*args, **kwargs)
            self.redis_client.rpush(outputs_key, output)
            return output
        return wrapper

    @count_calls
    @call_history
    def store(self, value):
        key = self.redis_client.incr("key_counter")
        self.redis_client.set(key, value)
        return key

    def get(self, key: str, fn: Optional[Callable] = None):
        value = self.redis_client.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str):
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str):
        return self.get(key, fn=int)

def replay(method: Callable):
    inputs_key = "{}:inputs".format(method.__qualname__)
    outputs_key = "{}:outputs".format(method.__qualname__)
    inputs = cache.redis_client.lrange(inputs_key, 0, -1)
    outputs = cache.redis_client.lrange(outputs_key, 0, -1)
    calls = len(inputs)
    print(f"{method.__qualname__} was called {calls} times:")
    for input_args, output in zip(inputs, outputs):
        input_args = eval(input_args.decode("utf-8"))
        print(f"{method.__qualname__}(*{input_args}) -> {output.decode('utf-8')}")
