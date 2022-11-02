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

``actions.py`` contains the actions – all classes deriving from :py:class:`meru.base.Action` – that are used in the rest of the project.  ``cli.py`` contains the :ref:`cli` to start processes.  ``processes/`` contains a submodule for each process.  ``state.py`` contains the :ref:`global State <state>`.

.. _setup:

Setup
-----

processes/\*.py
^^^^^^^^^^^^^^^

Process modules contain a function that acts as an entrypoint to the process.  The entrypoint sets up the broker connection and requests the current state from the broker if it uses (a subset of) the global state. Process modules usually contain a similar structure to this:

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

Handlers are registered by the :py:func:`meru.handlers.register_action_handler` annotation to be called when an action with the type specified in the first argument is received.

cli.py
^^^^^^

In ``cli.py`` the processes need to be registered first, to be available in the CLI.

.. code-block:: python
    :caption: cli.py

    from meru.actions import discover_actions
    from meru.command_line import main_cli, register_process


    def main():
        register_process("broker", "project_root.processes.broker.broker")
        register_process("process1", "project_root.processes.process1.process1")
        register_process("process2", "project_root.processes.process2.process2")
        # …
        discover_actions("project_root.actions")
        main_cli()

    if __name__ == '__main__':
        main()
