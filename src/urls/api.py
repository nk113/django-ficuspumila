#-*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from core.api import resources as core_api
from core.content.api import resources as content_api


urlpatterns = patterns('',
    url(r'^%s' % settings.API_PATH, include(core_api.urls)),
    url(r'^%s' % settings.API_PATH, include(content_api.urls)),
)
