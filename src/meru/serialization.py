"""Helpers related to de-/serialization."""
import json
import pickle
from dataclasses import fields

from meru.actions import Action
from meru.base import MeruObject
from meru.constants import MERU_SERIALIZATION_METHOD
from meru.exceptions import ActionException
from meru.introspection import get_subclasses


def serialize_objects(obj):
    """Serializes a Python object to a dictionary.

    If ``obj`` has a ``obj.to_dict()`` method, it is used instead of the builtin ``obj.__dict__()``.

    Parameters:
        obj: The object that should be serialized.

    Returns:
        A dictionary
    """
    if hasattr(obj, "to_dict"):
        data = obj.to_dict()
    else:
        data = obj.__dict__

    return data


def deserialize_objects(obj):
    """Deserializes an object from a dictionary.

    Parameter:
        obj: A dictionary containing the object's attributes.

    Returns:
        An object with the attributes in ``obj`` set to the specified values.  If the object's type
        can not be determined, ``obj`` is returned unchanged.
    """
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

            # Force timestamp and origin to be added correctly to Actions.
            # Both fields can not be found with getfullargsspec, since
            # it can not be in __init__.
            # see: https://bugs.python.org/issue36077
            if isinstance(action, Action):
                action.timestamp = obj["timestamp"]
                action.origin = obj["origin"]

            return action
        raise ActionException(f'Object {obj["object_type"]} not found.')

    return obj


def encode_object(action: any, method_override=None):
    """Serializes an action.

    The serialization method in :py:const:`meru.constants.MERU_SERIALIZATION_METHOD` is used if
    ``method_override`` is None.

    Parameters:
        action: The action to serialize.
        method_override: Can be used to override the default serialization method.

    Returns:
        The encoded object.

    See Also:
        :py:func:`decode_object`
    """
    if "json" in (MERU_SERIALIZATION_METHOD, method_override):
        encoded_object = json.dumps(action, default=serialize_objects).encode()
    else:
        encoded_object = pickle.dumps(action)

    return encoded_object


def decode_object(action: any, method_override=None):
    """Deserializes an action.

    The inverse operation to :py:func:`encoded_object`.

    The serialization method in :py:const:`meru.constants.MERU_SERIALIZATION_METHOD` is used if
    ``method_override`` is None.

    Parameters:
        action: The action to deserialize.
        method_override: Can be used to override the default serialization method.

    Returns:
        The decoded object.

    See Also:
        :py:func:`encode_object`
    """
    if "json" in (MERU_SERIALIZATION_METHOD, method_override):
        data = json.loads(action, object_hook=deserialize_objects)
    else:
        data = pickle.loads(action)
    return data
