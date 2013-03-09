# -*- coding: utf-8 -*-                                                
import json
import logging
import time

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.utils.importlib import import_module
from django.utils.translation import ugettext as _
from functools import wraps

from crypto import Transcoder
from exceptions import AuthException
from utils import generate_hmac_digest


logger = logging.getLogger(__name__)


class SSOBackend(object):

    DELIMITER = '$'

    supports_inactive_user = False; 

    def authenticate(self, username=None, password=None):
        logger.debug('trying to authenticate with sso: %s / %s' % (username,
                                                                   password,))
        try:
            service, id = username.split(DELIMITER)
            user = SSOAuthenticator(**{
                service: int(id),
                SSOAuthenticator.TOKEN_PARAM: password,
            }).user.user
        except Exception, e:
            logger.exception(u'failed to authenticate user: %s, %s' % (username,
                                                                       password,))

            user = None
        return user


class SSOAuthenticator(object):
    """
    Expects decrypted SSO token to contain following parameters:

    format: json
      [
        <timestamp, now + settings.TOKEN_TIMEOUT>
        (, {
          ("<service>_<user>_id": "<service user id>")
          (, "username": "<Django Auth username>")
          (, "password": "<Django Auth password>")
          (, "hmac": "<hmac for data>")
        } )
      ]
    """
    AUTH_TYPE = 'sso'

    TOKEN_PARAM = 'token'
    FORMAT_PARAM = 'format'
    DATA_PARAM = 'data'

    service = None
    token = None
    user = None

    def __init__(self, **kwargs):

        def get_name(path):
            return path.rpartition('.').lower()

        logger.debug('trying to initialize: %s' % kwargs,)

        try:
            # import modules
            services = {}
            for k, v in settings.SERVICES.iteritems():
                service = k.split('.')
                user = v['user'].split('.')
                services[get_name(k)] = {
                    'service': getattr(import_module('.'.join(service[:-1])),
                                                     service.pop().title()),
                    'user'   : getattr(import_module('.'.join(user[:-1])),
                                                     user.pop().title()),
                }

            logger.debug('installed services: %s' % services)

            # instantiate service
            self.service = [s[1]['service'].objects.get(
                         pk=int(kwargs.get(k)))
                         for s in [(get_name(k),
                                    v,) for k, v in services.iteritems()]
                         if kwargs.get(s[0])][0]

            # validate token
            self.token = self.validate_token(
                         self.service,
                         kwargs.get(SSOAuthenticator.TOKEN_PARAM, None),
                         kwargs.get(SSOAuthenticator.FORMAT_PARAM, None),
                         kwargs.get(SSOAuthenticator.DATA_PARAM, None))

            if self.token.get('username'):
                # TODO: detect service user from django user
                pass
            else:
                # detect service user from params
                self.user = self.user if self.user else [s[1]['user'].objects.get(**{
                                '%s' % s[0]: self.service,
                                '%s' % s[2]: self.token.get(s[2]),
                            })
                            for s in [(get_name(k),
                                v,
                                '%s_%s_id' % (get_name(k),
                                v['user'].__name__.lower(),))
                            for k, v in services.iteritems()]
                            if kwargs.get(s[0])][0]

        except IndexError, e:
            logger.exception(u'service or user not found in params')

        except AuthException, e:
            logger.exception(e)

        except Exception, e:
            if getattr(self, 'service', None) is None:
                logger.exception(u'failed to initialize authenticator: %s' % e)

                raise AuthException(e)

    def validate_token(self, service, token, format='json', data=None):
        if service is None:
            raise AuthException(_(u'Service not found.'))
        if token is None:
            raise AuthException(_(u'Token not found.'))

        logger.debug(u'token: %s' % token)

        try:
            decrypted = service.decrypt_token(token)
            if format == 'json':
                token = json.loads(decrypted)
            else:
                raise AuthException(_(u'Format not supported.'))

        except AuthException, e:
            raise e

        except Exception, e:
            logger.exception(u'failed to validate token: %s' % e)

            raise AuthException(_(u'Invalid token detected.'))

        logger.debug(u'token decrypted: %s' % token)

        if token[0]:
            if float(token[0]) > time.time() + settings.TOKEN_TIMEOUT:
                logger.debug(u'token expiration is bigger than expected: token %s > %s' % (
                                 token[0],
                                 timezone.now() + settings.TOKEN_TIMEOUT,))

                raise AuthException(_(u'Expiration specified in token is '
                                      u'bigger than expected.'))
        
            if float(token[0]) < time.time():
                logger.debug(u'token is expired: token %s < %s')

                raise AuthException(_(u'Token expired.'))
        else:
            raise AuthException(_(u'Invalid token detected.'))

        token = token[1] if len(token) > 0 else {}

        if data:
            if (token.get('hmac') and
               generate_hmac_digest(service.hmac_key, data)) != token.get('hmac'):
                raise AuthException(_(u'Invalid HMAC detected.'))
            else: 
                raise AuthException(_(u'HMAC not found.'))

        if token.get('username') and token.get('password'):
            user = authenticate(username=token.get('username'),
                                password=token.get('password'))

        return token

    def is_authenticated(self):
        return True if getattr(self, 'user', False) else False

    @staticmethod
    def from_request(request):
        if (request.META.get('HTTP_AUTHORIZATION') and
            request.META['HTTP_AUTHORIZATION'].lower().startswith(
                '%s ' % SSOAuthenticator.AUTH_TYPE)):
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

            if auth_type.lower() != SSOAuthenticator.AUTH_TYPE:
                raise ValueError(u'Incorrect authorization header')
            
            service, id, token = data.split(':', 2)
            kwargs = {
                service: id,
                SSOAuthenticator.TOKEN_PARAM: token,
            }
            authenticator = SSOAuthenticator(**kwargs).is_authenticated()
        else:
            kwargs = request.GET.copy()
            kwargs.update(request.POST.copy())
            kwargs.update(request.COOKIES.copy())
            kwargs['data'] = request.body
            authenticator = SSOAuthenticator(**kwargs)

        if authenticator.is_authenticated():
            request.user = authenticator.user.user

        return authenticator
