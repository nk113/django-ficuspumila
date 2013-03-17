# -*- coding: utf-8 -*-
import hashlib
import logging
import sys

from django.conf import settings
from django.core.cache import cache as djcache
from functools import wraps


TIMEOUT = settings.CACHE_TIMEOUT

logger = logging.getLogger(__name__)


def _generate_key(key, **kwargs):
    return hashlib.sha1(key).hexdigest()

def set(key, value, expiration=TIMEOUT, **kwargs):
    logger.debug(u'setting cache (%s -> %s)' % (key, value,))

    return djcache.set(_generate_key(key, **kwargs), value, expiration)

def add(key, value, expiration=TIMEOUT, **kwargs):
    logger.debug(u'adding cache (%s -> %s)' % (key, value,))

    return djcache.add(_generate_key(key, **kwargs), value, expiration)

def get(key, default=None, **kwargs):
    value = djcache.get(_generate_key(key, **kwargs))

    if value is None:
        logger.debug(u'not in cache (%s)' % key)
        return default

    logger.debug(u'found in cache (%s)' % key)
    return value        


def delete(key, **kwargs):
    logger.debug(u'deleting cache (%s)' % key)

    return djcache.delete(_generate_key(key, **kwargs))

def get_or_set(key, value=None, expiration=TIMEOUT, **kwargs):
    cached = get(key)

    if cached:
        return cached

    if value:
        value = value() if hasattr(value, '__call__') else value
    else:
        return None

    set(key, value, expiration, **kwargs)
    return value

def cache(**decorator_kwargs):

    def decorator(func):
        def wrapper(*args, **kwargs):
            keyargs  = decorator_kwargs.get('keyargs', [])
            keyarg   = decorator_kwargs.get('keyarg', None)
            breakson = decorator_kwargs.get('breakson', None)
            nocacheonbreak = decorator_kwargs.get('nocacheonbreak', False)
            donothing = False

            if keyarg is not None:
                keyargs.append(keyarg)

            keys = []
            for keyarg in keyargs:
                if isinstance(keyarg, int):
                    try:
                        keys.append('' if args[keyarg] is None else args[keyarg])
                    except:
                        pass
                if isinstance(keyarg, str):
                    keys.append('%s' % kwargs.get(keyarg) if kwargs.get(keyarg, None) else '')
            key = '-'.join(keys)

            donothing = len(key) < 1

            key = '%s:%s:%s' % (func.func_globals.get('__name__', ''),
                                func.func_name,
                                key,)

            if (breakson is not None and
                (breakson is True or
                 (hasattr(breakson, '__call__') and
                  breakson(*args, **kwargs)))):

                logger.debug(u'needs to refresh cache, deleting cahce (%s)' % key)
                delete(key)

                donothing = nocacheonbreak

            if donothing:
                return func(*args, **kwargs) 

            value = get_or_set(key)

            if value:
                return value

            return get_or_set(key,
                              func(*args, **kwargs),
                              decorator_kwargs.get('timeout', TIMEOUT))
        return wraps(func)(wrapper)

    return decorator
