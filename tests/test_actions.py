from meru.actions import RequireState, StateUpdate, discover_actions, get_all_actions
from meru.base import Action


def test_get_all_actions():
    discover_actions('meru.actions')
    actions = get_all_actions()

    assert Action in actions.values()
    assert RequireState in actions.values()
    assert StateUpdate in actions.values()
