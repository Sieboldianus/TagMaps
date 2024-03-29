# Developers

The tagmaps python package is research software. Maintenance usually happens in chunks, whenever I have time.

You can contribute feedback, submit issues for bugs etc. on [Github](https://github.com/Sieboldianus/tagmaps) 
or [Gitlab](https://gitlab.vgiscience.de/ad/tagmaps).

## Importing tagmaps as a package

It is possible to import tagmaps as a package:

```py
from tagmaps import TagMaps
from tagmaps import EMOJI, TAGS, LOCATIONS, TOPICS
from tagmaps import LoadData
from tagmaps import BaseConfig
from tagmaps.classes.utils import Utils
```

Have a look at the [Jupyter Lab examples](user-guide/jupyter-examples.md).

## Structure of the project

The project structure follows the [src-layout](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#src-layout).

The packaging is organized as described in the setuptools [declarative config (pyproject.toml)](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html).

The version is maintained both as git tags and inside `src/tagmaps/version.py`, with the latter as the single point of truth.

Tagmaps commit follow the [Angular commit message conventions](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits). For a good introduction, see [Understanding Semantic Commit Messages Using Git and Angular](https://nitayneeman.com/posts/understanding-semantic-commit-messages-using-git-and-angular/).

Releases are made with [python-semantic-release](https://github.com/python-semantic-release/python-semantic-release). At the
moment, releases are triggered manually after certain progress is available. Preview release flow with:

```bash
semantic-release -v --noop version
twine upload dist/*
semantic-release -v --noop publish
```

Without `--noop`, semantic-release will do the [following](https://python-semantic-release.readthedocs.io/en/latest/#semantic-release-publish):

1. Update changelog file.
2. Version project based on previous commits
3. Push changes to git.
4. Run [build_command](https://python-semantic-release.readthedocs.io/en/latest/configuration.html#config-build-command) 
   (`python -m build`) and upload the distribution files to Pypi.
5. Run [semantic-release changelog](https://python-semantic-release.readthedocs.io/en/latest/commands.html#cmd-changelog) and post to Gitlab/Github.
6. Attach the files created by [build_command](https://python-semantic-release.readthedocs.io/en/latest/commands.html#semantic-release-publish) to the release.

To trigger a test build:
```bash
pip install -q build
python -m build
```

There is a separate [conda-forge feedstock](https://github.com/conda-forge/tagmaps-feedstock) that prepares the conda-forge distribution of tagmaps.