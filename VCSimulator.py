from router import Router

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
        self.routers = []
        for x in range(0, DIM1):
            cur_row = []
            for y in range(0, DIM2):
                # creates router with the address corresponding to network dimensions
                cur_row.append(Router([x, y]))
            self.routers.append(cur_row)

    def step(self):
        # part 1: iterate over all routers, continue moving until there's nothign left to move
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                # inter-router movement
                self.routers[i][j].step(self.time)

        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                # intra-router movement
                #[i][j] is rowsxcolumns
                for p in DIRS:
                    if self.routers[i][j].ports[p].peekO() != None and not self.routers[i][j].ports[p].peekO().moved:
                        if p == UP:
                            if self.routers[(i-1) % DIM1][j].ports[DOWN].peekI() == None:
                                self.routers[(
                                    i-1) % DIM1][j].ports[DOWN].putI(self.routers[i][j].ports[p].getO())
                        elif p == RIGHT:
                            if self.routers[i][(j+1) % DIM2].ports[LEFT].peekI() == None:
                                self.routers[i][(
                                    j+1) % DIM2].ports[LEFT].putI(self.routers[i][j].ports[p].getO())
                        elif p == DOWN:
                            if self.routers[(i+1) % DIM1][j].ports[UP].peekI() == None:
                                self.routers[(
                                    i+1) % DIM1][j].ports[UP].putI(self.routers[i][j].ports[p].getO())
                        elif p == LEFT:
                            if self.routers[i][(j-1) % DIM2].ports[RIGHT].peekI() == None:
                                self.routers[i][(
                                    j-1) % DIM2].ports[RIGHT].putI(self.routers[i][j].ports[p].getO())
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                self.routers[i][j].reset_moved()
                self.routers[i][j].debug()

        self.time += 1


test_net = TwoDToroidalNetwork()

for x in range(0, 20):
    print("\n\nSTEP {}".format(x))
    test_net.step()
