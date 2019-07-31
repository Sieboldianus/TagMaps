The following is an (incomplete) list of issues and solutions.

1. 'proj' datadir not found

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