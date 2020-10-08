from dataclasses import dataclass

from meru.actions import Action
from meru.serialization import encode_object, decode_object
from meru.types import MeruObject


@dataclass
class MeruObjectToTest(MeruObject):
    field: str


@dataclass
class DummyAction(Action):
    wtf: int


encoded_object = b'{"field": "value", "object_type": "MeruObjectToTest"}'


def test_encode_custom_object():
    obj = MeruObjectToTest('value')
    res = encode_object(obj)

    assert res == encoded_object


def test_decode_custom_object():
    custom_object = decode_object(encoded_object)

    assert custom_object == MeruObjectToTest(field='value')
