# -*- coding: utf-8 -*-

"""Setup config for cx_freeze (built)"""

import distutils
import os.path
import sys

from cx_Freeze import Executable, setup

import opcode

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

# Dependencies are automatically detected,
# but it might need fine tuning.
INCLUDES_MOD = [
    "tkinter.filedialog",
    'numpy.core._methods',
    'numpy.lib.format',
    'matplotlib.backends.backend_tkagg',
    'seaborn',
    'seaborn.cm',
    'scipy.sparse.csgraph',
    'argparse',
    'scipy.sparse.csgraph._validation',
    'numpy.core._dtype_ctypes',
    'scipy._distributor_init',
    'multiprocessing'
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

setup(name="tagmaps",
      version=VERSION_DICT['__version__'],
      description="Tag Clustering for Tag Maps",
      options={
          'build_exe': {
              'includes': INCLUDES_MOD,
              'include_files': INCLUDE_FOLDERS_FILES,
              'packages': PACKAGES_MOD,
              'excludes': EXCLUDES_MOD,
              'optimize': 0}
      },
      executables=EXECUTABLES)

# open issue Windows:
# after build, rename
# \lib\multiprocessing\Pool.pyc
# to pool.pyc
# see:
# https://github.com/anthony-tuininga/cx_Freeze/issues/353