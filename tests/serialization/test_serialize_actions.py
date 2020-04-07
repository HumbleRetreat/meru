from freezegun import freeze_time

from meru.actions import Action
from meru.serialization import decode_object, encode_object


class DummyAction(Action):
    pass


encoded_action = b'{"timestamp": "2017-05-24T00:00:00", "action_type": "DummyAction"}'


def test_encode_action():
    with freeze_time('2017-05-24'):
        action = DummyAction()

    result = encode_object(action)
    assert result == encoded_action


def test_decode_action():
    action = decode_object(encoded_action)

    with freeze_time('2017-05-24'):
        expected_action = DummyAction()

    assert action.action_type == expected_action.action_type
    assert action.timestamp == expected_action.timestamp
    assert action.topic == action.topic
