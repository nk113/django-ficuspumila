#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='ficuspumila',
    version='0.0.1',
    description='A Django application suite which helps building media distribution service.',
    long_description=open('README.rst', 'r').read(),
    url='http://github.com/nk113/ficuspumila/',
    packages=find_packages(),
    zip_safe=False, 
    tests_require=('mock',),
    install_requires=[
        'celery',
        'Django',
        'django-celery',
        'django-tastypie',
        'pycrypto',
        'south',
        'tastypie-queryset-client',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    author='Nobu Kakegawa',
    author_email='nobu@nk113.com',
)
