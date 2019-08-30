"""Script to allow argdown parse_args to markdown conversion"""

import inspect
from tagmaps import BaseConfig
from tagmaps import __version__


def extract_argscode():
    """Extracts command line args code to separate file

    Preparation step for processing with argdown
    """
    # open file to output source code
    source_file = open("parse_args.py", "w")
    # extract source code of parse_args
    parse_args_source = inspect.getsource(BaseConfig.parse_args)
    # remove first line
    parse_args_source = parse_args_source[parse_args_source.index('\n')+1:]
    # unindent all other lines
    parse_args_source = parse_args_source.lstrip().replace('\n        ', '\n')
    # replace version string
    parse_args_source = parse_args_source.replace(
        'tagmaps {__version__}', f'tagmaps {__version__}')
    # replace package name
    parse_args_source = parse_args_source.replace(
        'usage: argdown', 'usage: tagmaps')
    # write argdown and argparse imports first
    source_file.write('import argparse\n')
    source_file.write('import argdown\n')
    source_file.write('from pathlib import Path\n')
    # fix argparse name
    parse_args_source = parse_args_source.replace(
        'ArgumentParser()', 'ArgumentParser(prog="tagmaps")')
    # write prepared source code
    source_file.write(parse_args_source)
    source_file.close()


# run script
extract_argscode()
