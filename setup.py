# -*- coding: utf-8 -*-

from setuptools import setup
import sys

with open('README.md') as f:
    long_description = f.read()
     
     
## setuptools dev
setup(  name = "tagmaps",
        version = "0.9.3",
        description = "Tag Clustering for Tag Maps",
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Alexander Dunkel',
        author_email='alexander.dunkel@tu-dresden.de',
        url='https://gitlab.vgiscience.de/ad/TagCluster',
        license='GNU GPLv3 or any higher',
        packages=['tagmaps'],
        install_requires=[
        ],
        entry_points={
        'console_scripts': [
            'tagmaps = tagmaps.__main__:main'
        ]
        })