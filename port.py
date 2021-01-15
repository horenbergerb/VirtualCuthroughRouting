from container import Container


class Port(Container):
    '''I/O buffers for each port of a router. Holds instructions.

    Inherits container behavior.'''
    def __init__(self):
        super().__init__()
