# -*- coding: utf-8 -*-

"""Setup config for cx_freeze (build)

Be warned: freezing is _complicated_.

This cx_freeze setup is configured to build a
self executable folder on Windows for Windows, for
users who cannot use a package manager. The resulting
tagmaps.exe can be directly run.

Has been tested with conda environment (Windows 10)

Prerequisites:

- use a fresh conda env and 
  install tagmaps dependencies and tagmaps, e.g.:
- install [OSGeosW64][1], add `C:/OSGeo4W64/bin` (e.g.) to PATH
- use environment_cx.yml to install cx_freeze dependencies:
    - [mkl-service][2]
    - instead of matplotlib-base, matplotlib is used

```cmd
conda update -n base conda
conda config --env --set channel_priority strict
conda env create -f environment_cx.yml
conda activate tagmaps_cx
pip install --no-dependencies .
```

Two additional steps:
- fix hdbscan-joblib-parallel:
    - [Joblib-freeze-issue][3]: as of 2020-01-29, 
      joblib.Parallel can only be run in frozen 
      apps when prefer="threads" is used. This
      has been changed in a fork of HDBSCAN found [here][4]
    - install hdbscan regularly with:
      `conda install hdbscan -c conda-forge`
    - then remove hdbscan without removing dependencies:
      `conda remove hdbscan -c conda-forge --force`
    - clone [4], update from upstream if necessary, 
      and install without dependencies into conda-environment:
      `pip install --no-dependencies .`
- fix shapely and pyproj in cxfreeze:
    - the way shapely and pyproj are packaged by conda is not 
      compatible with cxfreeze
    - `conda remove shapely pyproj -c conda-forge --force`
    - `pip install shapely pyproj`

- make sure that `C:/OSGeo4W64/bin` is available on PATH
- run build with:
```cmd
python cx_setup.py build
```
- rename `C:/OSGeo4W64/` or remove from PATH
- test: 
```cmd
tagmaps.exe ^
    --load_intermediate 01_Input/flickr_dresden_cc-by-licenses.csv
```

[1]: https://trac.osgeo.org/osgeo4w/
[2]: e.g. conda install mkl-service -c conda-forge
[3]: https://github.com/joblib/joblib/issues/1002
[4]: https://github.com/Sieboldianus/hdbscan
"""

import glob
import json
import pathlib
import os.path
import sys
from pathlib import Path

import opcode

from cx_Freeze import Executable, setup

