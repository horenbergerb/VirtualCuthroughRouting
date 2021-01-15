from messages import Header
from processor import Processor
from instruction import Instruction
from container import Container
from utilities import shortest_path

from parameters import MSG_LEN, MSG_FREQ, DIM1, DIM2, PORTS, UP, RIGHT, DOWN, LEFT, DIRS


class Router:
    def __init__(self, address):
        # address used for header parsing and message generation
        self.address = address
        self.time = 0

        # the four ports of the router
        self.ports = []
        for x in range(0, PORTS):
            self.ports.append(Container())

        # the router's processor
        self.processor = Processor()

    def __str__(self):
        result = "Router Readout: ({}, {})".format(*(self.address)) + "\n"
        data = []
        for x in range(0, len(self.ports)):
            cur_result = ["Port {}".format(x)]
            cur_result.extend(str(self.ports[x]).split("\n"))
            data.append(cur_result)
        col_width = max(len(entry) for row in data for entry in row) + 2
        data = zip(*data)
        for row in data:
            result += "".join(entry.ljust(col_width) for entry in row) + "\n"

        return result

    def parse_header(self, cur, source):
        '''Parses a Header into an Instruction object'''
        return shortest_path(cur, source, self.address, self.ports, self.time)

    def move(self):
        '''Moves flits from IBuffers to OBuffers using
        port/processor instructions.'''
        moved = []
        # Movement internal to processor
        self.processor.move()
        # Port logic
        for port in self.ports:
            instructions = port.get_instructions()
            for cur_index in range(0, len(instructions)):
                source = instructions.get_source(cur_index)
                target = self.ports[source].peekI() if source != -1 else self.processor.peekO()
                if target is not None and not target.moved:
                    if source != -1:
                        if port.putO(self.ports[source].peekI()):
                            self.ports[source].getI()
                            instructions.pop(cur_index)
                            moved.append(source)
                            break
                    elif port.putO(self.processor.peekO()):
                        self.processor.getO()
                        instructions.pop(cur_index)
                        break

        # Processor logic
        if self.processor.peekI() is None:
            instructions = self.processor.get_instructions()
            source = instructions.get_source()
            if source is not None and self.ports[source].peekI() is not None and not self.ports[source].peekI().moved:
                instructions.pop()
                self.processor.putI(
                    self.ports[source].getI())
                moved.append(source)

        return moved
    
    def parse_all_inputs(self):
        '''Creates new instructions from new Headers in input buffers.'''

        # PROCESSOR LOGIC
        cur = self.processor.peekO()
        if isinstance(cur, Header) and not (cur.parsed or cur.moved):
            new_instr = self.parse_header(cur, -1)
            self.ports[new_instr.dest].get_instructions().add(new_instr)

        # PORT LOGIC
        counter = 0
        for port in range(len(self.ports)):
            cur = self.ports[port].peekI()
            # NOTE: Parsing the header takes up one time unit
            # thus moving a header takes 2 time units
            if isinstance(cur, Header) and not (cur.moved or cur.parsed):
                if cur.dest == self.address:
                    self.processor.get_instructions().add(Instruction(port, -1, cur.length, self.time))
                    cur.parsed = True
                    cur.moved = True
                else:
                    new_instr = self.parse_header(cur, port)
                    self.ports[new_instr.dest].get_instructions().add(new_instr)
                    cur.moved = True

            counter += 1

    def step(self, time):
        self.time = time
        self.processor.step(self.address)
        self.parse_all_inputs()
        moved = self.move()
        return moved

    def reset_moved(self):
        self.processor.reset_moved()
        for port in self.ports:
            port.reset_moved()
