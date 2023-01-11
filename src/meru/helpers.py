"""Functionality related to action handlers."""
import os
import socket
from datetime import datetime
from functools import lru_cache
from importlib import import_module
from typing import Type

from meru.constants import MERU_HOSTNAME_IN_IDENTITY


def get_full_path_to_class(cls: Type) -> str:
    """Returns the absolute class name for a class.

    Parameters:
        cls: A Python class.

    Returns:
        The class name prefixed with the full module path.

    See Also:
        :py:func:`get_type_from_string`
    """
    mod = cls.__module__
    name = cls.__name__

    return f"{mod}.{name}"


def get_type_from_string(cls_path: str) -> Type:
    """Returns the class specified by the given absolute class name.

    This is the inverse operation to :py:func:`get_full_path_to_class`.

    Parameters:
        cls_path: The absolute class name.

    Returns:
        The corresponding Python class object.

    See Also:
        :py:func:`get_full_path_to_class`
    """
    module_name, class_name = cls_path.rsplit(".", 1)
    return getattr(import_module(module_name), class_name)


def build_address(ip_address, port):
    """Build a TCP URL from the address and port."""
    return f"tcp://{ip_address}:{port}"


@lru_cache
def get_process_identity():
    """
    Get the identity for the current process. There are 4 possible outcomes:

        - Hostname is not disabled and process name is set: Identity will contain hostname and process.
        - Hostname is not disabled, process name not set: Identity will contain hostname and a random
          string based on current time.
        - Hostname is disabled, process name is set: Identity will be only the process name.
        - Hostname is disabled, process name not set. Identity will be a random string based on time.

    To disable the hostname in the identity, set the `MERU_HOSTNAME_IN_IDENTITY` environment variable to 0
    :return:
    """
    out = ""
    if MERU_HOSTNAME_IN_IDENTITY:
        hostname = socket.gethostname()
        out += hostname + "-"

    process_name = os.environ.get("MERU_PROCESS", None)
    if not process_name:
        now = datetime.now()
        out += "t" + now.strftime("%M%S%f")
    else:
        out += process_name

    return out
