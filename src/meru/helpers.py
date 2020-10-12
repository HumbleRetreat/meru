def get_full_path_to_class(cls: object):
    mod = cls.__module__
    name = cls.__name__

    return f'{mod}.{name}'


def build_address(ip, port):
    return f'tcp://{ip}:{port}'
