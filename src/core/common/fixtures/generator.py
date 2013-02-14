# -*- coding: utf-8 -*-
import json
import logging
import os
import requests
import StringIO

from django.conf import settings
from operator import itemgetter

from core.common.models import Country


logger = logging.getLogger(__name__)

INITIAL_DATA = '%s/initial_data.json' % os.path.dirname(__file__)
COUNTRY_COMMENT = '#'
COUNTRY_PK_FIELD = 'alpha2' 
COUNTRY_COLUMN_DELIMITER = '\t'
COUNTRY_COLUMN_FIELD_MAP = (
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


def generate():
    logger.debug('generating fixture...')

    return update()

def update():
    logger.debug('updating fixture...')

    with open(INITIAL_DATA, 'w') as initial_data:
        # load json into memory
        logger.debug(INITIAL_DATA)
        try:
            fixture = json.loads(initial_data)
        except:
            fixture = json.loads('[]')

        # update objects
        _update_country_objects(fixture)

        # sort objects
        fixture = sorted(fixture, key=itemgetter('pk'))
        fixture = sorted(fixture, key=itemgetter('model'))

        # overwrite initial_data
        initial_data.write(json.dumps(fixture, sort_keys=True, indent=2))

    logger.debug('fixture has successfully been updated.')

    return 0

def _findex(fixture, model, pk):
    for i, obj in enumerate(fixture):
        if obj['model'] == model and obj['pk'] == pk:
            return i
    return len(fixture)

def _update_country_objects(fixture):

    def cindex(field):
        return [i for i, v in enumerate(COUNTRY_COLUMN_FIELD_MAP) if v[1] == field][0]

    def populate(fixture, row):
        pk_index = cindex(COUNTRY_PK_FIELD)
        try:
            del fixture[_findex(fixture, 'common.country', row[pk_index])]
        except IndexError, e:
            pass
            
        fixture.append({
            'pk': row[pk_index],
            'model': 'common.country',
            'fields': {
                'alpha3'  : row[cindex('alpha3')],
                'numeric3': row[cindex('numeric3')],
                'fips'    : row[cindex('fips')],
                'name'    : row[cindex('name')],
                'capital' : row[cindex('capital')],
                'area'    : row[cindex('area')],
                'population'        : row[cindex('population')],
                'continent'         : row[cindex('continent')],
                'tld'               : row[cindex('tld')],
                'currency_code'     : row[cindex('currency_code')],
                'currency_name'     : row[cindex('currency_name')],
                'phone'             : row[cindex('phone')],
                'postal_code_format': row[cindex('postal_code_format')],
                'postal_code_regex' : row[cindex('postal_code_regex')],
                'languages'         : row[cindex('languages')],
                'geonameid'         : row[cindex('geonameid')],
                'neighbours'        : row[cindex('neighbours')],
                'equivalent_fips_code': row[cindex('equivalent_fips_code')],
            }
        })

    # update country objects in initial_data.json
    response = requests.get(settings.GEONAMES_COUNTRY_INFO)

    if response.status_code == 200:
        tsv = StringIO.StringIO(response.text)
        prevline = ''
        columns = None

        for line in tsv.readlines():
            if not line.startswith(COUNTRY_COMMENT):

                # detect column headers
                if columns is None and prevline.startswith(COUNTRY_COMMENT):
                    columns = prevline[1:].strip().split(COUNTRY_COLUMN_DELIMITER)
                    # interrupt if column structure has changed
                    if columns != [c for c, f in COUNTRY_COLUMN_FIELD_MAP]:
                        raise Exception('Column structure seems to have changed!')

                # fill missing columns
                row = line.strip().split(COUNTRY_COLUMN_DELIMITER)
                while len(row) < len(COUNTRY_COLUMN_FIELD_MAP):
                    row.append(u'')

                populate(fixture, row)
                prevline = line

        tsv.close()
    else:
        logger.debug(u'failed to fetch the source: HTTP %s: %s' % (
                        response.status_code,
                        response.text))
