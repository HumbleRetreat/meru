import logging

from meru.helpers import underscore


logger = logging.getLogger('meru.state')


# pylint: disable=too-few-public-methods
class StateField:
    def __init__(self, default):
        self.default = default


# pylint: disable=too-few-public-methods
class StateNodeMeta(type):
    def __new__(cls, name, bases, nmspc):
        nodes = {}
        fields = {}
        new_nmspc = {}

        for key, value in list(nmspc.items()):
            if isinstance(value, cls.__class__):
                nodes[key] = value
            elif isinstance(value, StateField):
                fields[key] = value
            else:
                new_nmspc[key] = value

        new_nmspc['_nodes'] = nodes
        new_nmspc['_fields'] = fields

        return super().__new__(cls, name, bases, new_nmspc)


# pylint: disable=protected-access,too-few-public-methods,no-member
class StateNode(metaclass=StateNodeMeta):
    def __init__(self, **kwargs):
        for key, value in self.__class__._nodes.items():
            if isinstance(value, StateNodeMeta):
                setattr(self, key, value())

        for key, value in self.__class__._fields.items():
            if isinstance(value, StateField):
                if callable(value.default):
                    setattr(self, key, value.default())
                else:
                    setattr(self, key, value.default)

        fields = kwargs.get('fields', None)
        if fields:
            for key, value in fields.items():
                setattr(self, key, value)

    def process_action(self, action):
        expected_handler = 'handle_' + underscore(action.__class__.__name__)
        if hasattr(self, expected_handler):
            func = getattr(self, expected_handler)
            logger.debug(f'{self.__class__.__name__} processing action {action}')
            func(action)

        for node_name in self.__class__._nodes.keys():
            node = getattr(self, node_name)
            node.process_action(action)

    @property
    def state_nodes(self):
        return self._nodes.keys()

    @property
    def state_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self):
        data = self.__dict__
        data['state_type'] = self.state_type
        return data
