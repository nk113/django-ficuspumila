# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.test import ResourceTestCase


logger = logging.getLogger(__name__)


class CountryResourceTestCase(ResourceTestCase):

    api_name = 'common'
    resource_name = 'country'

    def setUp(self):

        super(CountryResourceTestCase, self).setUp()

        self.detail_endpoint = '%sJP/' % self.list_endpoint
