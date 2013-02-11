# -*- coding: utf-8 -*-
import dateutil
import hashlib
import logging
import os
import random

from datetime import datetime
from django.conf import settings
from django.core.cache import cache as djcache
from functools import wraps


logger = logging.getLogger(__name__)


# locale
def get_default_language_code():
    return settings.LANGUAGE_CODE.split('-')[0].lower()

def get_default_currency_code():
    return 'JPY'

# date
def later_than(date, base=datetime.utcnow()):
    date = date if isinstance(date, datetime) else dateutil.parser.parse(date)
    base = base if isinstance(base, datetime) else dateutil.parser.parse(base)
    return base < date

def earlier_than(date, base=datetime.now()):
    return not later_than(date, base)

# path
def whereis(command):
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, command)) and \
           not os.path.isdir(os.path.join(path, command)):
            return os.path.join(path, command)
    return None

# string
def bit2hex(bit_value):
    return hex(int('%s' % bit_value, 2))[2:].replace('L', '')

def hex2bit(hex_value):
    return format(int(hex_value, 16), 'b')

def generate_hmac_digest(key=None, text=None):
    key = '%s%s%s' % (str(time.time()),
                      str(random.randrange(0, 999)),
                      settings.SECRET_KEY) if not key else str(key)
    text = '%s%s' % (str(time.time()),
                        str(random.randrange(0, 999))) if not text else text
    return hmac.new(key, text, hashlib.sha256).hexdigest()

def generate_file_hash_digest(location, blocksize=65536):
    sha1 = hashlib.sha1()
    file = open(location, 'rb')
    buf = file.read(blocksize)
    while len(buf) > 0:
        sha1.update(buf)
        buf = file.read(blocksize)
    return sha1.hexdigest()

# cache
def cache(**decorator_kwargs):

    def decorator(func):
        def wrapper(*args, **kwargs):
            keyargs = decorator_kwargs.get('keyargs', [])
            keyarg  = decorator_kwargs.get('keyarg', None)

            if keyarg:
                keyargs.append(keyarg)

            keys = ['%s-' % kwargs.get(keyarg) if kwargs.get(keyarg, None) else '' for keyarg in keyargs]
            key = ''.join(keys)[:-1]

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

    logger.debug('setting cache: %s = %s' % (key, value,))

    djcache.set(hash, value, timeout)
    return value

