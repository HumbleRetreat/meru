import asyncio

import pytest

from meru.actions import Action


class DummyAction(Action):
    pass


@pytest.yield_fixture()
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture()
def wait():
    def gen_sleep():
        return asyncio.sleep(0.1)

    return gen_sleep


@pytest.fixture()
def dummy_action():
    return DummyAction
