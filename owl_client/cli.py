import logging
import logging.config
import sys
from argparse import ArgumentParser, FileType, Namespace
from typing import List

from owl_client.scripts import run_standalone

log = logging.getLogger(__name__)


def parse_args(input: List[str]) -> Namespace:
    """Parse command line arguments.

    Parameters
    ----------
    input
        list of command line arguments

    Returns
    -------
    parsed arguments
    """
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # Pipeline
    pipeline = subparsers.add_parser('pipeline').add_subparsers()

    # ... run
    pipeline_submit = pipeline.add_parser('run')
    pipeline_submit.add_argument('--conf', required=True, type=FileType('r'))
    pipeline_submit.set_defaults(func=run_standalone)

    args = parser.parse_args(input)
    if not hasattr(args, 'func'):
        parser.print_help()

    return args


def main():
    """Main entry point for owl.

    Invoke the command line help with::

        $ owl --help

    """
    args = parse_args(sys.argv[1:])

    if hasattr(args, 'func'):
        args.func(args)
