import os
from distutils.util import strtobool

from meru.exceptions import MeruException

BIND_ADDRESS = os.environ.get("BIND_ADDRESS", "127.0.0.1")
BROKER_ADDRESS = os.environ.get("BROKER_ADDRESS", "127.0.0.1")

PUBLISHER_PORT = "24051"
COLLECTOR_PORT = "24052"
STATE_PORT = "24053"

SSH_TUNNEL = os.environ.get("SSH_TUNNEL", False)

MERU_SERIALIZATION_METHOD = os.environ.get("MERU_SERIALIZATION_METHOD", "json")
MERU_RECEIVE_TIMEOUT = int(os.environ.get("MERU_RECEIVE_TIMEOUT", 4000))

MERU_HOSTNAME_IN_IDENTITY = strtobool(os.environ.get("MERU_HOSTNAME_IN_IDENTITY", "true"))

if MERU_SERIALIZATION_METHOD not in ("json", "pickle"):
    raise MeruException(
        f'Setting MERU_SERIALIZATION_METHOD "{MERU_SERIALIZATION_METHOD}" not supported. Use either "json" or "pickle"'
    )
