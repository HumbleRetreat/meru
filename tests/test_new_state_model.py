from meru.new_state import SomeAction, SomeState, get_state, register_state, update_state


def test_foo():
    register_state(SomeState)

    update_state(SomeAction('nice'))

    foo = get_state(SomeState)
    pass
