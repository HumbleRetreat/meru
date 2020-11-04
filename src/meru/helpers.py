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
