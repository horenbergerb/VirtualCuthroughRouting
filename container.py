from messages import Header, FlitQueue
from instruction import InstructionQueue

##################
# ABSTRACT CLASS #
##################


class Container():
    '''Container is the abstract class used to model router ports and processors.

    It mostly offers methods to take/receive flits from/to buffers.
    '''

    def __init__(self):
        self.Ibuffer = None
        self.Obuffer = FlitQueue()
        self.instructions = InstructionQueue()

    def has_instructions(self):
        return self.instructions.has_instructions()

    def pop_instruction(self, index=0):
        return self.instructions.pop_instruction(index)

    def get_instructions(self):
        return self.instructions.get_instruction()

    def get_instruction_source(self, index=0):
        return self.instructions.get_source(index)

    def add_instruction(self, instruction):
        self.instructions.add_instruction(instruction)

    def len_instructions(self):
        return self.instructions.len_instructions()

    def putI(self, package):
        '''Put item into the input buffer. Also marks the flit as having moved.
        Caution: Will overwrite input buffer contents.'''

        self.Ibuffer = package
        if isinstance(package, Header):
            package.parsed = False

    def putO(self, package):
        '''Put item into the output buffer or storage if buffer is full'''
        return self.Obuffer.add_flit(package)

    def peekI(self):
        '''Get without popping from input buffer'''
        return self.Ibuffer

    def peekO(self):
        '''Get without popping from output buffer'''
        return self.Obuffer.peek()

    def getI(self):
        '''Pops an item off the input buffer'''
        out = self.Ibuffer
        self.Ibuffer = None
        return out

    def getO(self):
        '''Pops an item off the output buffer'''
        return self.Obuffer.pop_flit()

    def reset_moved(self):
        '''Reset the "moved" variable for all flits'''
        if self.Ibuffer is not None:
            self.Ibuffer.moved = False
        self.Obuffer.reset_moved()
