from Classes.router import Router
from Classes.routergrid import RouterGrid

from Classes.parameters import PORTS, UP, RIGHT, DOWN, LEFT, DIRS

import random

###############
# ASSUMPTIONS #
###############


# distance is always less than 1/2 size
#   thus there is always a clear shortest path
#   (used implicitly in Router for header parsing)
# NOTE: Does this need to be implemented in the Processor message generation?


class TwoDToroidalNetwork:
    # routers in the self.routers matrix are connected to adjacent routers
    # connections apply modulo dim1 and dim2 (because it's a toroidal network)
    def __init__(self, DIM1=2, DIM2=2, MSG_LEN=20, SAMPLE_THRESH=50000, MSG_FREQ=.03, PATH_LEN=2):
        self.DIM1 = DIM1
        self.DIM2 = DIM2
        self.MSG_LEN = MSG_LEN
        self.SAMPLE_THRESH = SAMPLE_THRESH
        self.MSG_FREQ = MSG_FREQ
        self.PATH_LEN = PATH_LEN

        random.seed()
        self.time = 0
        # table of routers
        self.routers = RouterGrid(DIM1, DIM2, MSG_LEN, SAMPLE_THRESH, MSG_FREQ, PATH_LEN)

    def __str__(self):
        result = ""
        for i in range(0, self.DIM1):
            for j in range(0, self.DIM2):
                result += str(self.routers[i][j])
        return result
                
    def step(self, amount = 1, do_print = False):
        for x in range(amount):
            if do_print:
                print("TIME: {}".format(self.time))
            # part 1: iterate over all routers, continue moving until there's nothing left to move
            for i in range(0, self.DIM1):
                for j in range(0, self.DIM2):
                    # inter-router movement
                    moved = self.routers[i][j].step(self.time, do_print)
                    self.routers.follow_intra_movements(i, j, moved, self.time)
                    moved = self.routers.move_inter_router(i, j)
                    self.routers.follow_inter_movements(i, j, moved, self.time)

            for i in range(0, self.DIM1):
                for j in range(0, self.DIM2):
                    self.routers[i][j].reset_moved()
                    if do_print:
                        print(self.routers[i][j])

            self.time += 1

    def get_lifetimes(self):
        lifetimes = []
        for i in range(0, self.DIM1):
            for j in range(0, self.DIM2):
                lifetimes.extend(self.routers[i][j].processor.lifetimes)
        lifetimes.sort(key=lambda x: int(x[0]))
        return lifetimes
