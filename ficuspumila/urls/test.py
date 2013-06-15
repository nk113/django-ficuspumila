#-*- coding: utf-8 -*-
from django.conf.urls import include, patterns, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from ficuspumila.apps.tests import resources as tests_api


urlpatterns = patterns('',
    # api
    url(r'^api/', include('ficuspumila.urls.api')),
    url(r'^api/v1/apps/', include(tests_api.get_urls())),

    # event - testing purpose only
    url(r'^event_receiver/', 'ficuspumila.core.views.event_receiver'),
)

urlpatterns += staticfiles_urlpatterns()
