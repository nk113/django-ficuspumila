# -*- coding: utf-8 -*-
import dateutil
import hashlib
import hmac
import logging
import os
import random
import time

from datetime import datetime
from django.conf import settings
from django.utils.importlib import import_module


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

# file path
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

