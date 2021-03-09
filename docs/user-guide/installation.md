# Detailed installation guide

This detailed installation guide is for users who are not familiar with python package managers. The guide demonstrates installing tagmaps in Windows 10 and Miniconda3. Miniconda3 is available for Linux and macOS, too - in this case, substitute initial steps.

## Install Chocolatey

If you don't have conda package manager installed, I recommend installing it with [Chocolatey package manager](https://chocolatey.org/) for Windows. Chocolatey will configure everything without your need to intervene.

To install Chcolatey:

* Open cmd with administrator privileges: 
    * in Windows 10, click on start (or hit the ⊞ Win-Key), type "cmd", right click on **Open Command Prompt** and select "Run as Administrator" ![](https://ad.vgiscience.org/links/imgs/2019-05-23_cmd-run-as-admin.png)
* enter the following command (taken from the choco [installation instructions](https://chocolatey.org/install)):    
```
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
```
* Once choco is installed, restart the administrator console once
* (I suggest using **choco** for any software install on Windows, simply run `choco upgrade all -Y` once a week to keep all your software up to date)

## Install Miniconda

You can either install [Anaconda](<https://anaconda.org/>) or [Miniconda](<https://docs.conda.io/en/latest/miniconda.html>). Miniconda is suitable if you only want the package manager. To install Miniconda3 with Choco in Windows, type:

```Bash
choco install miniconda3
```

Now Miniconda is installed, you can either use the "Anaconda Prompt" to install packages, or add **conda** to your **Path**.
The latter _can_ be problematic if you have many different Python Versions installed (e.g. such as Python 2.7 and 3.6). However, since I only use conda for all my python work, it is convenient enough for me.

To add conda to your **Path**:

* click start (or hit the ⊞ Win-Key)
    * type "Environment", select the following: ![](https://ad.vgiscience.org/links/imgs/2019-05-23_environment_variables.png)
* select "Environment Variables.."
* under system variables, search for the entry for **Path**: ![](https://ad.vgiscience.org/links/imgs/2019-05-23_path.png)  
* click edit, add the following entries to the top of the list:
    * `C:\tools\miniconda3\Library\mingw-w64\bin`
    * `C:\tools\miniconda3\Library\usr\bin`
    * `C:\tools\miniconda3\Library\bin`
    * `C:\tools\miniconda3\Scripts`

It will look something like this:
![](https://ad.vgiscience.org/links/imgs/2019-05-23_conda_path.png)

Adding folder to **Path** means that if you type commands in the console (cmd), Windows will go through each folder and search for matching executables (exe´s). For example, if you type `conda do-something`, it will look for a conda.exe to do-something.
In the above picture, I've moved my still existent main Python installation above conda, meaning that if I type `python do-something`, it will first use the main Python exe.

## Create an Environment for tagmaps package

You can install Tagmaps in the conda base environment, but it is always better to organize python packages in separate __environments__ that can be used separately for separate projects.

To create a new conda environment:

* either open Anaconda Prompt
* or console/cmd (if you added conda to __Path__
* check if you have the latest version of conda package manager with `conda update conda`
* afterwards, type `conda create -n tagmaps_env -y` to initialize a new env called _tagmaps_env_

Note that it does not matter where your prompt/console is opened (e.g. `C:/temp/` or `C:/Windows/system32` etc.). The conda environment will always be created in `C:\tools\miniconda3\envs`.

## Install Tagmaps

* first, activate the environment that was just created by typing: `conda activate tagmaps_env`
* add conda-forge to the list of channels (for this env only): `conda config --add channels conda-forge`
    * [conda-forge](https://anaconda.org/conda-forge) is a community managed branch of anaconda packages
* install tagmaps in `tagmaps_env` with `conda install tagmaps -y`

![](https://ad.vgiscience.org/links/imgs/2019-05-23_install_tagmaps.gif)

This will install `tagmaps` package and all dependencies to `tagmaps_env`.

## Test Tagmaps

To verify it the package install works:

* go to the resource folder on [Github Tagmaps](https://github.com/Sieboldianus/TagMaps/tree/master/resources)
* download the folders `01_Input` and `00_Config` and its contents somewhere, e.g.:
    * `01_Input:`  
    ![](https://ad.vgiscience.org/links/imgs/2019-05-23_test_folder.png)  
    * `00_Config:`  
    ![](https://ad.vgiscience.org/links/imgs/2019-05-23_test_folder2.png)  
* go one folder up, hold down `Shift` and right click somewhere
* either select **Open Power Shell Window here** or **Open command Window here**
    * you may also open `Anaconda prompt` or cmd console (⊞ Win-Key)
    * and then change into your working dir by `cd C:\temp\tagmaps` (e.g.)
* type `conda activate tagmaps_env`
* then type `tagmaps` and hit enter

This should start tagmaps process the example file in `01_Input` subfolder using the example config files in `00_Config`:  
  
![](https://ad.vgiscience.org/links/imgs/2019-05-23_run_tagmaps.gif)

## Check results

Results will be stored in `02_Output` folder:
![](https://ad.vgiscience.org/links/imgs/2019-05-23_verify_tagmaps.gif)

These shapefiles can be visualized, for example, with ESRI ArcMap. There're *.mxd files provided for the different ArcMap versions on Github Tagmaps [resource folder](https://github.com/Sieboldianus/TagMaps/tree/master/resources).

Further reading:  

* There's a more thorough tutorial available [here](https://ad.vgiscience.org/tagmaps_tutorial), which also covers the steps in ArcMap 
* Check out [this album on Flickr](https://www.flickr.com/photos/64974314@N08/albums/72157628868173205) with some more Tag Maps examples
* There's also a semi-interactive interface to explore some Tag Maps [here](http://maps.alexanderdunkel.com/)
* Check out my blog [here](http://blog.alexanderdunkel.com/) with some background information
* A [Jekyll-Reveal presentation](https://ad.vgiscience.org/tagmaps_intro/) on theory & background

