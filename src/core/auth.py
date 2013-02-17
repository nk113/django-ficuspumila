# -*- coding: utf-8 -*-                                                
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.utils.importlib import import_module
from functools import wraps

from crypto import Transcoder
from exceptions import (
    SSOAuthenticatorInitializationException,
    InvalidSSOTokenException,
    InvalidHMACException,
    SSOTokenExpiredException,
    SSOTokenUserNotFoundException,
)


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
      (hmac: <hmac for data>,)
      (username: <useranme of Django User>,)
      (password: <passward of Dajngo User>,)
      (<service>_<user>_id: service user id)
    }
    '''
    TOKEN_PARAM = 'token'
    FORMAT_PARAM = 'format'

    def __init__(self, *args, **kwargs):
        try:
            self._authenticated = False

            # import modules
            services = {}
            for k, v in settings.SSO_SERVICES.iteritems():
                service = v['service'].split('.')
                user = v['user'].split('.')
                services[k] = {
                    'service': getattr(import_module('.'.join(service[:-1])),
                                                     service.pop().title()),
                    'user'   : getattr(import_module('.'.join(user[:-1])),
                                                     user.pop().title()),
                }

            # instantiate service
            self.service = [s[1]['service'].objects.get(
                               pk=int(kwargs.get(s[1]['service'].__name__.lower())))
                               for s in [(k, v,) for k, v in services.iteritems()]
                               if kwargs.get(s[0])][0]

            # validate token
            self.token = self.validate_token(kwargs.get(self.TOKEN_PARAM, None))

            # detect user
            self.user    = [s[1]['user'].objects.get(**{
                                   '%s' % s[0]: self.service,
                                   '%s' % s[2]: token.get(s[2]),
                               })
                               for s in [(k, v,
                                          '%s_%s_id' % (v['service'].__name__.lower(),
                                                        v['user'].__name__.lower(),))
                                          for k, v in services.iteritems()]
                               if kwargs.get(s[0])][0]

        except InvalidSSOTokenException, e:
            logger.exception(u'invalid token is given: %s' % kwargs.get(self.TOKEN_PARAM, None))
        except SSOTokenExpiredException, e:
            logger.exception(u'token is expired')           
        except SSOTokenUserNotFoundException, e:
            logger.exception(u'could not identify user')
        except InvalidHMACException, e:
            logger.exception(u'invalid HMAC detected')
        except Exception:
            if getattr(self, 'service', None) is None:
                logger.exception(u'failed to initialize authenticator: %s' % e)

                raise SSOAuthenticatorInitializationException()

    def validate_token(self, token):
        return {'source_owner_id': 'owner'}

    def is_authenticated(self):
        return self._authenticated

    @staticmethod
    def from_request(request):
        return SSOAuthenticator(
        )
