import json
from typing import Type

from meru.actions import Action
from meru.base import MeruObject
from meru.exceptions import ActionException
from meru.introspection import get_class_init_args, get_subclasses


def serialize_objects(obj):
    if hasattr(obj, 'to_dict'):
        data = obj.to_dict()
    else:
        data = obj.__dict__

    return data


def deserialize_objects(obj):
    if 'object_type' in obj.keys():
        subclass = get_subclasses(MeruObject)[obj['object_type']]

        if subclass:
            init_args = get_class_init_args(subclass)
            calling_args = [obj[arg] for arg in init_args]
            action = subclass(*calling_args)

            # Force timestamp to be added correctly to Actions.
            # Timestamp can not be found with getfullargsspec, since
            # it can not be in __init__.
            # see: https://bugs.python.org/issue36077
            if isinstance(action, Action):
                action.timestamp = obj['timestamp']

            return action
        raise ActionException(f'Object {obj["object_type"]} not found.')

    return obj


def encode_object(action: MeruObject):
    encoded_object = json.dumps(action, default=serialize_objects).encode()
    return encoded_object


def decode_object(state_data) -> Type[MeruObject]:
    data = json.loads(state_data, object_hook=deserialize_objects)
    return data
