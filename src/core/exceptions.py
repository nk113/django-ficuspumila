# -*- coding: utf-8 -*-                
from django.utils.translation import ugettext as _


class CoreException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.errors = kwargs.get('errors', None)

        super(CoreException, self).__init__(message, *arg, **kwargs)


class SSOAuthenticatorInitializationException(CoreException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self,
                           _(u'Failed to instantiate SSOAuthenticator, ' +
                             u'could not identify service or find ' +
                             u'required parameters.'))


class InvalidSSOTokenException(CoreException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self,
                           _(u'Invalid SSO token detected.'))


class InvalidHMACException(CoreException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self,
                           _(u'Invalid HMAC detacted'))


class SSOTokenExpiredException(CoreException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self,
                           _(u'SSO token has expired.'))


class SSOTokenUserNotFoundException(CoreException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self,
                           _(u'Could not identify user.'))


class SSOTokenGenerationFailureException(CoreException):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self,
                           _(u'Failed to generate SSO token.'))

