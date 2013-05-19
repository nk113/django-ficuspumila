# -*- coding: utf-8 -*-
import logging
import requests

from ficuspumila.core import proxies
from ficuspumila.core.cache import cache
from ficuspumila.core.exceptions import ProxyException
from ficuspumila.settings import ficuspumila as settings


logger = logging.getLogger(__name__)


class Country(proxies.Proxy):

    @classmethod
    @cache(keyarg=1)
    def query_country_code(cls, ip):

        if settings('IPINFODB_API_KEY') is None:
            raise ProxyException(u'"IPINFODB_API_KEY" is not defiend in settings.')

        try:
            response = requests.get(settings('IPINFODB_API_URL'),
                                    params={'key': settings('IPINFODB_API_KEY'),
                                            'ip': ip,
                                            'format': 'json'})

            if response.status_code == 200:
                logger.debug(u'api response (%s -> HTTP %s: %s)' % (
                                 ip,
                                 response.status_code,
                                 response.json(),))

                return response.json()['countryCode']
        except Exception, e:
            pass

        logger.exception(u'failed to retrieve country (%s -> HTTP %s: %s: %s)' % (
                             ip,
                             response.status_code,
                             response.text,
                             e if 'e' in locals() else None,))

        return None

    @classmethod
    def get_by_ip(cls, ip):
        return Country.objects.get(alpha2=cls.query_country_code(ip))
