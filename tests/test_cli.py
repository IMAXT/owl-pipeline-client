import json
import sys

import pytest
import yaml.parser

from owl_client.cli import main
from owl_client.utils import find_free_port, read_config


def test_read_config():
    config = {"key": "value"}
    res = read_config(json.dumps(config))
    assert res == config

    with pytest.raises(yaml.parser.ParserError):
        read_config('{"a": 1')


def test_find_port():
    port = find_free_port()
    assert port == 6006


def test_cli_nofunc(mocker, capsys):
    mocker.patch.object(sys, "argv")
    sys.argv = [""]
    main()
    captured = capsys.readouterr()
    assert "usage" in captured.out
    assert "help" in captured.out
