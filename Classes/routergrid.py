from Classes.router import Router

class RouterGrid():
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    DIRS = [0,1,2,3]

    def __init__(self, DIM1, DIM2, MSG_LEN, SAMPLE_THRESH, MSG_FREQ, PATH_LEN):
        self.DIM1 = DIM1
        self.DIM2 = DIM2        

        # table of routers
        self.routers = []
        for x in range(0, self.DIM1):
            cur_row = []
            for y in range(0, self.DIM2):
                # creates router with the address corresponding to network dimensions
                cur_row.append(Router([x, y], DIM1, DIM2, MSG_FREQ, MSG_LEN, PATH_LEN, SAMPLE_THRESH))
            self.routers.append(cur_row)
    
    def __len__(self):
        return len(self.routers)

    def __getitem__(self, key):
        return self.routers[key]

    def get_port_in_dir(self, i, j, dir):
        if dir == self.UP:
            return self.routers[(i-1) % self.DIM1][j].ports[self.DOWN]
        elif dir == self.RIGHT:
            return self.routers[i][(j+1) % self.DIM2].ports[self.LEFT]
        elif dir == self.DOWN:
            return self.routers[(i+1) % self.DIM1][j].ports[self.UP]
        elif dir == self.LEFT:
            return self.routers[i][(j-1) % self.DIM2].ports[self.RIGHT]

    def get_router_index_in_dir(self, i, j, dir):
        if dir == self.UP:
            return (i-1) % self.DIM1, j
        elif dir == self.RIGHT:
            return i, (j+1) % self.DIM2
        elif dir == self.DOWN:
            return (i+1) % self.DIM1, j
        elif dir == self.LEFT:
            return i, (j-1) % self.DIM2
        

    def move_inter_router(self, i, j, chosen_ports = None):
        moved = []
        if chosen_ports is None:
            chosen_ports = self.DIRS
        for p in chosen_ports:
            if self.routers[i][j].ports[p].obuffer_is_ready():
                dest_port = self.get_port_in_dir(i, j, p)
                if dest_port.Ibuffer is None:
                    dest_port.putI(self.routers[i][j].ports[p].getO())
                    moved.append(p)
        return moved

    def follow_intra_movements(self, i, j, moved, time):
        '''Propagates an intra-router movement, i.e.
        processes all consequential movement'''
        for dir in moved:
            new_i, new_j = self.get_router_index_in_dir(i, j, dir)
            dir_moved = self.move_inter_router(new_i, new_j, chosen_ports=[(dir+2)%4])
            if dir_moved:
                self.follow_inter_movements(new_i, new_j, dir_moved, time)

    def follow_inter_movements(self, i, j, moved, time):
        '''Propagates an inter-router movement, i.e.
        processes all consequential movement'''
        moved = self.routers[i][j].move(time, chosen_ports = moved)
        if moved:
            self.follow_intra_movements(i, j, moved, time)
