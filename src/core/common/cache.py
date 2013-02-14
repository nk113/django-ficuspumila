# -*- coding: utf-8 -*-
import hashlib
import logging
import sys

from django.core.cache import cache as djcache
from functools import wraps


logger = logging.getLogger(__name__)


def cache(**decorator_kwargs):

    def decorator(func):
        def wrapper(*args, **kwargs):
            keyargs = decorator_kwargs.get('keyargs', [])
            keyarg  = decorator_kwargs.get('keyarg', None)

            if keyarg:
                keyargs.append(keyarg)

            keys = []
            for keyarg in keyargs:
                if isinstance(keyarg, int):
                    try:
                        keys.append(args[keyarg])
                    except:
                        pass
                if isinstance(keyarg, str):
                    keys.append('%s' % kwargs.get(keyarg) if kwargs.get(keyarg, None) else '')
            key = '-'.join(keys)

            if len(key) < 1:
                return func(*args, **kwargs)

            key = '%s:%s:%s' % (func.func_globals.get('__name__', ''),
                                func.func_name,
                                key,)
            value = get_or_set_cache(key, prefix=False)

            if value:
                return value

            return get_or_set_cache(key,
                                    func(*args, **kwargs),
                                    decorator_kwargs.get('timeout', 60*15),
                                    prefix=False)
        return wraps(func)(wrapper)

    return decorator

def get_or_set_cache(key, value=None, timeout=60*15, **kwargs):
    if kwargs.get('prefix', True):
        frame = sys._getframe(1)
        lineno = kwargs.get('lineno', False)
        lineno = frame.f_lineno if lineno is True else lineno
        key = '%s%s:%s' % (frame.f_globals.get('__name__', ''),
                           ':%s' % lineno if lineno else '', key,)

    logger.debug('cache: %s' % key)

    hash = hashlib.sha1(key).hexdigest()
    stored = djcache.get(hash)

    if stored is not None:

        logger.debug('found in cache: %s' % key)

        return stored

    if value:
        value = value() if hasattr(value, '__call__') else value
    else:
        return None

    logger.debug('setting cache: %s = %s' % (key, value[:255],))

    djcache.set(hash, value, timeout)
    return value

