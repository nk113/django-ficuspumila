# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ficuspumila.core.models import Choice, CsvField, Model
from ficuspumila.core.cache import cache


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
    languages = CsvField(max_length=128,
                         blank=True)
    geonameid = models.IntegerField(null=True)
    neighbours = CsvField(max_length=64,
                         blank=True)
    equivalent_fips_code = models.CharField(max_length=2,
                         blank=True)

    def __unicode__(self):
        return '(%s): %s' % (self.alpha2, self.name)
