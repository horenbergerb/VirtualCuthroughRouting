class InstructionQueue:
    def __init__(self):
        self.instructions = []

    def pop_instruction(self, index=0):
        instruction = None
        if len(self.instructions) > index:
            instruction = self.instructions[index]
            self.instructions[index].amount -= 1
            if self.instructions[index].amount <= 0:
                self.instructions.pop(index)

        return instruction
    
    def get_instructions(self):
        return self.instructions

    def len_instructions(self):
        return len(self.instructions)

    def has_instructions(self):
        return bool(self.instructions)

    def add_instruction(self, instruction):
        self.instructions.append(instruction)
        
    def get_source(self, index=0):
        if len(self.instructions) <= index:
            return None
        return self.instructions[index].source


class Instruction:
    '''The instruction object used to direct the actions of ports/processors.

    Held in instruction queue attached to a port/processeor'''
    def __init__(self, source, dest, amount, time):
        self.source = source
        self.dest = dest
        self.amount = amount
        self.time = time