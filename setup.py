# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('README.md') as f:
    long_description = f.read()

with open('VERSION') as version_file:
    version_var = version_file.read().strip()         
     
## setuptools dev
setup(  name = "tagmaps",
        version = version_var,
        description = "Tag Clustering for Tag Maps",
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Alexander Dunkel',
        author_email='alexander.dunkel@tu-dresden.de',
        url='https://gitlab.vgiscience.de/ad/TagCluster',
        license='GNU GPLv3 or any higher',
        packages=['tagmaps'],
        include_package_data=True,
        install_requires=[
            'shapely',
            'emoji',
            'hdbscan'
        ],
        entry_points={
        'console_scripts': [
            'tagmaps = tagmaps.__main__:main'
        ]
        })