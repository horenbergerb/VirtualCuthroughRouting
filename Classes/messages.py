from collections import deque

class Flit:
    '''Flit object which follows the Header of a message'''
    def __init__(self, headerID):
        self.moved = False
        self.headerID = headerID
        self.is_header = False

        
class Header:
    '''Header object which leads message.'''
    def __init__(self, dest, time, length):
        self.dest = dest
        self.length = length
        self.moved = False
        self.parsed = False
        self.time = time
        self.is_header = True


class Message:
    def __init__(self, header):
        self.items = deque([])
        self.headerID = id(header)
        self.popped = 0
        self.next_message = None
        self.length = 0

    def __str__(self):
        #we truncate the ID for aesthetic purposes
        result = "{}: ".format(self.headerID % 1000)
        for cur in self.items:
            if isinstance(cur, Header):
                result += "H"
            else:
                result += "F"
        return result

    def add_flit(self, flit):
        if not self.items or self.items[0].is_header:
            flit.moved = True
            self.items.append(flit)
            self.length += 1
            return True
        return False

    def pop_flit(self):
        if not self.items:
            return None
        self.popped += 1
        self.length -= 1
        return self.items.popleft()

    def peek(self):
        '''Returns the flit next in line to be passed'''
        if self.items:
            return self.items[0]
        return None

    
class FlitQueue:
    def __init__(self, MSG_LEN):
        self.queue = deque()
        self.MSG_LEN = MSG_LEN
        self.length = 0
        
    def __str__(self):
        result = ""
        for cur in self.queue:
            result += str(cur) + "\n"
        return result

    def pop_flit(self):
        if self.queue:
            result = self.queue[0].pop_flit()
            if self.queue[0].popped >= self.MSG_LEN:
                self.queue.popleft()
                self.length -= 1
            result.moved = True
            return result
        return None

    def peek(self):
        if self.queue:
            result = self.queue[0].peek()
            return result
        return None

    def add_msg(self, new_msg):
        self.queue.append(new_msg)
        self.length += 1

    '''
    def add_flit(self, new_flit):
        if new_flit.is_header:
            new_flit.moved = True
            new_msg = Message(new_flit)
            self.queue.append(new_msg)
            return True
        else:
            for cur_msg in queue:
                if cur_msg.headerID == new_flit.headerID and (not cur_msg.items or cur_msg.items[0].is_header):
                    new_flit.moved = True
                    return cur_msg.add_flit(new_flit)
    '''
    '''
    def get_length(self):
        length = 0
        for x in self.queue:
            length += self.MSG_LEN-x.popped
        return length
    '''
    def set_moved(self):
        '''Rather unpleasantly hacked so that
        only relevant msgs are tampered with'''
        for cur_msg in range(0,min([2,self.length])):
            for cur_flit in self.queue[cur_msg].items:
                cur_flit.moved = True
        
    def reset_moved(self):
        for cur_msg in range(0,min([2,self.length])):
            for cur_flit in range(0,min([self.queue[cur_msg].length, 2])):
                self.queue[cur_msg].items[cur_flit].moved = False
