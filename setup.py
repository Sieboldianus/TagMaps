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
      python_requires='>=3.7',  # minimum, due to dataclass
      install_requires=[
          'fiona',
          'shapely',
          'pandas>=0.24.2',
          'pyproj>=2.0.0',
          'numpy',
          'matplotlib',
          'emoji>=1.0.1',
          'cython',
          'hdbscan>=0.8.20',
          'gdal',
          'seaborn',
          'descartes',
          'regex',
          'scipy',
          'joblib'
      ],
      entry_points={
          'console_scripts': [
              'tagmaps = tagmaps.__main__:main'
          ]
      })