# Derive Package Paths Dynamically
PYTHON_INSTALL_DIR = os.path.dirname(
    os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(
    PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(
    PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')


PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}'
print(f"Running cx_freeze for Python {PYTHON_VERSION}")

# opcode is not a virtualenv module,
# so we can use it to find the stdlib; this is the same
# trick used by distutils itself it installs itself into the virtualenv
DISTUTILS_PATH = os.path.join(os.path.dirname(opcode.__file__), 'distutils')

VERSION_DICT = {}
with open("tagmaps/version.py") as fp:
    exec(fp.read(), VERSION_DICT)  # pylint: disable=W0122
VERSION = VERSION_DICT['__version__']

# Dependencies are automatically detected,
# but it might need fine tuning.
INCLUDES_MOD = [
    "tkinter.filedialog",
    'numpy.lib.format',
    'numpy.core._methods',
    'matplotlib.backends.backend_tkagg',
    'seaborn',
    'seaborn.cm',
    'scipy.sparse.csgraph',
    'argparse',
    'scipy.sparse.csgraph._validation',
    'scipy.spatial.transform._rotation_groups',
    'numpy',
    'scipy._distributor_init',
    'multiprocessing',
    'gdal',
    'joblib',
    'shapely',
    'shapely.geometry'
]

# include all mkl files
# https://stackoverflow.com/q/54337644/4556479
# https://github.com/anthony-tuininga/cx_Freeze/issues/214
# get json file that has mkl files list (exclude the "service" file)
MKL_FILES_JSON_FILE = glob.glob(
    os.path.join(PYTHON_INSTALL_DIR, "conda-meta", "mkl-[!service]*.json"))[0]
with open(MKL_FILES_JSON_FILE) as file:
    MKL_FILES_JSON_DATA = json.load(file)
# get the list of files from the json data file
NUMPY_MKL_DLLS = MKL_FILES_JSON_DATA["files"]
# get the full path of these files
NUMPY_DLLS_FULLPATH = list(map(lambda currPath: os.path.join(
    PYTHON_INSTALL_DIR, currPath), NUMPY_MKL_DLLS))
# add libiomp5md.dll, as it is also needed for Intel MKL
NUMPY_DLLS_FULLPATH.append(
    os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'libiomp5md.dll')
)

# files that need manual attention
INCLUDE_FOLDERS_FILES = [
    (DISTUTILS_PATH, 'distutils'),
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'tcl86t.dll'),
     os.path.join('lib', 'tcl86t.dll'),
     ),
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'tk86t.dll'),
     os.path.join('lib', 'tk86t.dll'),
     ),
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'sqlite3.dll'),
     os.path.join('lib', 'sqlite3.dll'),
     ),
    # both files of geos need to be available in both directories
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'geos.dll'),
     os.path.join('Library', 'lib', 'geos.dll')
     ),
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'geos_c.dll'),
     os.path.join('Library', 'lib', 'geos_c.dll')
     ),
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'geos.dll'),
     os.path.join('geos.dll')
     ),
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'geos_c.dll'),
     os.path.join('geos_c.dll')
     ),
    # strange, but Library/share/proj
    # needs to move to /lib/share/proj
    # in frozen build
    (os.path.join(PYTHON_INSTALL_DIR, 'Library', 'share', 'proj'),
     os.path.join('lib', 'share', 'proj')
     ),        
    'resources/01_Input/',
    'resources/00_Config/',
    'resources/00_generateClusters_OnlyEmoji.cmd',
    'resources/00_generateClusters_OnlyPhotoLocations.cmd',
    'resources/00_generateClusters_OnlyTags.cmd',
    'resources/00_generateClusters_test.cmd',
    'README.md',
    ('tagmaps/matplotlibrc',
     "matplotlibrc")
] + NUMPY_DLLS_FULLPATH

PACKAGES_MOD = ["tkinter", "hdbscan", "sqlite3", "shapely", "shapely.geometry"]
EXCLUDES_MOD = [
    "scipy.spatial.cKDTree",
    "distutils"]


# GUI applications require a different base on Windows
# (the default is for a console application).
BASE = None

EXECUTABLES = [
    Executable('tagmaps/__main__.py',
               base=BASE,
               targetName="tagmaps.exe")
]

BUILD_NAME = f'tagmaps-{VERSION}-win-amd64-{PYTHON_VERSION}'

setup(name="tagmaps",
      version=VERSION,
      description="Tag Clustering for Tag Maps",
      options={
          'build_exe': {
              'includes': INCLUDES_MOD,
              'include_files': INCLUDE_FOLDERS_FILES,
              'packages': PACKAGES_MOD,
              'excludes': EXCLUDES_MOD,
              'optimize': 0,
              'build_exe': (
                  Path.cwd() / 'build' / BUILD_NAME)
          }
      },
      executables=EXECUTABLES)

# open issue Windows:
# after build, rename
# \lib\multiprocessing\Pool.pyc
# to pool.pyc
# see:
# https://github.com/anthony-tuininga/cx_Freeze/issues/353
BUILD_PATH_POOL = (
    Path.cwd() / 'build' / BUILD_NAME /
    'lib' / 'multiprocessing')
Path(BUILD_PATH_POOL / 'Pool.pyc').rename(
    BUILD_PATH_POOL / 'pool.pyc')
