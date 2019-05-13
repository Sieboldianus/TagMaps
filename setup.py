# -*- coding: utf-8 -*-

"""
Setup for building and installing tagmaps package.
"""

import sys
from setuptools import setup

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

try:
    from semantic_release import setup_hook
    setup_hook(sys.argv)
except ImportError:
    pass

VERSION_NUMBER = {}
with open("tagmaps/version.py") as fp:
    exec(fp.read(), VERSION_NUMBER)  # pylint: disable=W0122

setup(name="tagmaps",
      version=VERSION_NUMBER['__version__'],
      description="Tag Clustering for Tag Maps",
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      author='Alexander Dunkel',
      author_email='alexander.dunkel@tu-dresden.de',
      url='https://github.com/Sieboldianus/TagMaps',
      license='GNU GPLv3 or any higher',
      packages=['tagmaps'],
      include_package_data=True,
      install_requires=[
          'fiona>=1.8.6',
          'shapely>=1.6.4',
          'pandas>=0.24.2',
          'pyproj>=2.0.0',
          'numpy>=1.15.4',
          'matplotlib>=3.0.3',
          'emoji>=0.5.1',
          'cython>=0.29.7',
          'hdbscan>=0.8.20',
          'gdal>=2.4.0',
          'attrs>=19.1.0',
          'seaborn>=0.9.0',
          'descartes>=1.1.0',
          'regex>=2019.04.14',
          'scipy>=1.2.1',
      ],
      entry_points={
          'console_scripts': [
              'tagmaps = tagmaps.__main__:main'
          ]
      })
