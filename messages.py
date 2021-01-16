from parameters import MSG_LEN


class Flit:
    '''Flit object which follows the Header of a message'''
    def __init__(self, headerID):
        self.moved = False
        self.headerID = headerID

        
class Header:
    '''Header object which leads message.'''
    def __init__(self, dest, time, length=MSG_LEN):
        self.dest = dest
        self.length = length
        self.moved = False
        self.parsed = False
        self.time = time


class Message:
    def __init__(self, header):
        self.items = [header]
        self.headerID = id(header)
        self.popped = 0

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
        if not self.items or isinstance(self.items[0], Header):
            flit.moved = True
            self.items.append(flit)
            return True
        return False

    def pop_flit(self):
        if not self.items:
            return None
        self.popped += 1
        return self.items.pop(0)

    def peek(self):
        '''Returns the flit next in line to be passed'''
        if self.items:
            return self.items[0]
        return None

    
class FlitQueue:
    def __init__(self):
        self.queue = []

    def __str__(self):
        result = ""
        for cur in self.queue:
            result += str(cur) + "\n"
        return result

    def pop_flit(self):
        if self.queue:
            result = self.queue[0].pop_flit()
            if self.queue[0].popped >= MSG_LEN:
                self.queue.pop(0)
            result.moved = True
            return result
        return None

    def peek(self):
        if self.queue:
            result = self.queue[0].peek()
            return result
        return None

    def add_flit(self, new_flit):
        if isinstance(new_flit, Header):
            new_flit.moved = True
            new_msg = Message(new_flit)
            self.queue.append(new_msg)
            return True
        else:
            for cur_msg in self.queue:
                if cur_msg.headerID == new_flit.headerID and (not cur_msg.items or isinstance(cur_msg.items[0], Header)):
                    new_flit.moved = True
                    return cur_msg.add_flit(new_flit)

    def get_length(self):
        length = 0
        for x in self.queue:
            length += len(x.items)
        return length

    def set_moved(self):
        for cur_msg in self.queue:
            for cur_flit in cur_msg.items:
                cur_flit.moved = True
        
    def reset_moved(self):
        for cur_msg in self.queue:
            for cur_flit in cur_msg.items:
                cur_flit.moved = False
