# Troubleshooting

The following is an (incomplete) list of issues and solutions that have been observed with the package install.

## The UI does not work in Linux / WSL

Currently, the UI will only work if you have a graphical output device available. This is not the case in WSL, for example.

In this case, you need to setup and run tagmaps in Windows Command Line to be able to access the GUI.

!!! Note
    We plan to refactor the interface to be served through a web client.
    
## 'proj' datadir not found

If you see the following after running `tagmaps` in your shell:

```bash
proj_create: Cannot find proj.db
proj_create: no database context specified
proj_create: Cannot find proj.db
proj_create: no database context specified
```

.. you might be using an incompatible shell, such as Git Bash, in Windows. The problem relates to the way pyproj stores the location of the proj datadir.

Newer versions of pyproj use environment vars that get activate with the env itself (e.g. `conda activate tagmaps`).

This does not work when using Git Bash in Windows. Check if `PROJ_LIB` environmental variable is available with `echo %PROJ_LIB%` should point to `miniconda3\envs\tagmaps2_env\Library\share\proj`.

Solution: Use native Windows command line. You can access the command line in your current folder by holding `Shift` + `Rightclick` and selecting "Open command Window here".

## _tkinter.TclError: no display name and no $DISPLAY environment variable

To access the optional interface for filtering and preview data, you need to run tagmaps within a visual environment (e.g. Windows). The current error will be given if you try to access the interface from a shell-only environment (such as Windows Subsystem for Linux; or standard Linux shell):

```output
Traceback (most recent call last):
  File "/home/user/miniconda3/envs/tagmaps/bin/tagmaps", line 11, in <module>
    load_entry_point('tagmaps', 'console_scripts', 'tagmaps')()
  File "../tagmaps_package/tagmaps/__main__.py", line 126, in main
    continue_proc = tagmaps.user_interface()
  File "../tagmaps_package/tagmaps/tagmaps_.py", line 107, in _wrapper
    return func(self, *args, **kwargs)
  File "../tagmaps_package/tagmaps/tagmaps_.py", line 300, in user_interface
    self.lbsn_data.locid_locname_dict)
  File "../tagmaps_package/tagmaps/classes/interface.py", line 60, in __init__
    self.app = App()
  File "../tagmaps_package/tagmaps/classes/interface.py", line 563, in __init__
    tk.Tk.__init__(self)
  File "/home/user/miniconda3/envs/tagmaps/lib/python3.7/tkinter/__init__.py", line 2023, in __init__
    self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
_tkinter.TclError: no display name and no $DISPLAY environment variabl
```

You have a couple of options:

* either run tagmaps with the flag `tagmaps --auto_mode`, this will use default values and disable the user interface
* load tagmaps in jupyter or another python package and modify values, see [jupyter section](/user-guide/jupyter-examples/)
* run tagmaps in Windows (or OSx, Linux Gui)

!!! Note
    The Tkinter python interace will be replaced with a native browser based solution in the future. This will allow accessing tagmaps running in (e.g.) Windows Subsystem for Linux through `localhost`