from messages import Header, Flit
from container import Container

from parameters import DIM1, DIM2, MSG_LEN, MSG_FREQ

import random


class Processor(Container):
    def __init__(self):
        super().__init__()

    # generates new msgs in processor; either sends to Obuffer or stores
    # NOTE: Never sends message to itself
    def generate_msg(self, address):
        dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]
        # prevent messages sent to our own address
        while dest == address:
            dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]

        print("    NEW MESSAGE W/ DEST: {}".format(dest))
        new_header = Header(dest)
        self.Obuffer.add_flit(new_header)
        # one taken off for header
        for x in range(0, MSG_LEN-1):
            self.Obuffer.add_flit(Flit(id(new_header)))

    # move is called many times per unit time
    def move(self):
        # munch those inputs
        if self.Ibuffer is not None:
            self.Ibuffer = None

    # step is called exactly once per unit time

    def step(self, address):

        # generate a message 1 in 10 steps
        if random.randint(0, MSG_FREQ) == 0:
            self.generate_msg(address)

# holds an amount of flits in input and output buffers
