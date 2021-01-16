from messages import Header, Flit
from container import Container

import random


class Processor(Container):
    def __init__(self, DIM1, DIM2, MSG_FREQ, MSG_LEN, PATH_LEN, SAMPLE_THRESH):
        super().__init__(MSG_LEN)
        self.lifetimes = []
        self.DIM1 = DIM1
        self.DIM2 = DIM2
        self.MSG_FREQ = MSG_FREQ
        self.MSG_LEN = MSG_LEN
        self.PATH_LEN = PATH_LEN
        self.SAMPLE_THRESH = SAMPLE_THRESH

    # generates new msgs in processor; either sends to Obuffer or stores
    # NOTE: Never sends message to itself
    def generate_msg(self, address, time, do_print=False):
        dest = [random.randint(0, (self.DIM1-1)), random.randint(0, (self.DIM2-1))]
        # prevent messages sent to our own address
        while dest == address or (abs(dest[0]-address[0])+abs(dest[1]-address[1])) != self.PATH_LEN:
            dest = [random.randint(0, (self.DIM1-1)), random.randint(0, (self.DIM2-1))]
        if do_print:
            print("    NEW MESSAGE W/ DEST: {}".format(dest))
        new_header = Header(dest, time, self.MSG_LEN)
        self.Obuffer.add_flit(new_header)
        # one taken off for header
        for x in range(0, self.MSG_LEN-1):
            self.Obuffer.add_flit(Flit(id(new_header)))

    # move is called many times per unit time
    def move(self, time):
        # munch those inputs
        if self.Ibuffer is not None:
            if isinstance(self.Ibuffer, Header) and self.Ibuffer.time >= self.SAMPLE_THRESH:
                self.lifetimes.append([self.Ibuffer.time, time])
            self.Ibuffer = None

    # step is called exactly once per unit time

    def step(self, address, time, do_print=False):

        # generate a message 1 in 10 steps
        if random.uniform(0, 1) <= self.MSG_FREQ:
            self.generate_msg(address, time, do_print)

# holds an amount of flits in input and output buffers
