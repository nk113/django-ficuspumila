# -*- coding: utf-8 -*-
import logging

from django.utils.translation import ugettext as _


logger = logging.getLogger(__name__)


class CoreException(Exception):

    def __init__(self, message, *args, **kwargs):
        self.errors = kwargs.get('errors', None)

        super(CoreException, self).__init__(message, *args, **kwargs)


class AuthException(CoreException):

    pass


class FixtureException(CoreException):

    pass


class ModelException(CoreException):

    pass


class ProxyException(CoreException):

    pass

