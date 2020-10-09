from dataclasses import dataclass
import time

from meru.actions import Action
from meru.serialization import decode_object, encode_object


@dataclass
class DummyAction(Action):
    str_field: str
    int_field: int
    dict_field: dict


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


def benchmark_encoding():
    res = encode_object(DummyAction('some_random_String', 123, {'wtf': 123, 'abc': 'def'}))

    for _ in range(100_000):
        decode_object(res)


if __name__ == '__main__':
    with MyTimer('benchmark_encoding'):
        benchmark_encoding()
