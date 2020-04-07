import datetime
import inspect
import json
from pathlib import Path

import ciso8601

from meru.actions import Action
from meru.exceptions import ActionException
from meru.state import StateNode


def serialize_objects(obj):
    if hasattr(obj, 'to_dict'):
        data = obj.to_dict()
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        data = obj.isoformat()
    elif isinstance(obj, Path):
        data = str(obj)
    else:
        data = obj.__dict__

    return data


def deserialize_objects(obj):
    if 'action_type' in obj.keys():
        for subclass in Action.__subclasses__():
            if subclass.__name__ == obj['action_type']:
                calling_args = []
                args = inspect.getfullargspec(subclass.__init__)

                for arg in args.args:
                    if arg == 'self':
                        continue

                    calling_args.append(obj[arg])

                action = subclass(*calling_args)

                action.timestamp = ciso8601.parse_datetime(obj['timestamp'])

                return action
        raise ActionException(f'Action {obj["action_type"]} not found')

    if 'state_type' in obj.keys():
        for subclass in StateNode.__subclasses__():
            if subclass.__name__ == obj['state_type']:
                fields = {}
                for field in subclass._fields.keys():
                    fields[field] = obj[field]

                state = subclass(fields=fields)

                return state
        raise ActionException(f'StateNode {obj["state_type"]} not found')

    return obj


def encode_object(action: Action):
    encoded_object = json.dumps(action, default=serialize_objects).encode()
    return encoded_object


def decode_object(state_data):
    data = json.loads(state_data, object_hook=deserialize_objects)
    return data
