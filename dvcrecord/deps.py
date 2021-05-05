# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/deps.ipynb (unless otherwise specified).

__all__ = ['logger', 'add_dvcr_commands', 'make_parser', 'DVC_RECORD_STRING', 'DVC_DRY_RUN',
           'DO_NOT_INCLUDE_IN_PIPELINE', 'NoArgumentNamed', 'Dependency']

# Cell
import os
import sys
import logging
logger = logging.getLogger()
import collections
import argparse

from .utils import maybe_yaml

# Cell

DVC_RECORD_STRING = '--dvc_record'
DVC_DRY_RUN = '--dvc_dryrun'
DO_NOT_INCLUDE_IN_PIPELINE = [DVC_RECORD_STRING, DVC_DRY_RUN]

def add_dvcr_commands(parser):
    parser.add_argument(DVC_RECORD_STRING, action='store_true', dest='dvc_record',
                        help='Include this flag to record the dvc params entries')
    parser.add_argument(DVC_DRY_RUN, action='store_true', dest='dvc_dryrun',
                        help='Include this flag to not actually write the dvc.yaml but just display the params that would be written')
    parser.add_argument('--dvc_dep', action='append', nargs='?',
                        help='Filepaths to the dependency inputs')
    return parser

def make_parser(parser=None):
    parser = parser or argparse.ArgumentParser(description='Stock parser for dvcrecord commands')
    parser = add_dvcr_commands(parser)
    return parser

# Cell

class NoArgumentNamed(Exception):
    pass

class Dependency:
    def __init__(self, namespace=None):
        self.namespace = namespace
        self.deps = []

    def register(self, *args):
        fpath = os.path.join(*args)
        if fpath not in self.deps:
            self.deps.append(fpath)
        return fpath

    def from_cli(self, namespace=None, arg_name='dvc_dep'):
        namespace = namespace or self.namespace
        if namespace:
            try:
                return getattr(namespace, arg_name)
            except AttributeError:
                logger.info("Looked for dvc file dependencies in an argument named '{}' but it wasnt in the command line".format(arg_name))
                return []
        else:
            return []

    def register_param(self, param):
        for fpath in param.list_of_files():
            self.register(fpath)

    def register_sourcecode(self, command=None):
        command = command or sys.argv[:]
        self.register(command[0])

    def render(self, as_yaml=False, *args, **kwargs):
        returnme = self.deps[:]

        deps_in_cli = self.from_cli(*args, **kwargs)
        if deps_in_cli:
            returnme.extend(deps_in_cli)
        return maybe_yaml(returnme, as_yaml=as_yaml)
