import logging
import os
import re
import socket
import traceback
from contextlib import closing, suppress
from functools import wraps
from typing import IO, Any, Callable, Dict, Union, NamedTuple

import pkg_resources
import yaml
from distributed import Client

import voluptuous as vo

log = logging.getLogger('owl.cli')


_path_matcher = re.compile(r'(\S+)?(\$\{([^}^{]+)\})')


class Pipeline(NamedTuple):
    main: Callable
    schema: vo.Schema


_injected_pipelines: Dict[str, Pipeline] = {}


def inject_pipeline(name: str, fn: Callable, schema: vo.Schema = None):
    _injected_pipelines[name] = Pipeline(main=fn, schema=schema)


def _path_constructor(loader, node):
    """Extract the matched value, expand env variable, and replace the match.
    """
    value = node.value
    match = _path_matcher.match(value)
    env_var = match.groups()[2]
    return value.replace(match.groups()[1], os.environ.get(env_var, ''))


yaml.add_implicit_resolver('!path', _path_matcher, None, yaml.SafeLoader)
yaml.add_constructor('!path', _path_constructor, yaml.SafeLoader)


def read_config(
    config: Union[str, IO[str]], validate: Callable = None
) -> Dict[str, Any]:
    """Read configuration file.

    Parameters
    ----------
    config
        input configuration
    validate
        validation schema

    Returns
    -------
    parsed configuration
    """
    try:
        conf = yaml.safe_load(config)
    except:  # noqa
        log.critical('Unable to read configuration file.')
        raise
    if validate:
        conf = validate(conf)
    return conf


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        for n in range(6006, 7006, 10):
            with suppress(OSError):
                s.bind(('', n))
                break
        return n


def get_pipeline(name: str) -> Callable:
    f = find_pipeline(name)
    s = f.schema
    s.extra = vo.REMOVE_EXTRA
    return register_pipeline(validate=s)(f)


def find_pipeline(name: str) -> Pipeline:
    if name in _injected_pipelines:
        return _injected_pipelines[name]
    for e in pkg_resources.iter_entry_points('owl.pipelines'):
        if e.name == name:
            return e.load()
    raise Exception('Pipeline %s not found', name)


class register_pipeline:
    """Register a pipeline.
    """

    def __init__(self, *, validate: vo.Schema = None):
        self.schema = validate
        if self.schema is not None:
            self.schema.extra = vo.REMOVE_EXTRA

    def __call__(self, func: Pipeline) -> Callable:
        @wraps(func.main)
        def wrapper(config: Dict, logconfig: Dict, cluster=None):

            if self.schema is not None:
                _config = self.schema(config)
            else:
                _config = config

            if cluster is not None:
                try:
                    client = Client(cluster.scheduler_address)
                except Exception:
                    traceback_str = traceback.format_exc()
                    raise Exception(
                        'Error occurred. Original traceback ' 'is\n%s\n' % traceback_str
                    )
            else:
                client = None
            try:
                func.main.config = config  # type: ignore
                return func.main(**_config)  # type: ignore
            except Exception:
                traceback_str = traceback.format_exc()
                raise Exception(
                    'Error occurred. Original traceback ' 'is\n%s\n' % traceback_str
                )
            finally:
                if client is not None:
                    client.close()

        return wrapper
