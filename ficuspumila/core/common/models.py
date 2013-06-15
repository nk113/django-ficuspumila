# -*- coding: utf-8 -*-
import logging

from django.db import models as djmodels
from django.utils.translation import ugettext_lazy as _

from ficuspumila.core import models


logger = logging.getLogger(__name__)


class Country(models.Model):

    class Meta:

        verbose_name = _(u'Country')
        verbose_name_plural = _(u'Countries')

    class Continents(models.Choice):

        ANTARCTICA     = 'AN'
        ASIA           = 'AS'
        EUROPE         = 'EU'
        NOURTH_AMERICA = 'NA'
        OCEANIA        = 'OC'
        SOURTH_AMERICA = 'SA'

    alpha2 = djmodels.CharField(max_length=2,
                         primary_key=True,
                         verbose_name=_(u'ISO 3166-1 alpha-2 code'))
    alpha3 = djmodels.CharField(max_length=3,
                         unique=True,
                         verbose_name=_(u'ISO 3166-1 alpha-3 code'))
    numeric3 = djmodels.CharField(max_length=3,
                         unique=True,
                         verbose_name=_(u'ISO 3166-1 numeric code'))
    fips = djmodels.CharField(max_length=2,
                         blank=True)
    name = djmodels.CharField(max_length=128)
    capital = djmodels.CharField(max_length=128)
    area = djmodels.IntegerField(null=True,
                         verbose_name=_(u'Area (in sq km)'))
    population = djmodels.IntegerField(null=True)
    continent = djmodels.CharField(max_length=2,
                         choices=Continents)
    tld = djmodels.CharField(max_length=5,
                         blank=True,
                         verbose_name=_(u'Top level domain'))
    currency_code = djmodels.CharField(max_length=3,
                         blank=True,
                         verbose_name=_(u'ISO 4217 currency code'))
    currency_name = djmodels.CharField(max_length=16,
                         blank=True)
    phone = djmodels.CharField(max_length=16,
                         blank=True)
    postal_code_format = djmodels.CharField(max_length=255,
                         blank=True)
    postal_code_regex = djmodels.CharField(max_length=255,
                         blank=True)
    languages = models.CsvField(max_length=128,
                         blank=True)
    geonameid = djmodels.IntegerField(null=True)
    neighbours = models.CsvField(max_length=64,
                         blank=True)
    equivalent_fips_code = djmodels.CharField(max_length=2,
                         blank=True)

    def __unicode__(self):
        return '(%s): %s' % (self.alpha2, self.name)
