# -*- coding: utf-8 -*-
import logging
import os

from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from django.utils.importlib import import_module


logger = logging.getLogger(__name__)


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
        key = os.urandom(32)
        if self.hex: key = hexlify(key)
        return key

    def generate_iv(self):
        iv = os.urandom(AES.block_size)
        if self.hex: iv = hexlify(iv)
        return iv

    def encrypt(self, text):
        try:
            encrypted = AES.new(self.key,
                                AES.MODE_CBC,
                                self.iv).encrypt(self.add_padding(AES.block_size,
                                                                  text))
            if self.hex:
                return hexlify(encrypted)
            else:
                return encrypted
        except Exception, e:
            logger.exception('failed to encrypt (%s)' % e)
            raise e

    def decrypt(self, encrypted):
        try:
            if self.hex:
                encrypted = unhexlify(encrypted)

            return self.remove_padding(AES.block_size,
                                       (AES.new(self.key,
                                                AES.MODE_CBC,
                                                self.iv).decrypt(encrypted)))
        except Exception, e:
            logger.exception('failed to decrypt (%s)' % e)
            raise e

    def nr_pad_bytes(self, blocksize, size):
        '''
        Returns number of required pad bytes for block of size.
        '''
        if not (0 < blocksize < 255):
            raise Exception('Blocksize must be between 0 and 255.')
        return blocksize - (size % blocksize)

    def add_padding(self, blocksize, s):
        '''
        Adds rfc 1423 padding to string.

        RFC 1423 algorithm adds 1 up to blocksize padding bytes to string s. Each 
        padding byte contains the number of padding bytes.
        '''
        n = self.nr_pad_bytes(blocksize, len(s))
        return s + (chr(n) * n)

    def remove_padding(self, blocksize, s):
        '''
        Removes rfc 1423 padding from string.
        '''
        # last byte contains number of padding bytes
        n = ord(s[-1])
        if n > blocksize or n > len(s):
            raise Exception('Invalid padding.')
        return s[:-n]
