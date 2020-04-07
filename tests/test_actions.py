import time

from meru.actions import Action


class DummyAction(Action):
    pass


def test_serialization_roundtrip():
    action = DummyAction()
    # assert action.decode(a) == action
