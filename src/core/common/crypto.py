# -*- coding: utf-8 -*-
from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from django.utils.importlib import import_module

from lib import crypto


ALGORITHMS = ('AES',)


class Transcoder(object):

    def __init__(self, *args, **kwargs):
        self.algorithm = kwargs.get('algorithm', 'AES')

        if self.algorithm in ALGORITHMS:
            self.algorithm = getattr(import_module(self.__module__),
                                     '_%s' % self.algorithm)(*args, **kwargs)
        else:
            raise NotImplementedError()



class _AES(object):

    def __init__(self, *args, **kwargs):
        self.key = kwargs.get('key', None)
        self.iv = kwargs.get('iv', None)
        self.hex = kwargs.get('hex', True)

        if not self.key or not self.iv:
            self.key = self.generate_key()
            self.iv = self.generate_iv()

        if self.hex:
            self.key = unhexlify(self.key)
            self.iv = unhexlify(self.iv)

    def __str__(self):
        return 'AES'

    def generate_key(self):
        key = crypto.pool.get_bytes(32)
        if self.hex: key = hexlify(key)
        return key

    def generate_iv(self):
        iv = crypto.pool.get_bytes(AES.block_size)
        if self.hex: iv = hexlify(iv)
        return iv

    def encrypt(self, text):
        encrypted = AES.new(self.key,
                            AES.MODE_CBC,
                            self.iv).encrypt(crypto.appendPadding(AES.block_size,
                                                                  text))

        if self.hex:
            return hexlify(encrypted)
        else:
            return encrypted

    def decrypt(self, encrypted):
        if self.hex:
            encrypted = unhexlify(encrypted)

            return crypto.removePadding(AES.block_size,
                                        (AES.new(self.key,
                                                 AES.MODE_CBC,
                                                 self.iv).decrypt(encrypted)))
