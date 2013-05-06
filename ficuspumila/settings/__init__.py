# -*- coding: utf-8 -*-

def get(name, default=None):
    from django.conf import settings

    try:
        return getattr(settings, name)
    except AttributeError, e:
        return default

def ficuspumila(name, default=None):
    settings = get('FICUSPUMILA')

    try:
        return settings[name]
    except KeyError, e:
        return default
