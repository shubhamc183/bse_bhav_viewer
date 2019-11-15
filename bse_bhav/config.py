'''
Created on Nov 9, 2019

@author: sch
'''

import os
import logging

import redis


def get_redis_connection():
    """
    Return a redis connection
    """
    try:
        redis_connection = redis.from_url(os.environ.get("REDIS_URL"), charset="utf-8",
                                          decode_responses=True, db=0)
        redis_connection.ping()
        return redis_connection
    except redis.exceptions.ConnectionError as exception:
        logging.exception(exception)
    return None
