#-*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from core.common import resources as common_resources 


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # api
    url(r'^api/%s/' % settings.API_VERSION, include(common_resources.urls)),
)

urlpatterns += staticfiles_urlpatterns()
