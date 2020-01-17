import logging
from argparse import Namespace
from pathlib import Path

import jwt
import requests
import yaml

log = logging.getLogger(__name__)


def logs_pipeline(args: Namespace) -> None:  # pragma: nocover
    """Cancel pipeline

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    log.debug('Canceling pipeline...')

    url = 'https://{}/api/v1/pipeline/logs'.format(args.api)

    owlrc = Path('~/.owlrc').expanduser()
    if not owlrc.exists():
        print('Cannot find authentication token. Please login first  "owl login"')
        return

    with owlrc.open(mode='r') as fd:
        auth = yaml.safe_load(fd.read())
        username, password, secret = auth['username'], auth['password'], auth['secret']
        token = jwt.encode({'username': username, 'password': password}, secret)
        token = token.decode('utf-8')
        headers = {'Authentication': '{} {}'.format(username, token)}

    try:
        r = requests.get(url, params={'jobid': args.jobid}, headers=headers)
        print(r.text)
    except Exception as e:
        print('Failed to cancel pipeline: ', e)
