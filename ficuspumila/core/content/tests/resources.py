# -*- coding: utf-8 -*-
import logging

from ficuspumila.core import test


logger = logging.getLogger(__name__)


class ContentResource(test.Resource):

    api_name = 'content'
    resource_name = 'genre'

    def test_get_detail_json(self):

        pass


class GenreLocalizationResource(ContentResource):

    resource_name = 'genrelocalization'


class SourceResource(ContentResource):

    resource_name = 'source'


class SourceAttributeNameResource(ContentResource):

    resource_name = 'sourceattributename'


class SourceAttributeResource(ContentResource):

    resource_name = 'sourceattribute'

    def test_get_detail_json(self):

        pass


class SourceEventNameResource(ContentResource):

    resource_name = 'sourceeventname'


class SourceEventResource(ContentResource):

    resource_name = 'sourceevent'

    def test_get_detail_json(self):

        pass


class SourceNotificationResource(ContentResource):

    resource_name = 'sourcenotification'

    def test_get_detail_json(self):

        pass


class OwnerResource(ContentResource):

    resource_name = 'owner'


class FileTypeResource(ContentResource):

    resource_name = 'filetype'


class FileSpecificationAttributeNameResource(ContentResource):

    resource_name = 'filespecificationattributename'

    def test_get_detail_json(self):

        pass


class FileSpecificationAttributeResource(ContentResource):

    api_name = 'content'
    resource_name = 'filespecificationattribute'

    def test_get_detail_json(self):

        pass


class FileSpecificationResource(ContentResource):

    resource_name = 'filespecification'

    def test_get_detail_json(self):

        pass


class ResourceTypeResource(ContentResource):

    resource_name = 'resourcetype'

    def test_get_detail_json(self):

        pass
