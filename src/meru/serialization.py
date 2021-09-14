import json
import pickle

from meru.actions import Action
from meru.base import MeruObject
from meru.constants import MERU_SERIALIZATION_METHOD
from meru.exceptions import ActionException
from meru.helpers import get_subclasses
from meru.introspection import get_subclasses


def serialize_objects(obj):
    if hasattr(obj, "to_dict"):
        data = obj.to_dict()
    else:
        data = obj.__dict__

    return data


def deserialize_objects(obj):
    from dataclasses import fields

    if "object_type" in obj.keys():
        subclass = get_subclasses(MeruObject)[obj["object_type"]]

        if subclass:
            calling_args = []
            for field in fields(subclass):
                if not field.init:
                    continue

                cast_to = field.metadata.get("cast", None)
                if cast_to:
                    calling_args.append(cast_to(obj[field.name]))
                else:
                    calling_args.append(obj[field.name])
            action = subclass(*calling_args)

            # Force timestamp to be added correctly to Actions.
            # Timestamp can not be found with getfullargsspec, since
            # it can not be in __init__.
            # see: https://bugs.python.org/issue36077
            if isinstance(action, Action):
                action.timestamp = obj["timestamp"]

            return action
        raise ActionException(f'Object {obj["object_type"]} not found.')

    return obj


def encode_object(action: any, method_override=None):
    if "json" in (MERU_SERIALIZATION_METHOD, method_override):
        encoded_object = json.dumps(action, default=serialize_objects).encode()
    else:
        encoded_object = pickle.dumps(action)

    return encoded_object


def decode_object(action: any, method_override=None):
    if "json" in (MERU_SERIALIZATION_METHOD, method_override):
        data = json.loads(action, object_hook=deserialize_objects)
    else:
        data = pickle.loads(action)
    return data
