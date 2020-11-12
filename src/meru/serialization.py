import datetime
import json
from pathlib import Path

from meru.actions import Action
from meru.exceptions import ActionException
from meru.helpers import get_subclasses
from meru.state import StateNode
from meru.types import MeruObject


def serialize_objects(obj):
    if hasattr(obj, 'to_dict'):
        data = obj.to_dict()
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        data = obj.isoformat()
    elif isinstance(obj, Path):
        data = str(obj)
    elif isinstance(obj, set):
        data = list(obj)
    else:
        data = obj.__dict__

    return data


def deserialize_objects(obj):
    from dataclasses import fields
    if 'object_type' in obj.keys():
        subclass = get_subclasses(MeruObject)[obj['object_type']]

        if subclass:
            calling_args = []
            for field in fields(subclass):
                cast_to = field.metadata.get('cast', None)
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
                action.timestamp = obj['timestamp']

            return action
        raise ActionException(f'Object {obj["object_type"]} not found.')

    if 'state_type' in obj.keys():
        subclass = get_subclasses(StateNode)[obj['state_type']]
        if subclass:
            fields = {}
            for field in subclass._fields.keys():
                fields[field] = obj[field]

            state = subclass(fields=fields)

            return state
        raise ActionException(f'StateNode {obj["state_type"]} not found')

    return obj


def encode_object(action: any):
    encoded_object = json.dumps(action, default=serialize_objects).encode()
    return encoded_object


def decode_object(state_data):
    data = json.loads(state_data, object_hook=deserialize_objects)
    return data
