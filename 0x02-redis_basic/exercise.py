#!/usr/bin/env python3

from typing import Callable, Optional, Union
from uuid import uuid4
import redis
from functools import wraps

'''
    Writing strings to Redis.
'''


def count_calls(method: Callable) -> Callable:
    '''
        Decorator that counts the number of times a method is called.
    '''

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''
            Wrapper function that increments the call count and calls the method.
        '''
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs and outputs for a particular function.
    """
    key = method.__qualname__
    inputs = key + ":inputs"
    outputs = key + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):  # sourcery skip: avoid-builtin-shadow
        """
        Wrapper function that stores the inputs and outputs and calls the method.
        """
        self._redis.rpush(inputs, str(args))
        data = method(self, *args, **kwargs)
        self._redis.rpush(outputs, str(data))
        return data

    return wrapper


def replay(method: Callable) -> None:
    # sourcery skip: use-fstring-for-concatenation, use-fstring-for-formatting
    """
    Replays the history of a function
    Args:
        method: The function to be decorated
    Returns:
        None
    """
    name = method.__qualname__
    cache = redis.Redis()
    calls = cache.get(name).decode("utf-8")
    print("{} was called {} times:".format(name, calls))
    inputs = cache.lrange(name + ":inputs", 0, -1)
    outputs = cache.lrange(name + ":outputs", 0, -1)
    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(name, i.decode('utf-8'),
                                     o.decode('utf-8')))


class Cache:
    '''
    Cache class that interacts with Redis.
    '''

    def __init__(self):
        '''
        Initialize the cache by creating a Redis connection and flushing the database.
        '''
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''
        Store data in the cache with a random key and return the key.
        '''
        random_key = str(uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''
        Get data from the cache using the specified key.
        If a transformation function is provided, apply it to the retrieved value.
        '''
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> str:
        '''
        Get a string value from the cache using the specified key.
        '''
        value = self._redis.get(key)
        return value.decode('utf-8')

    def get_int(self, key: str) -> int:
        '''
        Get an integer value from the cache using the specified key.
        If the value cannot be converted to an integer, return 0.
        '''
        value = self._redis.get(key)
        try:
            value = int(value.decode('utf-8'))
        except Exception:
            value = 0
        return value
