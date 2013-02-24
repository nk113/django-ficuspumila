#-*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from core.common import resources as common_resources
from core.content.common import resources as content_common_resources


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # api
    url(r'^%s' % settings.API_PATH, include(common_resources.urls)),
    url(r'^%s' % settings.API_PATH, include(content_common_resources.urls)),
)

urlpatterns += staticfiles_urlpatterns()
