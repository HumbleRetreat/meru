import multiprocessing
from typing import List

import time
import click
from click import ClickException

from meru import run_process

AVAILABLE_PROCESSES = {}


@click.group()
def main_cli():
    pass


@main_cli.group(name="process", help="Start processes.")
def process_cli():
    pass


@process_cli.command(name="all", help="Start all processes together.")
def start_all():
    start_multiple_processes(list(AVAILABLE_PROCESSES.keys()))


@process_cli.command(name="multi", help="Start a selection of multiple processes.")
@click.argument("processes", nargs=-1, required=True)
def start_multiple(processes):
    validate_process_names(processes)
    if len(processes) == 1:
        run_process(AVAILABLE_PROCESSES[processes[0]])
    else:
        start_multiple_processes(processes)


def validate_process_names(process_names: List[str]):
    """
    Compare a list of names against the list of registered processes. If there are names given that
    do not exist in the list of registered processes a click exception will be raised.

    :param process_names: A list of names that will be validated against the registered processes.
    :raise: `ClickException`
    """
    invalid_process_names = [
        name for name in process_names if name not in AVAILABLE_PROCESSES
    ]
    if invalid_process_names:
        raise ClickException(
            f"Following process names are invalid: {', '.join(invalid_process_names)}"
        )


def start_multiple_processes(process_names: List[str]):
    """
    Start one or multiple processes using Python's multiprocessing module. While it is technically
    possible to start only one process with this method, it is rather pointless to do so.

    :param process_names: A list of process names that were registered with `register_process`.
    """
    validate_process_names(process_names)

    processes = []

    for name in process_names:
        entry_point = AVAILABLE_PROCESSES[name]

        processes.append(
            multiprocessing.Process(
                name=name,
                target=run_process,
                args=(entry_point,),
                daemon=False,
            )
        )

    for process_name in processes:
        time.sleep(0.1)
        process_name.start()

    for process_name in processes:
        process_name.join()


def register_process(name: str, path: str):
    """
    Register a new process with the CLI and meru in general.

    :param name: The name of the process to be used for the CLI
    :param path: The entry point of the method.
    """
    process_cli.command(name=name)(lambda: run_process(AVAILABLE_PROCESSES[name]))
    AVAILABLE_PROCESSES[name] = path
