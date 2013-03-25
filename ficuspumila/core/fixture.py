# -*- coding: utf-8 -*-
import json
import logging
import os

from operator import itemgetter

from .exceptions import FixtureException


logger = logging.getLogger(__name__)


class Generator(object):

    fixture_dir = None
    fixtures = ('initial_data.json',)
    data = None

    def __init__(self, fixtures=None):
        if self.fixture_dir is None:
            raise FixtureException(u'"fixture_dir" needs to be specified ' +
                                   u'in subclasses.')
        self.fixtures = fixtures if fixtures is not None else self.fixtures

    def generate(self):
        logger.info(u'generating fixtures...')

        return self.update()

    def update(self):
        logger.info(u'updating fixtures: %s' % str(self.fixtures))

        for fixture in self.fixtures:
            try:
                with open('%s/%s' % (self.fixture_dir,
                                     fixture,), 'r') as fixture_file:
                    # load json into memory
                    try:
                        self.data = json.loads(fixture_file.read())
                    except Exception, e:
                        logger.exception(u'an error occurred during parsing ' +
                                         u'fixture: %s' % e)

                        self.data = json.loads('[]')

                    # update objects
                    self.update_objects()

                    # sort objects
                    self.data = sorted(self.data, key=itemgetter('pk'))
                    self.data = sorted(self.data, key=itemgetter('model'))

                with open('%s/%s' % (self.fixture_dir,
                                     fixture,), 'w') as fixture_file:
                    # overwrite initial_data
                    fixture_file.write(json.dumps(self.data,
                                                  sort_keys=True,
                                                  indent=2))

            except Exception, e:
                logger.exception(u'an error has occurred during update (%s)' % e)

                return 1

        logger.info(u'fixtures have successfully been updated.')
        return 0

    def update_objects(self):
        """
        Should be implemented in subclasses
        """
        pass

    def index(self, model, pk):
        if self.data:
            for i, obj in enumerate(self.data):
                if obj['model'] == model and obj['pk'] == pk:
                    return i
        return -1
