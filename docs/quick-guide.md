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

Or, use the provided `environment.yml` and install in editable mode.
This would be more common for a development setup:
```bash
conda env create -n tagmaps -f environment.yml
conda activate tagmaps
pip install --no-deps --editable .
```

## Windows

There are many ways to install python tools:

1. The recommended way to install the package is with [conda](#conda)
2. If you need to install with pip, it is recommended to 
    - install all dependencies first (e.g. Windows users: use 
      [Gohlke wheels](<https://www.lfd.uci.edu/~gohlke/pythonlibs/>) if available), or
      `conda env create -f environment.yml`, and then run:
    - `pip install tagmaps --no-dependencies` or 
    - or clone the repository, and install locally with:
    - `pip install --no-dependencies --editable .`

For users who are not familiar with python package managers, 
please see [the detailed instructions to install tagmaps with conda](../user-guide/installation/).

## Linux

Both `pip install tagmaps` and `conda install tagmaps -c conde-forge` are available to install tagmaps in Linux.

Setup requires gdal to be available. As a minimal example, have a look at the following commands for Ubuntu:

First, install base dependencies:
```
apt-get install python3-venv python3-dev python3-tk gcc -y
```

Then clone the repository, install python3-venv and install dependencies:
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

Depending on your Linux distribution and version, you _may_ get away without the GDAL related instructions above.

Alternatively, you can also install using `requirements.txt`:
```
python3 -m venv tagmaps
source ./tagmaps/bin/activate
pip install -r requirements.txt
pip install --no-deps --editable .
```