import os

import pytest

from meru.base import Action
from meru.helpers import build_address, get_full_path_to_class, get_process_identity


def test_get_full_path_to_class():
    res = get_full_path_to_class(Action)

    assert res == 'meru.base.Action'


def test_build_address():
    res = build_address('127.0.0.1', 24051)

    assert res == 'tcp://127.0.0.1:24051'


def test_get_identity_full(mocker):
    mocker.patch("socket.gethostname", return_value="pytesthost")
    mocker.patch.dict(os.environ, {"MERU_PROCESS": "meru_process"})
    process_identity = get_process_identity()

    assert process_identity == "pytesthost-meru_process"


@pytest.mark.freeze_time('2017-05-24 15:42:12')
def test_get_identity_without_hostname(mocker):
    mocker.patch("meru.helpers.MERU_HOSTNAME_IN_IDENTITY", False)
    process_identity = get_process_identity()

    assert process_identity == "t4212000000"


@pytest.mark.freeze_time('2017-05-24 15:42:12')
def test_get_identity_without_process(mocker):
    mocker.patch("socket.gethostname", return_value="pytesthost")
    process_identity = get_process_identity()

    assert process_identity == "pytesthost-t4212000000"


@pytest.mark.freeze_time('2017-05-24 15:42:12')
def test_get_identity_no_hostname_no_process(mocker):
    mocker.patch("meru.helpers.MERU_HOSTNAME_IN_IDENTITY", False)
    process_identity = get_process_identity()

    assert process_identity == "t4212000000"
