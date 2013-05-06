# -*- coding: utf-8 -*-
import logging

from ficuspumila.core.test import ResourceTestCase


logger = logging.getLogger(__name__)


class ContentResourceTestCase(ResourceTestCase):

    api_name = 'content'
    resource_name = 'genre'

    def test_get_detail_json(self):

        pass


class GenreLocalizationResourceTestCase(ContentResourceTestCase):

    resource_name = 'genrelocalization'


class SourceResourceTestCase(ContentResourceTestCase):

    resource_name = 'source'


class SourceAttributeNameResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourceattributename'


class SourceAttributeResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourceattribute'

    def test_get_detail_json(self):

        pass


class SourceEventNameResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourceeventname'


class SourceEventResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourceevent'

    def test_get_detail_json(self):

        pass


class SourceNotificationResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourcenotification'

    def test_get_detail_json(self):

        pass


class OwnerResourceTestCase(ContentResourceTestCase):

    resource_name = 'owner'


class FileTypeResourceTestCase(ContentResourceTestCase):

    resource_name = 'filetype'


class FileSpecificationAttributeNameResourceTestCase(ContentResourceTestCase):

    resource_name = 'filespecificationattributename'

    def test_get_detail_json(self):

        pass


class FileSpecificationAttributeResourceTestCase(ContentResourceTestCase):

    api_name = 'content'
    resource_name = 'filespecificationattribute'

    def test_get_detail_json(self):

        pass


class FileSpecificationResourceTestCase(ContentResourceTestCase):

    resource_name = 'filespecification'

    def test_get_detail_json(self):

        pass


class ResourceTypeResourceTestCase(ContentResourceTestCase):

    resource_name = 'resourcetype'

    def test_get_detail_json(self):

        pass
