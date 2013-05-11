# -*- coding: utf-8 -*-
import dateutil
import django
import hashlib
import hmac
import logging
import os
import sys
import time
import urlparse

from datetime import datetime
from django.utils.importlib import import_module
from functools import wraps
from random import random, randrange

from ficuspumila.settings import (
    get as settings_get,
    ficuspumila as settings,
)

from .exceptions import RemotelyUncallableException


logger = logging.getLogger(__name__)


class Singleton(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)

        return cls._instance


# environment
def local_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if settings('API_URL'):
            raise RemotelyUncallableException(func.__name__)
        return func(*args, **kwargs)
    return wrapper


# django
def get_raw_post_data(request):
    if django.VERSION >= (1, 4):
        return request.body
    else:
        return request.raw_post_data


# locale
def get_default_language_code():
    return settings_get('LANGUAGE_CODE').split('-')[0].lower()

def get_default_currency_code():
    return 'JPY'


# date
def later_than(date, base=datetime.utcnow()):
    date = date if isinstance(date, datetime) else dateutil.parser.parse(date)
    base = base if isinstance(base, datetime) else dateutil.parser.parse(base)
    return base < date

def earlier_than(date, base=datetime.now()):
    return not later_than(date, base)


# module
def refresh(module):
    try:
        del(sys.modules[import_module(module).__name__])
    except:
        pass

# class
def extend(instance, new_class, attrs={}, replace_module=False):
    name = '%s_extended_with_%s' % (instance.__class__.__name__,
                                    new_class.__name__)
    module = instance.__module__
    if replace_module:
        name = new_class.__name__
        module = new_class.__module__

    instance.__class__ = type(name, 
                              (instance.__class__, new_class), 
                              attrs)
    instance.__class__.__module__ = module
    instance.__module__ = new_class.__module__
    return instance

def mixin(cls, mixin):
    if mixin not in cls.__bases__:
        cls.__bases__ = (mixin,) + cls.__bases__

def curtail(cls, mixedin):
    bases = list(cls.__bases__)
    for base in bases:
        if issubclass(base, mixedin):
            bases.remove(base)
    cls.__bases__ = tuple(bases)

def subclasses(module, cls):
    module = import_module(module)
    for name in dir(module):
        member = getattr(module, name)
        try:
            if member != cls and issubclass(member, cls):
                yield name, member
        except TypeError:
            pass


# random
def random(rate=1):
    return import_module('random').random() <= rate


# external command
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
                      str(randrange(0, 999)),
                      settings_get('SECRET_KEY', random())) if not key else str(key)
    text = '%s%s' % (str(time.time()),
                        str(randrange(0, 999))) if not text else text
    return hmac.new(key, text, hashlib.sha256).hexdigest()

def generate_file_hash_digest(location, blocksize=65536):
    sha1 = hashlib.sha1()
    with open(location, 'rb') as file:
        buf = file.read(blocksize)
        while len(buf) > 0:
            sha1.update(buf)
            buf = file.read(blocksize)
        return sha1.hexdigest()


# url
def parse_qs(query):
    return dict((k, v if len(v)>1 else v[0])
                for k, v in urlparse.parse_qs(query).iteritems())


# eval
def to_python(value):
    # simple values
    if value in ['true', 'True', True]:
        value = True
    elif value in ['false', 'False', False]:
        value = False
    elif value in ('nil', 'none', 'None', None):
        value = None
    return value

def from_python(value):
    # simple values
    if value is True:
        value = 'True'
    elif value is False:
        value = 'False'
    elif value is None:
        value = 'None'
    return value
