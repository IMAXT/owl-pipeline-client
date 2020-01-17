import logging
import logging.config
import os
import sys
from argparse import ArgumentParser, FileType, Namespace
from typing import List

from owl_client.scripts import (
    cancel_pipeline,
    login_api,
    logs_pipeline,
    run_standalone,
    status_pipeline,
    submit_pipeline,
)

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
    execute.add_argument('--debug', action='store_true')
    execute.set_defaults(func=run_standalone)

    # Cancel
    cancel = subparsers.add_parser('cancel')
    cancel.add_argument('jobid')
    cancel.add_argument('--api', required=False, type=str, default=OWL_API_URL)
    cancel.set_defaults(func=cancel_pipeline)

    # Status
    status = subparsers.add_parser('status')
    status.add_argument('jobid')
    status.add_argument('--api', required=False, type=str, default=OWL_API_URL)
    status.set_defaults(func=status_pipeline)

    # Logs
    logs = subparsers.add_parser('logs')
    logs.add_argument('jobid')
    logs.add_argument('--api', required=False, type=str, default=OWL_API_URL)
    logs.set_defaults(func=logs_pipeline)

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
