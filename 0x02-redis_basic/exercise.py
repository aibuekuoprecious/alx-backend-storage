#!/usr/bin/env python3

"""
This module provides a Cache class for storing and retrieving data using Redis.
"""

import redis
from typing import Callable, Optional
from functools import wraps
import uuid

class Cache:
    """
    A class for caching data using Redis.
    """

    def __init__(self) -> None:
        """
        Initialize the Cache class.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def count_calls(self, method: Callable) -> Callable:
        """
        Decorator that counts the number of times a method is called.

        Args:
            method: The method to be decorated.

        Returns:
            The decorated method.
        """
        @wraps(method)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that increments the call count and calls the method.
            """
            key = method.__qualname__
            self._redis.incr(key)
            return method(*args, **kwargs)
        return wrapper

    def call_history(self, method: Callable) -> Callable:
        """
        Decorator that records the inputs and outputs of a method.

        Args:
            method: The method to be decorated.

        Returns:
            The decorated method.
        """
        @wraps(method)
        def wrapper(*args, **kwargs):
            """
            Wrapper function that records the inputs and outputs and calls the method.
            """
            inputs_key = "{}:inputs".format(method.__qualname__)
            outputs_key = "{}:outputs".format(method.__qualname__)
            self._redis.rpush(inputs_key, str(args))
            output = method(*args, **kwargs)
            self._redis.rpush(outputs_key, output)
            return output
        return wrapper

    @count_calls
    @call_history
    def store(self, value: str) -> str:
        """
        Store a value in the cache and return the key.

        Args:
            value: The value to be stored.

        Returns:
            The key associated with the stored value.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, value)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Optional[str]:
        """
        Retrieve a value from the cache by key.

        Args:
            key: The key of the value to be retrieved.
            fn: An optional function to transform the retrieved value.

        Returns:
            The retrieved value, or None if the key does not exist.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string value from the cache by key.

        Args:
            key: The key of the string value to be retrieved.

        Returns:
            The retrieved string value, or None if the key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer value from the cache by key.

        Args:
            key: The key of the integer value to be retrieved.

        Returns:
            The retrieved integer value, or None if the key does not exist.
        """
        return self.get(key, fn=int)

def replay(method: Callable) -> None:
    """
    Replay the history of a method's calls.

    Args:
        method: The method to replay the history for.
    """
    inputs_key = "{}:inputs".format(method.__qualname__)
    outputs_key = "{}:outputs".format(method.__qualname__)
    inputs = cache._redis.lrange(inputs_key, 0, -1)
    outputs = cache._redis.lrange(outputs_key, 0, -1)
    calls = len(inputs)
    print(f"{method.__qualname__} was called {calls} times:")
    for input_args, output in zip(inputs, outputs):
        input_args = eval(input_args.decode("utf-8"))
        print(f"{method.__qualname__}(*{input_args}) -> {output.decode('utf-8')}")
