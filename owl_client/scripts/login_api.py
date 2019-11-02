import getpass
import logging
import os
from argparse import Namespace
from pathlib import Path

import requests
import yaml

log = logging.getLogger(__name__)


def login_api(args: Namespace) -> None:  # pragma: nocover
    """Login to the API.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """
    username = input('Username: ')
    password = getpass.getpass()

    url = f'https://{args.api}/api/v1/login'
    data = {'username': username, 'password': password}
    try:
        r = requests.post(url, json=data)
        salt, secret = r.text.split('$')
    except Exception:
        print('Login failed')
        return

    owlrc = Path('~/.owlrc').expanduser()
    with owlrc.open(mode='w+') as fd:
        config = yaml.safe_load(fd.read())
        if config is None:
            config = {}
        config.update({'username': username, 'password': salt, 'secret': secret})
        config = yaml.dump(config)
        fd.seek(0)
        fd.write(config)

    os.chmod(f'{owlrc}', 0o600)
