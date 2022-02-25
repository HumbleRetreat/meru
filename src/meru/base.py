from dataclasses import dataclass, field
import time

from meru.helpers import get_process_identity


@dataclass
class MeruObject:
    @property
    def object_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self):
        data = self.__dict__
        data["object_type"] = self.object_type
        return data


@dataclass
class Action(MeruObject):
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
    pass
