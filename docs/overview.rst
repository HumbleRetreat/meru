Overview
========

Meru is a framework that bundles a number of features that act as building blocks for building distributed multi-process applications.  While blocks for building an :ref:`ipc` are at the center of the package, the package also contains utilities like a :ref:`logging` configuration and a simple :ref:`cli`.

.. _ipc:

Inter-Process Communication
---------------------------

Processes communicate using regular Python objects (:py:class:`meru.base.MeruObject`) that are serialized and distributed to the other processes via a broker.  `ZeroMQ`_ is used for the communication between the broker and the processes.  The processes declare handler functions and meru takes care of the communication with the broker and the de-/serialization.

.. _ZeroMQ: https://zeromq.org/

.. _state:

State Management
----------------

Applications often have some kind of global state.  Using meru, this state (in form of a :py:class:`meru.base.StateNode`) can be shared between processes while the framework takes care of synchronizing changes.

The processes maintain a second pair of connections to the broker to request the current state without the request being broadcast to all other processes.

.. _cli:

Command Line Interface
----------------------

:py:mod:`meru.command_line` provides a simple command line interface (CLI) that can be used to start one ore more meru processes.

.. _logging:

Logging
-------

:py:func:`meru.logging.setup_logging` configures the ``logging`` module with defaults suited for the intended usecase of building distributed services.
