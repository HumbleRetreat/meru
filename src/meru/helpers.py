import inspect
from functools import lru_cache
from importlib import import_module


def get_full_path_to_class(cls: object):
    mod = cls.__module__
    name = cls.__name__

    return f'{mod}.{name}'


def get_type_from_string(cls_path: str):
    module_name, class_name = cls_path.rsplit('.', 1)
    return getattr(import_module(module_name), class_name)


def build_address(ip, port):
    return f'tcp://{ip}:{port}'


@lru_cache(maxsize=None)
def get_subclasses(base_cls):
    all_subclasses = {}

    def _get_all_subclasses(cls):
        for subclass in cls.__subclasses__():
            _get_all_subclasses(subclass)
            all_subclasses[subclass.__name__] = subclass

    if len(all_subclasses) == 0:
        _get_all_subclasses(base_cls)

    return all_subclasses


@lru_cache(maxsize=None)
def get_class_init_args(cls):
    """
    Get the __init__ arguments from a given class and return their names and their types.

    :param cls:
    :return:
    """
    args = inspect.getfullargspec(cls.__init__)
    init_args = {}

    for arg in args.args[:]:
        if arg == 'self':
            continue
        init_args[arg] = args.annotations[arg]

    return init_args
