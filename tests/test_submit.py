import json
from argparse import Namespace
from unittest.mock import Mock, patch

import requests

from owl_client.scripts import submit_pipeline


@patch.object(requests, 'post')
def test_submit_ok(mockpost, capsys):
    mockresponse = Mock()
    mockpost.return_value = mockresponse
    mockresponse.text = '22'
    conf = json.dumps({'key': 'value'})
    ns = Namespace(api='localhost', conf=conf)
    submit_pipeline(ns)
    out, err = capsys.readouterr()
    assert '22' in out


@patch.object(requests, 'post')
def test_failed_login(mockpost, capsys):
    mockresponse = Mock()
    mockpost.return_value = mockresponse
    mockresponse.text = 'ff'
    conf = json.dumps({'key': 'value'})
    ns = Namespace(api='localhost', conf=conf)
    submit_pipeline(ns)
    out, err = capsys.readouterr()
    assert 'Authentication' in out


def test_failed_submit(capsys):
    conf = json.dumps({'key': 'value'})
    ns = Namespace(api='localhost', conf=conf)
    submit_pipeline(ns)
    out, err = capsys.readouterr()
    assert 'Failed to submit' in out
