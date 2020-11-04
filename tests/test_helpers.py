from meru.base import Action
from meru.helpers import build_address, get_full_path_to_class


def test_get_full_path_to_class():
    res = get_full_path_to_class(Action)

    assert res == 'meru.base.Action'


def test_build_address():
    res = build_address('127.0.0.1', 24051)

    assert res == 'tcp://127.0.0.1:24051'
