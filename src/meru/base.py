"""Base classes for the communication"""

from dataclasses import dataclass, field
import time

from meru.helpers import get_process_identity


@dataclass
class MeruObject:
    """A base class for objects that are sent over a process-broker connection.

    Attributes:
        object_type: The name of the derived class

    See also:
        :py:class:`Action`
        :py:class:`StateNode`
    """

    @property
    def object_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self):
        """Converts ``self`` to a dictionary.

        Returns:
            A dictionary that contains the fields of ``self`` as entries.
        """
        data = self.__dict__.copy()
        data["object_type"] = self.object_type
        return data


@dataclass
class Action(MeruObject):
    """A base class for action message objects.

    Instances of derived classes are used as messages between processes.

    Attributes:
        origin: Identity of the sender process. See :py:func:`meru.helpers.get_process_identity`.
        topic: Can be used to group Actions.
        timestamp: Timestamp from the moment the Action was created (und usually sent).  Unix time in ms.
    """

    origin: str = field(
        init=False,
        repr=False,
    )
    topic = b""

    timestamp: float = field(
        init=False,
        repr=False,
    )

    def __post_init__(self):
        self.timestamp = int(time.time() * 1000)
        self.origin = get_process_identity()


# pylint: disable=protected-access,too-few-public-methods,no-member
@dataclass
class StateNode(MeruObject):
    """A base class for state objects.

    Instances of this class contain global state, i.e. state that is distributed by the broker
    to all connected processes.

    Each process maintains its own copy of the global state and updates it according to update
    actions received from the broker.

    See Also:
        :py:func:`meru.base.register_state`
    """

    pass
