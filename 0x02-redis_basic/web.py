#!/usr/bin/env python3
""" Redis Module """

from functools import wraps
import redis
import requests
from typing import Callable

redis_client = redis.Redis()


def count_requests(func: Callable) -> Callable:
    """ Decorator for counting requests """
    @wraps(func)
    def wrapper(url):  
        """ Wrapper function for counting requests """
        redis_client.incr(f"count:{url}")
        cached_html = redis_client.get(f"cached:{url}")
        if cached_html:
            return cached_html.decode('utf-8')
        html = func(url)
        redis_client.setex(f"cached:{url}", 10, html)
        return html

    return wrapper


@count_requests
def get_page(url: str) -> str:
    """ Retrieve the HTML content of a URL """
    response = requests.get(url)
    return response.text
