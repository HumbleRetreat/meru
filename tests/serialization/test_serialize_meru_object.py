from freezegun import freeze_time

from meru.serialization import decode_object, encode_object

encoded_object = b'{"object_type": "DummyObject"}'
encoded_action = b'{"timestamp": 1495584000000, "origin": "does not matter", "object_type": "DummyAction"}'


def test_encode_custom_object(dummy_object):
    obj = dummy_object()
    res = encode_object(obj)

    assert res == encoded_object


def test_decode_custom_object(dummy_object):
    custom_object = decode_object(encoded_object)

    assert custom_object == dummy_object()


def test_encode_action(dummy_action):
    with freeze_time('2017-05-24'):
        action = dummy_action()
        action.origin = "does not matter"

    result = encode_object(action)
    assert result == encoded_action


def test_decode_action(dummy_action):
    action = decode_object(encoded_action)

    with freeze_time('2017-05-24'):
        expected_action = dummy_action()
        expected_action.origin = "does not matter"

    assert action.object_type == expected_action.object_type
    assert action.timestamp == expected_action.timestamp
    assert action.topic == action.topic
