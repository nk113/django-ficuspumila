# -*- coding: utf-8 -*-
import logging

from ficuspumila.core import test


logger = logging.getLogger(__name__)


class CountryResource(test.Resource):

    api_name = 'common'
    resource_name = 'country'

    def setUp(self):

        super(CountryResource, self).setUp()

        self.detail_endpoint = '%sJP/' % self.list_endpoint
