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
    def __init__(self):
        random.seed()
        self.time = 0

        # table of routers
        self.routers = RouterGrid()

    def step(self):
        # part 1: iterate over all routers, continue moving until there's nothign left to move
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                # inter-router movement
                moved = self.routers[i][j].step(self.time)
                self.routers.follow_intra_movements(i, j, moved, self.time)
                moved = self.routers.move_inter_router(i, j)
                self.routers.follow_inter_movements(i, j, moved, self.time)

        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                self.routers[i][j].reset_moved()
                print(self.routers[i][j])

        self.time += 1


test_net = TwoDToroidalNetwork()

for x in range(0, 20):
    print("\n\nSTEP {}".format(x))
    test_net.step()
