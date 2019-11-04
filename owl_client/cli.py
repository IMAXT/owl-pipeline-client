import logging
import logging.config
import os
import sys
from argparse import ArgumentParser, FileType, Namespace
from typing import List

from owl_client.scripts import login_api, run_standalone, submit_pipeline

log = logging.getLogger(__name__)

OWL_API_URL = os.environ.get('OWL_API_URL', 'imaxt.ast.cam.ac.uk')


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

    # Login
    login = subparsers.add_parser('login')
    login.add_argument('--api', required=False, type=str, default=OWL_API_URL)
    login.set_defaults(func=login_api)

    # Submit
    submit = subparsers.add_parser('submit')
    submit.add_argument('conf', type=FileType('r'))
    submit.add_argument('--api', required=False, type=str, default=OWL_API_URL)
    submit.set_defaults(func=submit_pipeline)

    # Execute
    execute = subparsers.add_parser('execute')
    execute.add_argument('conf', type=FileType('r'))
    execute.set_defaults(func=run_standalone)

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
