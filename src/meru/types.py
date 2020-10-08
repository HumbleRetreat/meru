from dataclasses import dataclass


@dataclass
class MeruObject:
    @property
    def object_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self):
        data = self.__dict__
        data['object_type'] = self.object_type
        return data

