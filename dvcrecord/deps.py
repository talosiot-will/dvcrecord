# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/deps.ipynb (unless otherwise specified).

__all__ = ['add_dvcr_commands', 'make_parser', 'DVC_RECORD_STRING', 'NoArgumentNamed', 'Dependency']

# Cell
import collections
import argparse

from dvcrecord import TrackedFile
from .utils import maybe_yaml

# Cell

DVC_RECORD_STRING = '--dvc_record'
def add_dvcr_commands(parser):
    parser.add_argument(DVC_RECORD_STRING, action='store_true', dest='dvc_record',
                        help='Include this flag to record the dvc params entries')
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
        self.deps = collections.OrderedDict({})

    def load(self, fpath, *args, **kwargs):
        tracked_file = self.deps.setdefault(fpath, TrackedFile(fpath, *args, **kwargs))
        return tracked_file

    def _from_cli(self, namespace=None, arg_name='dvc_dep'):
        namespace = namespace or self.namespace
        if namespace:
            try:
                return getattr(namespace, arg_name)
            except AttributeError:
                raise NoArgumentNamed("Looked for dvc file dependencies in an argument named '{}' but it wasnt in the command line".format(arg_name))
        else:
            return []

    def render(self, as_yaml=False, *args, **kwargs):
        returnme = [dep.render(as_yaml=False) for dep in self.deps.values()]
        returnme.extend(self._from_cli(*args, **kwargs))
        return maybe_yaml(returnme, as_yaml=as_yaml)