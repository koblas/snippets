#!/usr/bin/env python

from distutils.core import setup

install_requires = []

version = "0.1"

setup(
    name='Snippets',
    version=version,
    description='A snippet platform',
    author='David Koblas',
    author_email='david@koblas.com',
    url='http://github.com/koblas/snippets',
    install_requires=install_requires,
    package_dir = {'thistle' : 'py/thistle' },

    packages=['snippets'],

    requires=[
        'thistle',
        'tornado',
        'mongoengine',
        'PyYAML',
    ],
)

