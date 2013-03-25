#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import to get rid of an error in atexit._run_exitfuncs
import logging
import multiprocessing

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='django-ficuspumila',
    version='0.0.1',
    description='A Django application suite which helps building media distribution service.',
    long_description=open('README.rst', 'r').read(),
    url='http://github.com/nk113/django-ficuspumila/',
    packages=find_packages(),
    package_data={'': ['*/fixtures/*.json']},
    zip_safe=False, 
    tests_require=('mock', 'django_nose',),
    test_suite = 'ficuspumila.runtests.runtests',
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
