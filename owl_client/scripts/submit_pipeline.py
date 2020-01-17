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


def submit_pipeline(args: Namespace) -> None:
    """Add pipeline to queue.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    log.debug('Submitting pipeline to queue...')
    conf = read_config(args.conf)

    url = 'https://{}/api/v1/pipeline/add'.format(args.api)
    data = {'config': conf}
    owlrc = Path('~/.owlrc').expanduser()
    if not owlrc.exists():
        print('Cannot find authentication token. Please login first  "owl login"')
        return

    with owlrc.open(mode='r') as fd:
        auth = yaml.safe_load(fd.read())
        username, password, secret = auth['username'], auth['password'], auth['secret']
        token_bytes = jwt.encode({'username': username, 'password': password}, secret)
        token = token_bytes.decode('utf-8')
        headers = {'Authentication': '{} {}'.format(username, token)}

    try:
        r = requests.post(url, json=data, headers=headers)
        job_id = int(r.text)
        print(success_msg % job_id)
    except ValueError as err:
        print('Failed to submit pipeline. Authentication failed. %s ' % err)
    except Exception as err:
        print('Failed to submit pipeline: %s' % err)
