from messages import Flit, Header
from processor import Processor
from instruction import Instruction
from port import Port

from parameters import MSG_LEN, MSG_FREQ, DIM1, DIM2, PORTS, UP, RIGHT, DOWN, LEFT, DIRS


class Router:
    def __init__(self, address):
        # address used for header parsing and message generation
        self.address = address
        self.time = 0

        # the four ports of the router
        self.ports = []
        for x in range(0, PORTS):
            self.ports.append(Port())

        # the router's processor
        self.processor = Processor()

    # debug function for reading out info
    def debug(self):
        print("Router Readout: ({}, {})".format(*(self.address)))
        port_list = []
        for x in range(0, len(self.ports)):
            port_list.append("Port {}".format(x))

        # show contents of each port
        line = []
        for x in range(0, len(self.ports)):
            # contents of Ibuffer
            in_string = "I: "
            if self.ports[x].Ibuffer.queue is not None:
                if isinstance(self.ports[x].Ibuffer, Header):
                    in_string += "H"
                if isinstance(self.ports[x].Ibuffer, Flit):
                    in_string += "F"
            # contents of Obuffer
            out_string = "O: "
            if self.ports[x].Obuffer.queue:
                for cur in self.ports[x].Obuffer.queue[0].items:
                    if isinstance(cur, Header):
                        out_string += "H"
                    if isinstance(cur, Flit):
                        out_string += "F"

            line.append(in_string + " " + out_string)
        col_width = max(len(word)
                        for row in [port_list, line] for word in row) + 2
        for row in [port_list, line]:
            print("".join(word.ljust(col_width) for word in row))

    def parse_header(self, cur, source):
        '''Parses a Header into an Instruction object'''
        instruction = Instruction(source, -1, cur.length, self.time)
        cur.parsed = True

        # find best choice out of l/r (denoted false/true) options
        lr_dir = -1
        if ((self.address[1]-cur.dest[1]) % DIM1 > (cur.dest[1]-self.address[1]) % DIM1):
            lr_dir = RIGHT
        else:
            lr_dir = LEFT
        # note if we're already done moving l/r
        if self.address[1] == cur.dest[1]:
            lr_dir = -1

        # find best choice out of up/down (denoted false/true) options
        ud_dir = -1
        if ((self.address[0]-cur.dest[0]) % DIM2 > (cur.dest[0]-self.address[0]) % DIM2):
            ud_dir = UP
        else:
            ud_dir = DOWN
        # note if we're already done moving up/down
        if self.address[0] == cur.dest[0]:
            ud_dir = -1

        # if there's only one choice, return it
        if lr_dir == -1:
            instruction.dest = ud_dir
            return instruction
        if ud_dir == -1:
            instruction.dest = lr_dir
            return instruction

        # pick choice with shortest queue
        if self.ports[lr_dir].Obuffer.get_length() < self.ports[ud_dir].Obuffer.get_length():
            instruction.dest = lr_dir
        else:
            # tie breaker goes with smallest port number
            instruction.dest = min(lr_dir, ud_dir)
        return instruction

    def move(self):
        '''Moves flits from IBuffers to OBuffers using
        port/processor instructions.'''
        self.processor.move()
        # incrementing the queues of each output port
        for port in self.ports:
            for cur_index in range(0, port.len_instructions()):
                source = port.get_instruction_source(cur_index)
                if source != -1:
                    target = self.ports[source].peekI()
                else:
                    target = self.processor.peekO()
                if target is not None and not target.moved:
                    if source != -1:
                        if port.putO(self.ports[source].peekI()):
                            self.ports[source].getI()
                            port.pop_instruction(cur_index)
                            break
                    elif port.putO(self.processor.peekO()):
                        self.processor.getO()
                        port.pop_instruction(cur_index)
                        break

        # incrementing processor queue
        if self.processor.peekI() is None:
            source = self.processor.get_instruction_source()
            if source is not None and self.ports[source].peekI() is not None:
                self.processor.pop_instruction()
                self.processor.putI(
                    self.ports[source].getI())

    def parse_all_inputs(self):
        '''Creates new instructions from new Headers in input buffers.'''

        # PROCESSOR LOGIC
        cur = self.processor.peekO()
        if isinstance(cur, Header) and not (cur.parsed or cur.moved):
            new_instr = self.parse_header(cur, -1)
            self.ports[new_instr.dest].add_instruction(new_instr)

        # PORT LOGIC
        counter = 0
        for port in range(len(self.ports)):
            cur = self.ports[port].peekI()
            # NOTE: Parsing the header takes up one time unit
            # thus moving a header takes 2 time units
            if isinstance(cur, Header) and not (cur.moved or cur.parsed):
                if cur.dest == self.address:
                    self.processor.add_instruction(Instruction(port, -1, cur.length, self.time))
                    cur.moved = True
                else:
                    new_instr = self.parse_header(cur, port)
                    self.ports[new_instr.dest].add_instruction(new_instr)
                    cur.moved = True

            counter += 1

    def step(self, time):
        self.time = time
        self.processor.step(self.address)
        self.parse_all_inputs()
        self.move()

    def reset_moved(self):
        self.processor.reset_moved()
        for port in self.ports:
            port.reset_moved()
