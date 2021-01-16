from router import Router
from parameters import DIRS, UP, DOWN, LEFT, RIGHT, DIM1, DIM2, MSG_FREQ


class RouterGrid():
    def __init__(self, MSG_FREQ=MSG_FREQ, dim1=DIM1, dim2=DIM2):
        self.dim1 = dim1
        self.dim2 = dim2

        # table of routers
        self.routers = []
        for x in range(0, self.dim1):
            cur_row = []
            for y in range(0, self.dim2):
                # creates router with the address corresponding to network dimensions
                cur_row.append(Router([x, y], MSG_FREQ=MSG_FREQ))
            self.routers.append(cur_row)

    def get_routers(self):
        return self.routers

    def __len__(self):
        return len(self.routers)

    def __getitem__(self, key):
        return self.routers[key]

    def get_port_in_dir(self, i, j, dir):
        if dir == UP:
            return self.routers[(i-1) % DIM1][j].ports[DOWN]
        elif dir == RIGHT:
            return self.routers[i][(j+1) % DIM2].ports[LEFT]
        elif dir == DOWN:
            return self.routers[(i+1) % DIM1][j].ports[UP]
        elif dir == LEFT:
            return self.routers[i][(j-1) % DIM2].ports[RIGHT]

    def get_router_index_in_dir(self, i, j, dir):
        if dir == UP:
            return (i-1) % DIM1, j
        elif dir == RIGHT:
            return i, (j+1) % DIM2
        elif dir == DOWN:
            return (i+1) % DIM1, j
        elif dir == LEFT:
            return i, (j-1) % DIM2

    def move_inter_router(self, i, j):
        moved = []
        for p in DIRS:
            if self.routers[i][j].ports[p].peekO() is not None and not self.routers[i][j].ports[p].peekO().moved:
                dest_port = self.get_port_in_dir(i, j, p)
                if dest_port.peekI() is None:
                    dest_port.putI(self.routers[i][j].ports[p].getO())
                    moved.append(p)
        return moved

    def follow_intra_movements(self, i, j, moved, time):
        '''Propagates an intra-router movement, i.e.
        processes all consequential movement'''
        for dir in moved:
            new_i, new_j = self.get_router_index_in_dir(i, j, dir)
            moved = self.move_inter_router(new_i, new_j)
            if moved:
                self.follow_inter_movements(new_i, new_j, moved, time)

    def follow_inter_movements(self, i, j, moved, time):
        '''Propagates an inter-router movement, i.e.
        processes all consequential movement'''
        moved = self.routers[i][j].move(time)
        if moved:
            self.follow_intra_movements(i, j, moved, time)
