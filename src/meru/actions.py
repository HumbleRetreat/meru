"""Actions for the functionality included in meru.

The module also holds a global list of all available Actions which is populated by calling
:py:func:`discover_actions`.

"""

from dataclasses import dataclass
from importlib import import_module
import inspect
from typing import List

from meru.base import Action, StateNode
from meru.helpers import get_full_path_to_class


@dataclass
class StateUpdate(Action):
    """Sent to the broker to request the current state.

    Properties:
        nodes: Parts of the global state for which the state is requested.
    """

    topic = b"StateUpdate"

    nodes: List[StateNode]


@dataclass
class Ping(Action):
    """Sent from a process to the broker to check the connection.

    See Also:
        :py:class:`Pong`
        :py:func:`meru.handlers.ping_pong`
    """

    pass


@dataclass
class Pong(Action):
    """Answer to a ping back to the process.

    See Also:
        :py:class:`Ping`
        :py:func:`meru.handlers.ping_pong`
    """

    pass


@dataclass
class RequireState(Action):
    """Sent to the broker to request the current state.

    Properties:
        nodes: Parts of the global state for which the state is requested.

            Each entry is an absolute class name of the corresponding :py:class:`StateNode`.
    """

    topic = b"state"

    nodes: List[str]

    def to_dict(self):
        sup = super().to_dict()
        sup["nodes"] = [get_full_path_to_class(obj) for obj in sup["nodes"]]
        return sup


_all_actions = {}


def discover_actions(path: str):
    """Scans a module for :py:class:`Action` classes.

    All classes deriving from :py:class:`Action` are added to the global list.  This function does
    not recurse into submodules.

    Parameters:
        path: The absolute name of a python module to scan.
    """
    mod = import_module(path)

    for _, cls in inspect.getmembers(mod, inspect.isclass):
        if issubclass(cls, Action):
            _all_actions[cls.__name__] = cls


def get_all_actions():
    """Returns the global list of available actions."""
    return _all_actions
