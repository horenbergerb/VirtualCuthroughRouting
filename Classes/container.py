from Classes.messages import Header, Flit, FlitQueue
from Classes.instruction import InstructionQueue

##################
# ABSTRACT CLASS #
##################


class Container():
    '''Container is the class used to model router ports and processors.

    It mostly offers methods to take/receive flits from/to buffers.
    '''

    def __init__(self, MSG_LEN):
        self.Ibuffer = None
        self.Obuffer = FlitQueue(MSG_LEN)
        self.instructions = InstructionQueue()

    def __str__(self):
        result = "I: "
        if isinstance(self.Ibuffer, Header):
            result += "{}: H".format(id(self.Ibuffer) % 1000)
        elif isinstance(self.Ibuffer, Flit):
            result += "{}: F".format(self.Ibuffer.headerID % 1000)
        result += "\n" + "O:\n"
        result += str(self.Obuffer)
        return result
    
    def has_instructions(self):
        '''Check if instructions exist'''
        return self.instructions.has_instructions()

    def get_instructions(self):
        '''Used to interact with the container's instructions'''
        return self.instructions
    
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

    def obuffer_is_ready(self):
        '''Whether the Obuffer has contents ready
        to be moved'''
        #peeko is not none and peeko is not moved
        cur = self.Obuffer.peek()
        return (cur is not None) and (not cur.moved)
    
    def getI(self):
        '''Pops an item off the input buffer'''
        self.Ibuffer.moved = True
        out = self.Ibuffer
        self.Ibuffer = None
        return out

    def getO(self):
        '''Pops an item off the output buffer'''
        self.Obuffer.set_moved()
        return self.Obuffer.pop_flit()

    def reset_moved(self):
        '''Reset the "moved" variable for all flits'''
        if self.Ibuffer is not None:
            self.Ibuffer.moved = False
        self.Obuffer.reset_moved()
