from Classes.messages import Header
from Classes.processor import Processor
from Classes.instruction import Instruction
from Classes.container import Container
from Classes.utilities import shortest_path

from Classes.parameters import PORTS, UP, RIGHT, DOWN, LEFT, DIRS

import itertools


class Router:
    def __init__(self, address, DIM1, DIM2, MSG_FREQ, MSG_LEN, PATH_LEN, SAMPLE_THRESH):
        # address used for header parsing and message generation
        self.address = address
        self.time = 0
        self.DIM1 = DIM1
        self.DIM2 = DIM2

        # the four ports of the router
        self.ports = []
        for x in range(0, PORTS):
            self.ports.append(Container(MSG_LEN))

        # the router's processor
        self.processor = Processor(DIM1, DIM2, MSG_FREQ, MSG_LEN, PATH_LEN, SAMPLE_THRESH)

    def __str__(self):
        result = "Router Readout: ({}, {})".format(*(self.address)) + "\n"
        data = []
        for x in range(0, len(self.ports)):
            cur_result = ["Port {}".format(x)]
            cur_result.extend(str(self.ports[x]).rstrip("\n").split("\n"))
            data.append(cur_result)
        col_width = max(len(entry) for row in data for entry in row) + 2
        data = list(map(list, itertools.zip_longest(*data, fillvalue="")))
        for row in data:
            result += "".join(entry.ljust(col_width) for entry in row) + "\n"

        return result

    def parse_header(self, cur, source):
        '''Parses a Header into an Instruction object'''
        return shortest_path(cur, source, self.address, self.ports, self.time, self.DIM1, self.DIM2)
        '''Given a new header, determines proper destination port
        and creates a corresponding instruction.'''
        instruction = Instruction(source, -1, cur.length, self.time)
        cur.parsed = True
        cur.moved = True

        #the possible directions
        is_valid = [True, True, True, True]

        # find best choice out of l/r (denoted false/true) options
        left_dist = (self.address[1]-cur.dest[1]) % self.DIM1
        right_dist = (cur.dest[1]-self.address[1]) % self.DIM1
        if left_dist > right_dist:
            is_valid[LEFT] = False
        elif left_dist < right_dist:
            is_valid[RIGHT] = False
        elif left_dist == 0:
            is_valid[LEFT] = False
            is_valid[RIGHT] = False

        # find best choice out of up/down (denoted false/true) options
        up_dist = (self.address[0]-cur.dest[0]) % self.DIM2
        down_dist = (cur.dest[0]-self.address[0]) % self.DIM2
        if up_dist > down_dist:
            is_valid[UP] = False
        elif up_dist < down_dist:
            is_valid[DOWN] = False
        elif up_dist == 0:
            is_valid[DOWN] = False
            is_valid[UP] = False

        # if there's only one choice, return it
        if sum(is_valid) == 1:
            instruction.dest = is_valid.index(True)
            return instruction

        # pick empty queue if available
        for cur_port in range(len(is_valid)):
            if is_valid[cur_port]:
                if not ports[cur_port].Obuffer.queue:
                    instruction.dest = cur_port
                    return instruction

        # pick lowest port number
        instruction.dest = is_valid.index(True)
        return instruction

    def move(self, time):
        '''Moves flits from IBuffers to OBuffers using
        port/processor instructions.'''
        moved = []
        # Movement internal to processor
        self.processor.move(time)
        # Port logic
        for port in self.ports:
            instructions = port.get_instructions()
            for cur_index in range(0, len(instructions)):
                source = instructions.get_source(cur_index)
                target = (self.ports[source].Ibuffer if source != -1 else self.processor.peekO()) if source is not None else None
                if target is not None and not target.moved:
                    if source != -1:
                        if port.putO(target):
                            self.ports[source].getI()
                            instructions.pop(cur_index)
                            moved.append(source)
                    elif port.putO(target):
                        self.processor.getO()
                        instructions.pop(cur_index)

        # Processor logic
        if self.processor.peekI() is None:
            instructions = self.processor.get_instructions()
            source = instructions.get_source()
            if source is not None:
                target = self.ports[source].Ibuffer
                if target is not None and not target.moved:
                    instructions.pop()
                    self.processor.putI(
                        self.ports[source].getI())
                    moved.append(source)

        return moved
    
    def parse_all_inputs(self):
        '''Creates new instructions from new Headers in input buffers.'''
        proc_instructions = []
        port_instructions = [[] for x in range(len(self.ports))]
        
        # PROCESSOR LOGIC
        cur = self.processor.peekO()
        if isinstance(cur, Header) and not (cur.parsed or cur.moved):
            new_instr = self.parse_header(cur, -1)
            port_instructions[new_instr.dest].append([cur.time, new_instr])

        # PORT LOGIC
        for port in range(len(self.ports)):
            cur = self.ports[port].peekI()
            # NOTE: Parsing the header takes up one time unit
            # thus moving a header takes 2 time units
            if isinstance(cur, Header) and not (cur.moved or cur.parsed):
                if cur.dest == self.address:
                    proc_instructions.append([cur.time, Instruction(port, -1, cur.length, self.time)])
                    cur.parsed = True
                    cur.moved = True
                else:
                    new_instr = self.parse_header(cur, port)
                    port_instructions[new_instr.dest].append([cur.time, new_instr])
                    cur.moved = True

        proc_instructions.sort(key=lambda x: int(x[0]))
        proc = self.processor.get_instructions()
        for instr in proc_instructions:
            proc.add(instr[1])

        for port in range(len(self.ports)):
            cur_port_instructions = port_instructions[port]
            cur_port_instructions.sort(key=lambda x: int(x[0]))
            port_instr = self.ports[port].get_instructions()
            for instr in cur_port_instructions:
                port_instr.add(instr[1])


    def step(self, time, do_print=False):
        self.time = time
        self.processor.step(self.address, time, do_print)
        self.parse_all_inputs()
        moved = self.move(time)
        return moved

    def reset_moved(self):
        self.processor.reset_moved()
        for port in self.ports:
            port.reset_moved()
