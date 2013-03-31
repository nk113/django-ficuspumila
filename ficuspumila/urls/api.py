#-*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from ficuspumila.core.auth import resources as auth_api
from ficuspumila.core.common import resources as common_api
from ficuspumila.core.content import resources as content_api


urlpatterns = patterns('',
    # v1
    url(r'^v1/core/', include(auth_api.get_urls())),
    url(r'^v1/core/', include(common_api.get_urls())),
    url(r'^v1/core/', include(content_api.get_urls())),
)
