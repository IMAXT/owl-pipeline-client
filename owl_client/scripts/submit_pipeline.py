import logging
from argparse import Namespace
from pathlib import Path

import jwt
import requests
import yaml

from owl_client.utils import read_config

log = logging.getLogger(__name__)

success_msg = """
Job ID %d submitted.
"""


def submit_pipeline(args: Namespace) -> None:  # pragma: nocover
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    log.debug('Submitting pipeline to queue...')
    conf = read_config(args.conf)

    url = f'http://{args.api}/api/v1/pipeline/add'
    data = {'config': conf}

    with Path('~/.owlrc').expanduser().open(mode='r') as fd:
        auth = yaml.safe_load(fd.read())
        username, password, secret = auth['username'], auth['password'], auth['secret']
        token = jwt.encode({'username': username, 'password': password}, secret)
        token = token.decode('utf-8')
        headers = {'Authentication': f'{username} {token}'}

    try:
        r = requests.post(url, json=data, headers=headers)
        job_id = int(r.text)
        err = ''
        print(success_msg % job_id)
    except ValueError:
        print('Failed to submit pipeline. Authentication failed.')
        err = 'Authentication failed.'
        job_id = None
    except Exception as err:
        print('Failed to submit pipeline: ', err)
        job_id = None

    return (job_id, err)
