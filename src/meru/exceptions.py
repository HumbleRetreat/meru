"""Exceptions for the use in other modules."""


class ActionException(Exception):
    """An error related to :py:class:`Action`s occurred."""


class PingTimeout(Exception):
    """A ping to the broker did not succeed."""


class MeruException(Exception):
    """A generic exception."""


class HandlerException(Exception):
    """An error related to action handlers occurred."""
