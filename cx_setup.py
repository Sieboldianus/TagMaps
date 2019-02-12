# -*- coding: utf-8 -*-

"""Setup config for cx_freeze (build)"""

import os.path
import opcode
from pathlib import Path
from cx_Freeze import Executable, setup

# Derive Package Paths Dynamically
PYTHON_INSTALL_DIR = os.path.dirname(
    os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(
    PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(
    PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')


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
    'numpy',
    'scipy._distributor_init',
    'multiprocessing',
    'gdal'
]

# windows pipenv:
# copy tcl86t.dll, tk86t.dll and sqlite3.dll
# to venv_folder/DLLs/*
INCLUDE_FOLDERS_FILES = [
    (DISTUTILS_PATH, 'distutils'),
    (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
     os.path.join('lib', 'tcl86t.dll'),
     ),
    (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
     os.path.join('lib', 'tk86t.dll'),
     ),
    (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'sqlite3.dll'),
     os.path.join('lib', 'sqlite3.dll'),
     ),
    os.path.join(PYTHON_INSTALL_DIR, 'Library', 'bin', 'mkl_intel_thread.dll'),
    # os.path.join(os.environ['GDAL_DATA'], 'gcs.csv'),
    'resources/01_Input/',
    'resources/00_Config/',
    'resources/00_generateClusters_OnlyEmoji.cmd',
    'resources/00_generateClusters_OnlyPhotoLocations.cmd',
    'resources/00_generateClusters_OnlyTags.cmd',
    ('tagmaps/matplotlibrc',
     "matplotlibrc")
]
PACKAGES_MOD = ["tkinter", "hdbscan"]
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

BUILD_NAME = f'TagMaps-Win-{VERSION}'

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
