import logging
import logging.config
import os
import signal
import sys
import tempfile
import time
from argparse import Namespace
from contextlib import closing
import traceback
import voluptuous as vo
from typing import Callable, Dict, Any, List, Union

from distributed import Client, LocalCluster, SpecCluster
from dask_jobqueue import *

from owl_client.formatting import ArithmeticFormatter
from owl_client.utils import find_free_port, get_pipeline, read_config

logconf = """
version: 1
handlers:
  console:
    class: logging.StreamHandler
    formatter: standard
    stream: 'ext://sys.stderr'
  file:
    class: logging.FileHandler
    filename: owl.log
    mode: w
    formatter: standard
formatters:
  standard:
    format: '%(asctime)s PIPELINE %(levelname)s %(name)s %(funcName)s | %(message)s'
loggers:
  owl.daemon.pipeline:
    handlers: [console, file]
    level: ${LOGLEVEL}
  prefect.TaskRunner:
    handlers: [console, file]
    level: ${LOGLEVEL}
    propagate: False
  prefect.FlowRunner:
    handlers: [console, file]
    level: ${LOGLEVEL}
    propagate: False
"""

log = logging.getLogger('owl.daemon.pipeline')

os.environ['LOGLEVEL'] = os.environ.get('LOGLEVEL', 'DEBUG')
os.environ['OMP_NUM_THREADS'] = '1'


def terminate(*args):  # pragma: nocover
    log.info('Terminating...')
    try:
        client = Client.current()
        client.close()
        client.cluster.close()
    except:  # noqa: E722
        pass
    sys.exit(1)


clusterList = [MoabCluster, PBSCluster, SLURMCluster, SGECluster, LSFCluster, OARCluster, HTCondorCluster]
clusterMap: Dict[str, Callable[..., SpecCluster]] = {c.config_name: c for c in clusterList}

clusterSchema = vo.Schema({
    vo.Required("type"): str,
    vo.Required("cores", default="{threads}"): vo.Coerce(str),
    vo.Required("memory", default="{memory}GB"): str,
    vo.Required("local_directory", default="{local_directory}"): str,
    vo.Required("dashboard_address", default="localhost:{port + 1}"): str,
    vo.Required("walltime", default="24:00:00"): vo.Coerce(str),
    vo.Required("n_workers", default="{workers}"): vo.Coerce(str)
}, extra=vo.ALLOW_EXTRA)

formatter = ArithmeticFormatter()


def format_conf(obj: Union[Dict, List, str], **kwargs):
    if isinstance(obj, List):
        return [format_conf(e, **kwargs) for e in obj]
    elif isinstance(obj, Dict):
        return {k: format_conf(v, **kwargs) for k, v in obj.items()}
    elif isinstance(obj, str):
        f = formatter.format(obj, **kwargs)
        try:
            return int(f)
        except ValueError:
            return f
    else:
        return obj


def createCluster(conf: Dict[str, Any], port, local_directory) -> SpecCluster:
    f"""
    Creates a cluster based on "cluster" section of the configuration file
    uses it's "type" attribute to determine the type of cluster to use
    and the rest if it's attributes a kwargs to the chosen constructor see below.
    These attributes will be formatted with the :func:'~formatting.ArithmeticFormatter
    using the kwargs: [port, local_directory] referring the the parameters of the function
    and [threads, memory, workers] referring to attributes in the recourse section of the config file.
    
    The available types are:
    {clusterMap}

    If the "cluster" section doesn't exit a local cluster will be created
    :param conf: configuration file
    :param port: default port
    :param local_directory: temporary local directory
    :return: the cluster
    """
    resources = conf.get('resources', {})
    n_workers = resources.get('workers', 2)
    threads = resources.get('threads', 2)
    memory = resources.get('memory', 7)
    if "cluster" in conf:
        cluster_conf: Dict[str, Any] = clusterSchema(conf["cluster"])
        cluster_conf = format_conf(cluster_conf, threads=threads, memory=memory, port=port,
                                   local_directory=local_directory, workers=n_workers)
        cluster_type: str = cluster_conf.pop("type")
        if cluster_type not in clusterMap:
            raise ValueError(f"{cluster_type} is not a valid type of cluster \n Please use on of {clusterMap.keys()}")
        constructor = clusterMap[cluster_type]
        return constructor(**cluster_conf)
    else:
        return LocalCluster(
            n_workers=n_workers,
            threads_per_worker=threads,
            scheduler_port=port,
            dashboard_address='localhost:{}'.format(port + 1),
            memory_limit='{}GB'.format(memory),
            local_directory=local_directory
        )


def run_standalone(args: Namespace) -> None:  # pragma: nocover
    """Run worker pipeline.

    Parameters
    ----------
    args
        Argparse namespace containing command line flags.
    """

    global logconf

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)

    conf = read_config(args.conf)

    log_config = read_config(logconf)
    logging.config.dictConfig(log_config)

    func = get_pipeline(conf['name'])

    port = find_free_port()

    tmpdir = os.environ.get('TMP_DIR', '/tmp')
    with tempfile.TemporaryDirectory(dir=tmpdir) as local_directory:
        with closing(
                createCluster(conf, port, local_directory)
        ) as cluster:
            log.info('Running diagnostics interface in http://localhost:%s', port + 1)
            log.info('Starting pipeline %r', conf['name'])
            log.debug('Configuration %s', conf)
            watch = time.monotonic()
            if args.debug:
                log.info('Running in debug mode')
                import dask.config

                dask.config.set(scheduler='single-threaded')
            try:
                func(conf, log_config, cluster=cluster)
            except Exception:
                tb = traceback.format_exc()
                log.critical(f'{tb!r}')
                raise
    log.info('Elapsed time %fs', time.monotonic() - watch)
