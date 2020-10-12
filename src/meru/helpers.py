from functools import lru_cache
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


def build_address(ip, port):
    return f'tcp://{ip}:{port}'
