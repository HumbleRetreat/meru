from freezegun import freeze_time

from meru.serialization import decode_object, encode_object

encoded_action = b'{"timestamp": 1495584000.0, "object_type": "DummyAction"}'


def test_encode_action(dummy_action):
    with freeze_time('2017-05-24'):
        action = dummy_action()

    result = encode_object(action)
    assert result == encoded_action


def test_decode_action(dummy_action):
    action = decode_object(encoded_action)

    with freeze_time('2017-05-24'):
        expected_action = dummy_action()

    assert action.object_type == expected_action.object_type
    assert action.timestamp == expected_action.timestamp
    assert action.topic == action.topic
