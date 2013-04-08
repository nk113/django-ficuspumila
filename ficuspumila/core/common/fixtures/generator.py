# -*- coding: utf-8 -*-
import logging
import math
import os
import requests
import StringIO

from django.conf import settings
from django.utils import timezone

from ficuspumila.core import fixture


logger = logging.getLogger(__name__)


class Generator(fixture.Generator):

    fixture_dir = os.path.dirname(__file__)

    def update_objects(self):
        Country(self).update_objects()


class Country(object):

    PK_FIELD = 'alpha2' 
    COMMENT = '#'
    DELIMITER = '\t'
    COLUMN_FIELD_MAP = (
        (u'ISO', 'alpha2',),
        (u'ISO3', 'alpha3',),
        (u'ISO-Numeric', 'numeric3',),
        (u'fips', 'fips',),
        (u'Country', 'name',),
        (u'Capital', 'capital',),
        (u'Area(in sq km)', 'area',),
        (u'Population', 'population',),
        (u'Continent', 'continent',),
        (u'tld', 'tld',),
        (u'CurrencyCode', 'currency_code',),
        (u'CurrencyName', 'currency_name',),
        (u'Phone', 'phone',),
        (u'Postal Code Format', 'postal_code_format',),
        (u'Postal Code Regex', 'postal_code_regex',),
        (u'Languages', 'languages',),
        (u'geonameid', 'geonameid',),
        (u'neighbours', 'neighbours',),
        (u'EquivalentFipsCode', 'equivalent_fips_code',),
    )

    def __init__(self, generator):
        self.generator = generator

    def update_objects(self):

        def cindex(field):
            return [i for i, v in enumerate(self.COLUMN_FIELD_MAP) if v[1] == field][0]

        def populate(row):
            # logger.debug(u'populating... (%s)' % row)

            index = self.generator.index('common.country', row[cindex(self.PK_FIELD)])

            try:
                if index >= 0:
                    del self.generator.data[index]
            except IndexError, e:
                pass

            area = int(math.ceil(float(row[cindex('area')]))) if len(row[cindex('area')]) else None
            population = row[cindex('population')] if len(row[cindex('population')]) else None
            geonameid = row[cindex('geonameid')] if len(row[cindex('geonameid')]) else None

            self.generator.data.append({
                'pk': row[cindex(self.PK_FIELD)],
                'model': 'common.country',
                'fields': {
                    'alpha3'    : row[cindex('alpha3')],
                    'numeric3'  : row[cindex('numeric3')],
                    'fips'      : row[cindex('fips')],
                    'name'      : row[cindex('name')],
                    'capital'   : row[cindex('capital')],
                    'area'      : area,
                    'population': population,
                    'continent'         : row[cindex('continent')],
                    'tld'               : row[cindex('tld')],
                    'currency_code'     : row[cindex('currency_code')],
                    'currency_name'     : row[cindex('currency_name')],
                    'phone'             : row[cindex('phone')],
                    'postal_code_format': row[cindex('postal_code_format')],
                    'postal_code_regex' : row[cindex('postal_code_regex')],
                    'languages'         : row[cindex('languages')],
                    'geonameid'         : geonameid,
                    'neighbours'        : row[cindex('neighbours')],
                    'equivalent_fips_code': row[cindex('equivalent_fips_code')],
                    'ctime': '%s' % timezone.now(),
                    'utime': '%s' % timezone.now(),
                }
            })

        # update objects in fixture
        response = requests.get(settings.FICUSPUMILA['GEONAMES_COUNTRY_INFO'])

        if response.status_code == 200:
            tsv = StringIO.StringIO(response.text)
            prevline = ''
            columns = None

            for line in tsv.readlines():
                if not line.startswith(self.COMMENT):

                    # detect column headers
                    if columns is None and prevline.startswith(self.COMMENT):
                        columns = prevline[1:].strip().split(self.DELIMITER)
                        # interrupt if column structure has changed
                        if columns != [c for c, f in self.COLUMN_FIELD_MAP]:
                            raise Exception('Column structure seems to have changed!')

                    # fill missing columns
                    row = line.strip().split(self.DELIMITER)
                    while len(row) < len(self.COLUMN_FIELD_MAP):
                        row.append(u'')

                    populate(row)
                    prevline = line

                    tsv.close()

        else:
            logger.warning(u'failed to fetch the source (HTTP %s: %s)' % (
                             response.status_code,
                             response.text))
