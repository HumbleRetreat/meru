import inspect
import re


def underscore(word):
    """
    Make an underscored, lowercase form from the expression in the string.

    Example::

        >>> underscore("DeviceType")
        "device_type"

    """
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', word)
    word = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', word)
    word = word.replace("-", "_")
    return word.lower()


def get_full_path_to_class(cls: object):
    mod = cls.__module__
    name = cls.__name__

    return f'{mod}.{name}'


def inspect_action_handler(func):
    from meru.actions import Action
    from meru.state import StateNode

    found_action = None
    calling_args = {}
    signature = inspect.signature(func)

    for param in signature.parameters.values():
        if issubclass(param.annotation, Action):
            if found_action is not None:
                raise Exception('An action handler can have only one action.')
            found_action = param.annotation
            calling_args[param.name] = param.annotation
        elif issubclass(param.annotation, StateNode):
            calling_args[param.name] = param.annotation

    if found_action is None:
        raise Exception('An action handler needs one action.')

    return found_action, calling_args
