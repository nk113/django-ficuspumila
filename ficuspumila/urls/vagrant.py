#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from ficuspumila.settings import ficuspumila as settings


admin.autodiscover()


urlpatterns = patterns('',
    # admin
    url(r'^%s' % settings('ADMIN_PREFIX'), include(admin.site.urls)),

    # api
    url(r'^api/', include('ficuspumila.urls.api')),

    # event - testing purpose only
    url(r'^event_receiver/', 'ficuspumila.core.views.event_receiver'),
)

urlpatterns += staticfiles_urlpatterns()
