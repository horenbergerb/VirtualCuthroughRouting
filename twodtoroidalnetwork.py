from router import Router
from routergrid import RouterGrid

from parameters import MSG_LEN, MSG_FREQ, DIM1, DIM2, PORTS, UP, RIGHT, DOWN, LEFT, DIRS

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
    def __init__(self, MSG_FREQ=MSG_FREQ):
        random.seed()
        self.time = 0

        self.MSG_FREQ = MSG_FREQ
        # table of routers
        self.routers = RouterGrid(MSG_FREQ=self.MSG_FREQ)

    def __str__(self):
        result = ""
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                result += str(self.routers[i][j])
        return result
                
    def step(self, amount = 1, do_print = False):
        for x in range(amount):
            if do_print:
                print("TIME: {}".format(self.time))
            # part 1: iterate over all routers, continue moving until there's nothign left to move
            for i in range(0, len(self.routers)):
                for j in range(0, len(self.routers[0])):
                    # inter-router movement
                    moved = self.routers[i][j].step(self.time, do_print)
                    self.routers.follow_intra_movements(i, j, moved, self.time)
                    moved = self.routers.move_inter_router(i, j)
                    self.routers.follow_inter_movements(i, j, moved, self.time)

            for i in range(0, len(self.routers)):
                for j in range(0, len(self.routers[0])):
                    self.routers[i][j].reset_moved()
                    if do_print:
                        print(self.routers[i][j])

            self.time += 1

    def get_lifetimes(self):
        lifetimes = []
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                lifetimes.extend(self.routers[i][j].processor.lifetimes)
        lifetimes = sorted(lifetimes)
        return lifetimes
