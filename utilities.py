from instruction import Instruction

from parameters import UP, DOWN, LEFT, RIGHT, DIM1, DIM2

def shortest_path(cur, source, address, ports, time):
    '''Given a new header, determines proper destination port
    and creates a corresponding instruction.'''
    instruction = Instruction(source, -1, cur.length, time)
    cur.parsed = True

    # find best choice out of l/r (denoted false/true) options
    lr_dir = -1
    if ((address[1]-cur.dest[1]) % DIM1 > (cur.dest[1]-address[1]) % DIM1):
        lr_dir = RIGHT
    else:
        lr_dir = LEFT
    # note if we're already done moving l/r
    if address[1] == cur.dest[1]:
        lr_dir = -1

    # find best choice out of up/down (denoted false/true) options
    ud_dir = -1
    if ((address[0]-cur.dest[0]) % DIM2 > (cur.dest[0]-address[0]) % DIM2):
        ud_dir = UP
    else:
        ud_dir = DOWN
    # note if we're already done moving up/down
    if address[0] == cur.dest[0]:
        ud_dir = -1

    # if there's only one choice, return it
    if lr_dir == -1:
        instruction.dest = ud_dir
        return instruction
    if ud_dir == -1:
        instruction.dest = lr_dir
        return instruction

    # pick choice with shortest queue
    if ports[lr_dir].Obuffer.get_length() < ports[ud_dir].Obuffer.get_length():
        instruction.dest = lr_dir
    else:
        # tie breaker goes with smallest port number
        instruction.dest = min(lr_dir, ud_dir)
    return instruction
