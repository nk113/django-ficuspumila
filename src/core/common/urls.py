# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url


from resources import urls as resources_urls


urlpatterns = patterns('',
    # resources
    url(r'^api/%s/' % settings.API_VERSION, include(resources_urls)),
)
