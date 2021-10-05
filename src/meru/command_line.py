import multiprocessing

import click
import time
from click import ClickException
from typing import List

from meru import run_process

AVAILABLE_PROCESSES = {}


@click.group()
def main_cli():
    pass


@main_cli.command(name="process", help="Start processes.")
@click.argument("processes", nargs=-1, required=True)
def process_cli(processes):
    if processes[0] == "all":
        start_multiple_processes(list(AVAILABLE_PROCESSES.keys()))
    elif len(processes) == 1:
        run_process(AVAILABLE_PROCESSES[processes[0]])
    else:
        start_multiple_processes(processes)


def validate_process_names(process_names: List[str]):
    invalid_process_names = [
        name for name in process_names if name not in AVAILABLE_PROCESSES
    ]
    if invalid_process_names:
        raise ClickException(
            f"Following process names are invalid: {', '.join(invalid_process_names)}"
        )


def start_multiple_processes(process_names: List[str]):
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
    AVAILABLE_PROCESSES[name] = path
