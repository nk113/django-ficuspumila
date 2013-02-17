# -*- coding: utf-8 -*-
import json
import logging
import os

from operator import itemgetter


logger = logging.getLogger(__name__)


class Generator(object):

    fixture = '%s/initial_data.json' % os.path.dirname(__file__)
    data = None

    def __init__(self, fixture=None):
        self.fixture = fixture if fixture else self.fixture

    def generate(self):
        logger.info('generating fixture...')

        return self.update()

    def update(self):
        logger.info('updating fixture: %s' % self.fixture)

        try:
            with open(self.fixture, 'r') as fixture:
                # load json into memory
                try:
                    self.data = json.loads(fixture.read())
                except Exception, e:
                    logger.exception('an error occurred during parsing fixture: %s' % e)

                    self.data = json.loads('[]')

                # update objects
                self.update_objects()

                # sort objects
                self.data = sorted(self.data, key=itemgetter('pk'))
                self.data = sorted(self.data, key=itemgetter('model'))

            with open(self.fixture, 'w') as fixture:

                # overwrite initial_data
                fixture.write(json.dumps(self.data, sort_keys=True, indent=2))

        except Exception, e:
            logger.exception('an error has occurred during update (%s)' % e)

            return 1

        logger.info('fixture has successfully been updated.')
        return 0

    def update_objects(self):
        '''
        Should be implemented in subclasses
        '''
        pass

    def index(self, model, pk):
        if self.data:
            for i, obj in enumerate(self.data):
                if obj['model'] == model and obj['pk'] == pk:
                    return i
        return -1
