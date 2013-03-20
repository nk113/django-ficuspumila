#-*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from ficuspumila.core.api import resources as core_api
from ficuspumila.core.content.api import resources as content_api


urlpatterns = patterns('',
    # v1
    url(r'^api/v1/',      include(core_api.get_urls())),
    url(r'^api/v1/core/', include(content_api.get_urls())),
)
