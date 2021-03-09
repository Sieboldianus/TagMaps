# Installation
## Conda

This is the recommended way for all systems.

This approach is independent of the OS used.

First create an environment.

```bash
conda create --name tagmaps
```

Then install tagmaps from the conda-forge channel.

```bash
conda activate tagmaps
conda config --env --set channel_priority strict
conda install tagmaps --channel conda-forge
```

## Windows

There are many ways to install python tools:

1. The recommended way to install the package is with [conda](#conda)
2. For Windows users, an alternative is to download the newest pre-compiled build from [releases](../../releases) and run `tagmaps.exe`
3. If you need to install with pip, it is recommended to 
    - install all dependencies first (e.g. Windows users: use [Gohlke wheels](<https://www.lfd.uci.edu/~gohlke/pythonlibs/>) if available) and then run:
    - `pip install tagmaps --no-dependencies`
    - or clone the repository, and install locally with:
    - `pip install --no-dependencies --editable .`

Of these 3 choices, **using conda is the one that I prefer**. For users who are not familiar with python package managers, please see the detailed instructions to install tagmaps with conda provided [here](../user-guide/installation/).

## Linux

Both `pip install tagmaps` and `conda install tagmaps -c conde-forge` are available to install tagmaps in Linux.

Setup requires gdal to be available. As a minimal example, have a look at the following commands for Ubuntu:

```bash
git clone https://github.com/Sieboldianus/TagMaps.git
cd tagmaps
apt-get install python3-venv
# create a virtual env
python3 -m venv tagmaps
source ./tagmaps/bin/activate
# install gdal
apt-get install libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
# get gdal version
gdal-config --version # Output: 2.2.3
# install matching gdal version with pip
pip install GDAL==2.2.3
# Install latest tagmaps from GitHub
pip install --editable .
# or from latest release on pip:
# pip install tagmaps
```