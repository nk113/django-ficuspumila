# -*- coding: utf-8 -*-                                                
import json
import logging
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.utils.importlib import import_module
from functools import wraps

from exceptions import (
    AuthenticatorInitializationException,
    InvalidHMACException,
    InvalidTokenException,
    TokenExpiredException,
    UnsupportedFormatException,
    UserNotFoundException,
)
from crypto import Transcoder
from utils import generate_hmac_digest

logger = logging.getLogger(__name__)


class SSOBackend(object):

    DELIMITER = '$'

    def authenticate(self, username=None, password=None):
        try:
            service, id = username.split(DELIMITER)
            kwargs = {
                service: id,
                SSOAuthenticator.TOKEN_PARAM: password,
            }
            user = SSOAuthenticator(**kwargs).user.user
        except Exception, e:
            logger.exception(u'failed to authenticate user: %s, %s' % (username,
                                                                       password,))

            user = None
        return user


class SSOAuthenticator(object):
    '''
    Expects decrypted SSO token to contain following parameters:

    {
      expiration: <timestamp, now + settings.SSO_TOKEN_EXPIRATION>,
      <service>_<user>_id: <service user id>,
      (hmac: <hmac for data>,)
    }
    '''
    def __init__(self, *args, **kwargs):

        def get_name(path):
            return path.split('.').pop().lower()

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

            # instantiate service
            self.service = [s[1]['service'].objects.get(
                               pk=int(kwargs.get(k)))
                               for s in [(get_name(k),
                                          v,) for k, v in services.iteritems()]
                               if kwargs.get(s[0])][0]

            # validate token
            self.token = self.validate_token(kwargs.get('token', None),
                                             kwargs.get('format', None),
                                             kwargs.get('data', None))


            # detect user
            self.user = [s[1]['user'].objects.get(**{
                               '%s' % s[0]: self.service,
                               '%s' % s[2]: self.token.get(s[2]),
                               })
                               for s in [(get_name(k),
                                          v,
                                          '%s_%s_id' % (get_name(k),
                                                        v['user'].__name__.lower(),))
                                          for k, v in services.iteritems()]
                               if kwargs.get(s[0])][0]

        except InvalidHMACException, e:
            logger.exception(u'invalid HMAC detected')

        except InvalidTokenException, e:
            logger.exception(u'invalid token is given: %s' % kwargs.get(self.TOKEN_PARAM, None))

        except TokenExpiredException, e:
            logger.exception(u'token is expired')           

        except UserNotFoundException, e:
            logger.exception(u'could not identify user')

        except Exception, e:
            if getattr(self, 'service', None) is None:
                logger.exception(u'failed to initialize authenticator: %s' % e)

                raise AuthenticatorInitializationException()

    def validate_token(self, token, format='json', data=None):
        if token is None or getattr(self, 'service', None) is None:
            raise InvalidSSOTokenException()

        logger.debug(u'token: %s' % token)

        try:
            decrypted = Transcoder(
                            key=self.service.token_key,
                            iv=self.service.token_iv
                        ).algorithm.decrypt(token)
            if format == 'json':
                token = json.loads(decrypted)
            else:
                raise UnsupportedFormatException()

        except UnsupportedFormatException, e:
            raise e

        except Exception, e:
            logger.exception(u'failed to validate token: %s' % e)

            raise InvalidSSOTokenException()

        logger.debug(u'token decrypted: %s' % token)

        if token.get('expiration'):
            if float(token['expiration']) > time.time() + settings.TOKEN_EXPIRATION:
                logger.debug(u'token expiration is bigger than expected: token %s > %s' % (
                                 token['expiration'],
                                 timezone.now() + settings.TOKEN_EXPIRATION,))

                raise InvalidSSOTokenException()
        
            if float(token['expiration']) < time.time():
                logger.debug(u'token is expired: token %s < %s')

                raise TokenExpiredException()
        else:
            raise InvalidSSOTokenException()

        if data:
            if (token.get('hmac') and
               generate_hmac_digest(self.service.hmac_key, data)) != token['hmac']:
                raise InvalidHMACException
            else:
                raise InvalidSSOTokenException()

        return token

    def is_authenticated(self):
        return True if getattr(self, 'user', False) else False

    @staticmethod
    def from_request(request):
        instance = SSOAuthenticator(
        )

        if instance.is_authenticated():
            request.user = instance.user.user

        return instance

