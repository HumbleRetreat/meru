Project Structure
=================

This page describes the structure and basic setup of a meru project.

.. _module-structure:

Python Module Structure
-----------------------

A project using meru typically contains the following module structure::

    ├── project_module
    │   ├── __init__.py
    │   ├── actions.py
    │   ├── cli.py
    │   ├── processes
    │   │   ├── broker.py
    │   │   ├── process1.py
    │   │   ├── process2.py
    │   │   ├── …
    │   │   └── state.py
    │   └── state.py

``actions.py`` contains the actions – all classes deriving from
:py:class:`meru.base.Action` – that are used in the rest of the project.
``cli.py`` contains the :ref:`cli` to start processes.  ``processes/`` contains
a submodule for each process.  ``state.py`` contains the :ref:`global State
<state>`.

.. _setup:

Setup
-----

.. _processes-py:

processes/\*.py
^^^^^^^^^^^^^^^

Process modules contain a function that acts as an entrypoint to the process.
The entrypoint sets up the broker connection and requests the current state from
the broker if it uses (a subset of) the global state. Process modules usually
contain a similar structure to this:

.. code-block:: python
    :caption: a_process.py

    from meru.actions import register_action_handler, register_state, request_state
    from meru.sockets import PushSocket, SubscriberSocket

    register_state(AStateThatIsUsedByThisProcess)
    register_state(AnotherState)

    @register_action_handler
    async def handle_an_action(action: AnAction):
        # respond with another action
        return AnotherAction

    # states can be requested and multiple actions can be returned
    @register_action_handler
    async def handle_yet_another_action(action: YetAnotherAction, a_state: AStateThatIsUsedByThisProcess):
        # respond with two actions
        yield AnotherAction
        yield AnotherAction

    @register_action_handler
    async def handle_a_different_action(action: DifferentAction):
        # handlers don't have to return anything
        pass

    async def a_process():
        # establish the connection to the broker.
        pusher = PushSocket()
        sub = SubscriberSocket()

        # retrieve the current state
        await request_state()

        # enter the main loop
        while True:
            async for action in sub.handle_incoming_actions():
                await pusher.push(action)

Handlers are registered by the :py:func:`meru.handlers.register_action_handler`
annotation to be called when an action with the type specified in the first
argument is received.

broker.py
^^^^^^^^^

The broker is a special process that all other processes connect to.  The broker
redistributes actions sent by the other processes as described in `ipc`_.

The user of the framework is responsible to implement the broker themselves.  A
minimal implementation looks like this:

.. code-block:: python
    :caption: broker.py
    import asyncio
    import logging

    from meru.actions import StateUpdate
    from meru.sockets import CollectorSocket, PublisherSocket, StateManagerSocket
    from meru.state import (
        get_all_states,
        register_state,
        update_state,
    )

    _log = logging.getLogger(__name__)


    async def _collect_and_publish():
        """Handle the 1:n broker functionality."""

        publisher = PublisherSocket()
        collector = CollectorSocket()

        _log.info("Starting to accept broadcast actions ...")
        while True:
            action = await collector.collect()
            _log.debug(action)
            await update_state(action)
            await publisher.publish(action)


    async def _manage_state():
        """Handle the 1:1 state request socket.

        This function is basically a copy of ``meru.state.answer_state_requests()``.  The original
        function is broken for pickle serialization, so we have to implement our own.
        """

        state_manager = StateManagerSocket()

        _log.info("Starting to accept state update requests ...")
        while True:
            identity, action = await state_manager.get_state_request()
            nodes = []
            states = get_all_states()
            for node in action.nodes:
                # node_cls = get_type_from_string(node)  # original line
                node_cls = node
                nodes.append(states[node_cls])

            action = StateUpdate(nodes)
            await state_manager.answer_state_request(identity, action)


    async def broker():
        """Entrypoint for the broker process."""

        # register _all_ states here
        # register_state(SomeState)
        # register_state(…)

        # this would be a bit more readable with an asyncio.TaskGroup which is added in Python 3.11
        await asyncio.gather(_collect_and_publish(), _manage_state())

        # this shoud never be reached
        _log.error("Broker exited prematurely")

actions.py
^^^^^^^^^^

This module contains the action classes which are used by the processes to
communicate with each other.  Each action is a dataclass which derives from
:py:class:`meru.base.Action`:

.. code-block:: python
    :caption: actions.py

    from dataclasses import dataclass

    from meru.actions import Action


    @dataclass
    class AnAction(Action):
        """An Action, that is emitted whenever a new measurement was collected.

        Attributes
        ----------
            measurements
                A list of newly taken measurements.
        """

        some_parameter: str

Meru relies on the type annotations for serialization purposes.  Each attribute
should have a type that can be serialized by the ``json`` module directly or
contains either a ``__dict__`` attribute or a ``.to_dict()`` method.  Note that
there is no support for an inverse operation to ``.to_dict()``.

state.py
^^^^^^^^

This module usually contains the state classes.  See `state`_ for an explanation
on how the global state management works.  Each handler can request states as
seen in `processes-py`_.  State classes can contain handlers themselves which is
the preferred way to update the global state.  A state class is a dataclass
deriving from :py:class:`StateNode`:

.. code-block:: python
    :caption: state.py

    from dataclasses import dataclass
    from datetime import datetime
    import logging
    from typing import Optional

    from meru.base import StateNode

    from shoged.actions import BackendRequestCompleted, EnableStateReceived

    _log = logging.getLogger(__name__)


    @dataclass
    class EnabledState(StateNode):
        some_state: int = 0

        async def update(self, action: AnAction):
            """A handler that is triggered when the corresponding action is received."
            some_state += 1

Note that all members need initializers, so that the objects can be construct
without the need to specify arguments.

cli.py
^^^^^^

In ``cli.py`` the processes need to be registered first, to be available in
the CLI.

.. code-block:: python
    :caption: cli.py

    from meru.actions import discover_actions
    from meru.command_line import main_cli, register_process


    def main():
        # register all processes here
        register_process("broker", "project_root.processes.broker.broker")
        register_process("process1", "project_root.processes.process1.process1")
        register_process("process2", "project_root.processes.process2.process2")
        # …
        discover_actions("project_root.actions")
        main_cli()

    if __name__ == '__main__':
        main()
