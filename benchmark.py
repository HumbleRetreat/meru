import argparse
from dataclasses import dataclass
import time

from meru.actions import Action
from meru.serialization import decode_object, encode_object
from meru.state import StateField, StateNode


parser = argparse.ArgumentParser(description='Benchmark Meru')
parser.add_argument('iterations', metavar='ITERATIONS', type=int,
                    help='Amount of iterations')

args = parser.parse_args()


@dataclass
class DummyAction(Action):
    str_field: str
    int_field: int
    dict_field: dict


class DummyState(StateNode):
    string_state = StateField('some_string')
    int_state = StateField(666)


class MyTimer:
    def __init__(self, name):
        self.start = time.time()
        self.name = name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        print(f'The function "{self.name}" took {runtime} seconds to complete')


def benchmark_action_decoding():
    res = encode_object(DummyAction('some_random_String', 123, {'wtf': 123, 'abc': 'def'}))

    for _ in range(args.iterations):
        decode_object(res)


def benchmark_state_decoding():
    res = encode_object(DummyState())

    for _ in range(args.iterations):
        decode_object(res)


if __name__ == '__main__':
    with MyTimer('benchmark_encoding'):
        benchmark_action_decoding()
