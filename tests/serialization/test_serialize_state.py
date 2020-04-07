from meru.serialization import decode_object, encode_object
from meru.state import StateField, StateNode


class StateLeaf(StateNode):
    leaf_prop = StateField(1)


class RootState(StateNode):
    root_prop = StateField(1)
    leaf = StateLeaf


serialized_state = b'{"leaf": {"leaf_prop": 1, "state_type": "StateLeaf"}, "root_prop": 1, "state_type": "RootState"}'


def test_encode_state():
    state = RootState()
    result = encode_object(state)
    assert result == serialized_state


def test_decode_state():
    result = decode_object(serialized_state)
    expected_state = RootState()

    assert result.state_type == expected_state.state_type
    assert result.root_prop == expected_state.root_prop
    assert result.leaf.state_type == expected_state.leaf.state_type
    assert result.leaf.leaf_prop == expected_state.leaf.leaf_prop
