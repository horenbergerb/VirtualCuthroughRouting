from messages import Header, Flit
from container import Container

from parameters import DIM1, DIM2, MSG_LEN, MSG_FREQ, PATH_LEN

from parameters import SAMPLE_THRESH

import random


class Processor(Container):
    def __init__(self, MSG_FREQ=MSG_FREQ):
        super().__init__()
        self.lifetimes = []
        self.MSG_FREQ = MSG_FREQ

    # generates new msgs in processor; either sends to Obuffer or stores
    # NOTE: Never sends message to itself
    def generate_msg(self, address, time, do_print=False):
        dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]
        # prevent messages sent to our own address
        while dest == address or (abs(dest[0]-address[0])+abs(dest[1]-address[1])) != PATH_LEN:
            dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]
        if do_print:
            print("    NEW MESSAGE W/ DEST: {}".format(dest))
        new_header = Header(dest, time)
        self.Obuffer.add_flit(new_header)
        # one taken off for header
        for x in range(0, MSG_LEN-1):
            self.Obuffer.add_flit(Flit(id(new_header)))

    # move is called many times per unit time
    def move(self, time):
        # munch those inputs
        if self.Ibuffer is not None:
            if isinstance(self.Ibuffer, Header) and self.Ibuffer.time >= SAMPLE_THRESH:
                self.lifetimes.append([self.Ibuffer.time, time])
            self.Ibuffer = None

    # step is called exactly once per unit time

    def step(self, address, time, do_print=False):

        # generate a message 1 in 10 steps
        if random.uniform(0, 1) <= self.MSG_FREQ:
            self.generate_msg(address, time, do_print)

# holds an amount of flits in input and output buffers
