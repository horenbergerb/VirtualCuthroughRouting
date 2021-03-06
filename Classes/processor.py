from Classes.messages import Header, Flit, Message
from Classes.container import Container

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

        #trash can holds header until the whole message is consumed
        #this prevents id collisions
        self.header_trash = []
        self.header_trash_timers = []

    # generates new msgs in processor; either sends to Obuffer or stores
    # NOTE: Never sends message to itself
    def generate_msg(self, address, time, do_print=False):
        dest = [address[0], address[1]]
        while dest == address:
            x_dist = random.randint(-self.PATH_LEN, self.PATH_LEN)
            dest_x = (address[0] + x_dist) % self.DIM1
            dest_y = (address[1] + ((-1)**random.randint(0, 1))*(self.PATH_LEN-abs(x_dist))) % self.DIM2
            dest = [dest_x, dest_y]
        if do_print:
            print("    NEW MESSAGE W/ DEST: {}".format(dest))
        new_header = Header(dest, time, self.MSG_LEN)
        new_header.moved = True
        new_header_id = id(new_header)
        
        new_msg = Message(new_header)
        new_msg.add_flit(new_header)
        # one taken off for header
        for x in range(0, self.MSG_LEN-1):
            new_flit = Flit(new_header_id)
            new_flit.moved = True
            new_msg.add_flit(new_flit)
        self.Obuffer.add_msg(new_msg)
        
    # move is called many times per unit time
    def move(self, time):
        # munch those inputs
        if self.Ibuffer is not None and not self.Ibuffer.moved:
            if isinstance(self.Ibuffer, Header):
                if self.Ibuffer.time >= self.SAMPLE_THRESH:
                    self.lifetimes.append([self.Ibuffer.time, time+self.MSG_LEN])
                self.header_trash.append(self.Ibuffer)
                self.header_trash_timers.append(time)
            self.Ibuffer = None

    # step is called exactly once per unit time

    def step(self, address, time, do_print=False):
        while self.header_trash_timers and self.header_trash_timers[0] + self.MSG_LEN < time:
            self.header_trash_timers.pop(0)
            self.header_trash.pop(0)

        # generate a message 1 in 10 steps
        if random.uniform(0, 1) <= self.MSG_FREQ:
            self.generate_msg(address, time, do_print)

# holds an amount of flits in input and output buffers
