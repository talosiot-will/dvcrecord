# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/stage.ipynb (unless otherwise specified).

__all__ = ['PipelineStage']

# Cell
import sys
import yaml
import atexit

from .params import Params
from .deps import Dependency, make_parser, DO_NOT_INCLUDE_IN_PIPELINE
from .output import Output
from .utils import maybe_yaml, write_yaml, PIPELINE_FILE_DEFAULT

class PipelineStage:
    def __init__(self, name, params=None, outputs=None, deps=None, parser=None):
        self.name = name
        self.parser = parser or make_parser()

        self.outputs = outputs or Output()
        self.params = params or Params()
        self.deps = deps or Dependency(namespace=self.parse_args())

        self.rendering_funcs = {
            'params': self.params.render,
            'deps': self.deps.render,
            'outs': self.outputs.render
            }
        self.atexit_actions()

    def atexit_actions(self):
        ns = self.parse_args()
        if ns is None:
            return None
        if ns.dvc_dryrun:
            atexit.register(self.show_render)
        elif ns.dvc_record:
            atexit.register(self.write)

    def parse_args(self, *args, **kwargs):
        if self.parser is None:
            return None
        else:
            known, unknown = self.parser.parse_known_args(*args, **kwargs)
            return known

    def render_cmd(self, cli_args=None):
        cli_args = cli_args or sys.argv[:]
        cli_args = ['python'] + cli_args
        return ' '.join([arg for arg in cli_args if arg not in DO_NOT_INCLUDE_IN_PIPELINE])

    def render(self, as_yaml=False):
        dvc_config = {}

        self.deps.register_sourcecode()
        self.deps.register_param(self.params)

        for key, render_func in self.rendering_funcs.items():
            this_yaml = render_func(as_yaml=False)
            if this_yaml:
                dvc_config[key] = this_yaml

        dvc_config['cmd'] = self.render_cmd()
        return maybe_yaml(dvc_config, as_yaml=as_yaml)

    def show_render(self):
        print(self.render(as_yaml=True))

    def write(self, pipefile=None):
        pipefile = pipefile or PIPELINE_FILE_DEFAULT
        try:
            with open(pipefile, 'r') as f:
                pipeline = yaml.safe_load(f)
        except FileNotFoundError:
            pipeline = {'stages': {}}

        pipeline['stages'][self.name] = self.render(as_yaml=False)
        write_yaml(pipeline, fname=pipefile)
        return pipeline