# -*- coding: utf-8 -*-                                                
import logging

from django.utils.translation import ugettext as _

from .sso import Authenticator


logger = logging.getLogger(__name__)


class SSO(object):

    DELIMITER = '$'

    supports_inactive_user = False; 

    def authenticate(self, username=None, password=None):
        logger.debug(u'trying to authenticate with SSO (%s / %s)' % (username,
                                                                     password,))
        try:
            service, id = username.split(SSO.DELIMITER)
            user = Authenticator(**{
                service: int(id),
                Authenticator.TOKEN_PARAM: password,
            }).user.user
        except Exception, e:
            logger.exception(u'failed to authenticate user: %s, %s' % (username,
                                                                       password,))

            user = None
        return user
