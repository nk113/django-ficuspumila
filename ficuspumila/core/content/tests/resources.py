# -*- coding: utf-8 -*-
from ficuspumila.core.test import ResourceTestCase


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


class SourceEventNameResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourceeventname'


class SourceEventResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourceevent'


class SourceNotificationResourceTestCase(ContentResourceTestCase):

    resource_name = 'sourcenotification'


class OwnerResourceTestCase(ContentResourceTestCase):

    resource_name = 'owner'


class FileTypeResourceTestCase(ContentResourceTestCase):

    resource_name = 'filetype'


class FileSpecificationResourceTestCase(ContentResourceTestCase):

    resource_name = 'filespecification'


class FileSpecificationAttributeNameResourceTestCase(ContentResourceTestCase):

    resource_name = 'filespecificationattributename'


class FileSpecificationAttributeResourceTestCase(ContentResourceTestCase):

    resource_name = 'filespecificationattribute'


class ResourceTypeResourceTestCase(ContentResourceTestCase):

    resource_name = 'resourcetype'
