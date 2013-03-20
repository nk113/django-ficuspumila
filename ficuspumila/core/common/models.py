# -*- coding: utf-8 -*-
import logging
import requests

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import Choice, CSVField, Model
from core.cache import cache


logger = logging.getLogger(__name__)


class Country(Model):

    class Meta:

        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')

    class Continents(Choice):

        ANTARCTICA     = 'AN'
        ASIA           = 'AS'
        EUROPE         = 'EU'
        NOURTH_AMERICA = 'NA'
        OCEANIA        = 'OC'
        SOURTH_AMERICA = 'SA'

    alpha2 = models.CharField(max_length=2,
                         primary_key=True,
                         verbose_name=_(u'ISO 3166-1 alpha-2 code'))
    alpha3 = models.CharField(max_length=3,
                         unique=True,
                         verbose_name=_(u'ISO 3166-1 alpha-3 code'))
    numeric3 = models.CharField(max_length=3,
                         unique=True,
                         verbose_name=_(u'ISO 3166-1 numeric code'))
    fips = models.CharField(max_length=2,
                         blank=True)
    name = models.CharField(max_length=128)
    capital = models.CharField(max_length=128)
    area = models.IntegerField(null=True,
                         verbose_name=_(u'Area (in sq km)'))
    population = models.IntegerField(null=True)
    continent = models.CharField(max_length=2,
                         choices=Continents)
    tld = models.CharField(max_length=5,
                         blank=True,
                         verbose_name=_(u'Top level domain'))
    currency_code = models.CharField(max_length=3,
                         blank=True,
                         verbose_name=_(u'ISO 4217 currency code'))
    currency_name = models.CharField(max_length=16,
                         blank=True)
    phone = models.CharField(max_length=16,
                         blank=True)
    postal_code_format = models.CharField(max_length=255,
                         blank=True)
    postal_code_regex = models.CharField(max_length=255,
                         blank=True)
    languages = CSVField(max_length=128,
                         blank=True)
    geonameid = models.IntegerField(null=True)
    neighbours = CSVField(max_length=64,
                         blank=True)
    equivalent_fips_code = models.CharField(max_length=2,
                         blank=True)

    def __unicode__(self):
        return '(%s): %s' % (self.alpha2, self.name)

    @staticmethod
    @cache(keyarg=0)
    def get_by_ip(ip):
        response = requests.get(settings.IPINFODB_API_URL,
                              params={'key': settings.IPINFODB_API_KEY,
                                      'ip': ip,
                                      'format': 'json'})

        try:
            if response.status_code == 200:
                logger.debug(u'api response (%s -> HTTP %s: %s)' % (
                                ip,
                                response.status_code,
                                response.json,))

                return Country.objects.get(alpha2=response.json['countryCode'])
        except Exception, e:
            pass

        logger.exception(u'failed to retrieve country (%s -> HTTP %s: %s: %s)' % (
                             ip,
                             response.status_code,
                             response.text,
                             e if 'e' in locals() else None,))

        return None

