from collections import deque

class InstructionQueue:
    def __init__(self):
        self.instructions = []

    def __getitem__(self, key):
        return self.instructions[key]

    '''
    def __str__(self):
        result = ""
        for instr in self.instructions:
            result += str(result) + "\n"
        return result
    '''
    
    def pop(self, index=0):
        '''Pop a single move instruction at a given index.
        Clears the instruction if all moves are complete'''
        instruction = None
        if len(self.instructions) > index:
            instruction = self.instructions[index]
            self.instructions[index].amount -= 1
            if self.instructions[index].amount <= 0:
                del self.instructions[index]

        return instruction
    
    def get(self):
        return self.instructions

    def __len__(self):
        return len(self.instructions)

    def add(self, instruction):
        self.instructions.append(instruction)
        
    def get_source(self, index=0):
        if len(self.instructions) <= index:
            return None
        return self.instructions[index].source


class Instruction:
    '''The instruction object used to direct the actions of ports/processors.

    Held in instruction queue attached to a port/processeor'''
    def __init__(self, source, dest, message, amount, time):
        self.source = source
        self.dest = dest
        self.amount = amount
        self.time = time
        self.msg = message

    def __str__(self):
        return "Source: {}, Dest: {}, Amount: {}, Time: {}".format(self.source,self.dest,self.amount,self.time)
