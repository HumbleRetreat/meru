from dataclasses import dataclass, field
from typing import Union

from meru.actions import Action
from meru.new_state import get_state, NewStateModel, register_state, update_state
from meru.serialization import decode_object, encode_object


@dataclass
class FooAction(Action):
    device_name: str
    counter: int


@dataclass
class BarAction(Action):
    counter: int


@dataclass
class DummyState(NewStateModel):
    devices: list = field(default_factory=lambda: [])
    counter: int = field(default=0)

    def handle_devices(self, action: FooAction):
        self.devices.append(action.device_name)

    def handle_all(self, action: Union[FooAction, BarAction]):
        self.counter += action.counter


def test_foo():
    register_state(DummyState)

    update_state(FooAction('device_name', 5))

    foo = get_state(DummyState)

    assert foo.devices == ['device_name']


def test_bar():
    register_state(DummyState)

    update_state(FooAction('device_name', 5))
    update_state(BarAction(2))

    foo = get_state(DummyState)

    assert foo.devices == ['device_name']
    assert foo.counter == 7


def test_serialize_new_state():
    register_state(DummyState)

    update_state(FooAction('device_name', 5))
    update_state(BarAction(2))

    foo = get_state(DummyState)

    res = encode_object(foo)

    res2 = decode_object(res)
    pass
