from Classes.instruction import Instruction

from Classes.parameters import UP, DOWN, LEFT, RIGHT

def shortest_path(cur, source, address, ports, time, DIM1, DIM2):
    '''Given a new header, determines proper destination port
    and creates a corresponding instruction.'''
    instruction = Instruction(source, -1, cur.length, time)
    cur.parsed = True
    cur.moved = True
    
    #the possible directions
    is_valid = [True, True, True, True]
    
    # find best choice out of l/r (denoted false/true) options
    if ((address[1]-cur.dest[1]) % DIM1 > (cur.dest[1]-address[1]) % DIM1):
        is_valid[LEFT] = False
    elif ((address[1]-cur.dest[1]) % DIM1 < (cur.dest[1]-address[1]) % DIM1):
        is_valid[RIGHT] = False
    elif (address[1]-cur.dest[1]) % DIM1 == 0:
        is_valid[LEFT] = False
        is_valid[RIGHT] = False

    # find best choice out of up/down (denoted false/true) options
    if ((address[0]-cur.dest[0]) % DIM2 > (cur.dest[0]-address[0]) % DIM2):
        is_valid[UP] = False
    elif ((address[0]-cur.dest[0]) % DIM2 < (cur.dest[0]-address[0]) % DIM2):
        is_valid[DOWN] = False
    elif (address[0]-cur.dest[0]) % DIM2 == 0:
        is_valid[DOWN] = False
        is_valid[UP] = False

    # if there's only one choice, return it
    if sum(is_valid) == 1:
        instruction.dest = is_valid.index(True)
        return instruction

    # pick empty queue if available
    for cur_port in range(len(is_valid)):
        if is_valid[cur_port]:
            if ports[cur_port].Obuffer.get_length() == 0:
                instruction.dest = cur_port
                return instruction

    # pick lowest port number
    instruction.dest = is_valid.index(True)
    return instruction
