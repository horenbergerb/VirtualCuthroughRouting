import random
import abc


##########
#Thoughts#
##########
#11/28/2020
#it seems like we might be just about ready. speed is definitely going to be an issue. i should start making a list of possible optimizations.
#i'm going to prioritize making tools for collecting measurements

#apart from that, 
#11/28/2020
#here's my implementation idea for "flits only stack in the output when the header is in the output"
#output queues simply don't move unless the queue is empty OR the first thing in the output is a header
# i re-run the inter-router algorithm for that router whenever the intra-router algorithm moves a flit
#seems to work, not sure if this will cause lag

#11/27/2020
#so recently i redesigned the router class in a big way.
#i realized many problems are simplified if the movements are queued up in the outgoing ports
#so incoming headers are processed into a request which gets put into the respective out port's queue
#this handles lots of issues with locking and whatnot in a very natural way

#I think i fixed most of the bugs with this new format, but i need to implement some additional assumptions about the movement (flits do not move when their header is sitting in an input port)

#after i smooth this out, though, i just need to start implementing measurement protocols (and check the message distance assumption)

#############
#ASSUMPTIONS#
#############
#distance is always less than 1/2 size, so there is always a clear shortest path (used implicitly in Router for header parsing)
#NOTE: Does this need to be implemented in the Processor message generation?
#NOTE: DON'T WE NEED DIM1, DIM2 TO BE ODD?

#################
#MEASURED VALUES#
#################
lifetimes = []

############
#PARAMETERS#
############
#threshhold before we start measuring lifetimes
T_THRESH = 50000
#includes header in count
MSG_LEN = 5
#message is created when rand(0, MSG_FREQ)==0, i.e. big MSG_FREQ means smaller generation chance
MSG_FREQ = 29
DIM1 = 6
DIM2 = 6
PATH_LEN = 3
#this is not yet implemented, i.e. do not change this from 4
PORTS = 4

###########
#CONSTANTS#
###########
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
DIRS = [UP, RIGHT, DOWN, LEFT]

##################
#ABSTRACT CLASSES#
##################
class Container():
    def __init__(self):
        self.Ibuffer = None
        self.Obuffer = None
        self.Ostorage = []
        self.instructions = None

    #NOTE: the "put" methods are the ones that determine whether a flit has moved in a given time unit
    #the "get" methods do not affect this
        
    #puts an item in the input buffer and resets whether a header has been parsed
    #WARNING: DOES NOT CHECK FOR OVERWRITING
    def putI(self, package):
        self.Ibuffer = package
        package.moved = True
        if isinstance(package, Header):
            package.parsed = False

    #puts an item in the output buffer, moves to storage if buffer is full
    def putO(self, package):
        if self.Obuffer == None:
            self.Obuffer = package
            package.moved = True
        else:
            self.Ostorage.append(package)
            package.moved = True

    #looks at the item in the buffer
    def peekI(self):
        return self.Ibuffer
    def peekO(self):
        return self.Obuffer
            
    #pops an item off input buffer
    def getI(self):
        out = self.Ibuffer
        self.Ibuffer = None
        return out

    #pops an item off output buffer, replaces from storage
    def getO(self):
        out = None
        if self.Obuffer != None:
            out = self.Obuffer
            if len(self.Ostorage) > 0:
                self.Obuffer = self.Ostorage.pop(0)
                self.Obuffer.moved = True
            else:
                self.Obuffer = None
        return out

    def reset_moved(self):
        if self.Ibuffer != None:
            self.Ibuffer.moved = False
            self.Ibuffer.lifetime += 1
        if self.Obuffer != None:
            self.Obuffer.moved = False
            self.Obuffer.lifetime += 1
        for flit in self.Ostorage:
            flit.moved = False
            flit.lifetime += 1

#########
#CLASSES#
#########

#single instruction for a router's instruction queues
class Instruction:
    def __init__(self, source, dest, amount, time):
        self.source = source
        self.dest = dest
        self.amount = amount
        self.time = time

class Flit:
    def __init__(self):
        self.moved = False
        self.lifetime = 0
                
class Header:
    def __init__(self, dest, length=MSG_LEN):        
        self.dest = dest
        self.length = length
        self.moved = False
        self.parsed = False
        self.lifetime = 0
        
class Processor(Container):
    def __init__(self):
        self.Ibuffer = None
        self.Obuffer = None
        self.Ostorage = []
        #this is a queue of requests for flits to be sent to the processor
        self.instructions = []

    #generates new msgs in processor; either sends straight to Obuffer or puts in storage
    #NOTE: Never sends message to itself
    def generate_msg(self, address):
        dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]
        #prevent messages sent to our own address
        while dest == address or (((address[0]-dest[0])%DIM1)+((address[1]-dest[1])%DIM1)) == PATH_LEN:
            dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]

        #print("    NEW MESSAGE W/ DEST: {}".format(dest))
        if self.Obuffer == None:
            self.Obuffer = Header(dest)
        else:
            self.Ostorage.append(Header(dest))
        #one taken off for header
        for x in range(0, MSG_LEN-1):
            self.Ostorage.append(Flit())

    #simulates internal flit movement. for processor, this is just munching inputs
    def move(self, time):
        global T_THRESH
        global debug_counter
        #munch those inputs
        if self.Ibuffer != None:
            #measure the lifetime
            if time > T_THRESH and isinstance(self.Ibuffer, Header):
                lifetimes.append(self.Ibuffer.lifetime)
                print("Found lifetime to measure")
            self.Ibuffer = None


    #step is called exactly once per unit time
    def step(self, address):
        
        #generate a message 1 in 10 steps
        if random.randint(0, MSG_FREQ) == 0:
            self.generate_msg(address)
                                 
#holds an amount of flits in input and output buffers
class Port(Container):
    def __init__(self):
        self.Ibuffer = None
        self.Obuffer = None
        self.Ostorage = []
        #instructions are the memory that tells us whether we're currently in the middle of transmitting a message through this port
        #set to [X, Y] to move Y flits from Ibuffer to port X OStorage
        #X=-1 means to send it to processor (i.e. we've arrived at destination)
        self.instructions = []   
                    
#receives messages from other routers in input ports, redirects to output ports or processor based on the header destination
class Router:
    def __init__(self, address, ports = PORTS):
        #address (used for header parsing and in router's processor for message generation)
        self.address = address
        self.time = 0

        #the four ports of the router
        #convention: [0,1,2,3] = [UP,RIGHT,DOWN,LEFT]
        self.ports = []
        for x in range(0, ports):
            self.ports.append(Port())

        #the router's processor
        self.processor = Processor()

    #debug function for reading out info
    def debug(self):
        print("Router Readout: ({}, {})".format(*(self.address)))
        port_list = []
        for x in range(0, len(self.ports)):
            port_list.append("Port {}".format(x))
        
        #show contents of each port
        line = []
        for x in range(0, len(self.ports)):
            #contents of Ibuffer
            in_string = "I: "
            if self.ports[x].Ibuffer != None:
                if isinstance(self.ports[x].Ibuffer, Header):
                    in_string += "H"
                if isinstance(self.ports[x].Ibuffer, Flit):
                    in_string += "F"
            #contents of Obuffer
            out_string = "O: "
            if self.ports[x].Obuffer != None:
                if isinstance(self.ports[x].Obuffer, Header):
                    out_string += "H"
                if isinstance(self.ports[x].Obuffer, Flit):
                    out_string += "F"
                for cur in self.ports[x].Ostorage:
                    if isinstance(cur, Header):
                        out_string += "H"
                    if isinstance(cur, Flit):
                        out_string += "F"

            line.append(in_string + " " + out_string)
        col_width = max(len(word) for row in [port_list, line] for word in row) + 2
        for row in [port_list, line]:
            print("".join(word.ljust(col_width) for word in row))
            
    #calculates instructions for port or processor; used when a new header appears in an Obuffer
    def parse_header(self, cur, source):
        instruction = Instruction(source, -1, cur.length, self.time)
        #instruction = [source, -1, cur.length, self.time]

        #mark this header as parsed
        cur.parsed = True
        #find best choice out of l/r (denoted false/true) options
        lr_dir = -1
        if ((self.address[1]-cur.dest[1])%DIM1 > (cur.dest[1]-self.address[1])%DIM1):
            lr_dir = RIGHT
        else:
            lr_dir = LEFT
        #note if we're already done moving l/r
        if self.address[1] == cur.dest[1]:
            lr_dir = -1

        #find best choice out of up/down (denoted false/true) options
        ud_dir = -1
        if ((self.address[0]-cur.dest[0])%DIM2 > (cur.dest[0]-self.address[0])%DIM2):
            ud_dir = DOWN
        else:
            ud_dir = UP
        #note if we're already done moving up/down
        if self.address[0] == cur.dest[0]:
            ud_dir = -1

        #if there's only one choice, return it
        if lr_dir == -1:
            instruction.dest = ud_dir
            return instruction
        if ud_dir == -1:
            instruction.dest = lr_dir
            return instruction

        '''
        #pick choice with shortest queue
        if (len(self.ports[lr_dir].Ostorage) +(self.ports[lr_dir].Obuffer != None)) < (len(self.ports[ud_dir].Ostorage) + (self.ports[ud_dir].Obuffer != None)):
            instruction.dest = lr_dir
        if (len(self.ports[ud_dir].Ostorage) +(self.ports[ud_dir].Obuffer != None)) < (len(self.ports[lr_dir].Ostorage) + (self.ports[lr_dir].Obuffer != None)):
            instruction.dest = ud_dir
        '''
        #picking free port with the smallest number
        if (len(self.ports[min(lr_dir, ud_dir)].Ostorage) +(self.ports[min(lr_dir, ud_dir)].Obuffer != None)) == 0:
            instruction.dest = min(lr_dir, ud_dir)
        elif (len(self.ports[max(lr_dir, ud_dir)].Ostorage) +(self.ports[max(lr_dir, ud_dir)].Obuffer != None)) == 0:
            instruction.dest = max(lr_dir, ud_dir)
        else:
            #tie breaker goes with larget occupied port number
            instruction.dest = max(lr_dir, ud_dir)
        #print("L/R: {}, U/D: {}".format(lr_dir, ud_dir))
        #print("Chosen port: {}".format(instruction.dest))
        return instruction

    #all about moving flits from IBuffers to OBuffers or to processor
    def move(self):
        #internal processor movement (Munching inputs)
        self.processor.move(self.time)
        #incrementing the queues of each output port
        for port in self.ports:
            if len(port.instructions) > 0:
                #pop old instructions
                if port.instructions[0].amount == 0:
                    port.instructions.pop(0)
            #if we still have instructions, try to take action
            if len(port.instructions) > 0:
                #flit to be grabbed
                if port.instructions[0].source != -1:
                    target = self.ports[port.instructions[0].source].peekI()
                else:
                    target = self.processor.peekO()
                #this is where we make sure we do not move unless the output is empty or has the header
                if target != None and not target.moved and (isinstance(target, Header) or isinstance(port.peekO(), Header) or port.peekO()==None or len(port.Ostorage) >= MSG_LEN):
                    #moving to another port
                    if port.instructions[0].source != -1:
                        port.putO(self.ports[port.instructions[0].source].getI())
                    else:
                        port.putO(self.processor.getO())
                    #moving to processor
                    #decrement amount
                    port.instructions[0].amount -= 1
        #incrementing processor queue
        if self.processor.peekI() == None:
            if len(self.processor.instructions) > 0:
                if self.processor.instructions[0].amount == 0:
                    print("Processor [{}, {}] finished instructions".format(self.address[0],self.address[1]))
                    self.processor.instructions.pop(0)
            if len(self.processor.instructions) > 0:
                target = self.ports[self.processor.instructions[0].source].peekI()
                if target != None and self.processor.peekI() == None and not target.moved:
                    self.processor.putI(self.ports[self.processor.instructions[0].source].getI())
                    self.processor.instructions[0].amount -= 1
            
    #looks at all the new inputs and creates instructions
    def parse_all_inputs(self):
        #################
        #PROCESSOR LOGIC#
        #################

        #if our processor has a header in OBuffer, parse it into processor instructions
        cur = self.processor.peekO()
        if isinstance(cur, Header) and not (cur.parsed or cur.moved):
            new_instr = self.parse_header(cur, -1)
            self.ports[new_instr.dest].instructions.append(new_instr)
            cur.parsed = True
            cur.moved = True
        
        ############
        #PORT LOGIC#
        ############
        #parsing the contents of input ports into instructions
        counter = 0
        for port in range(len(self.ports)):
            cur = self.ports[port].peekI()
            #NOTE: Parsing the header here takes up one flit, which is why moving a header takes 2 time units
            if isinstance(cur, Header) and not (cur.moved or cur.parsed):
                #eat headers that have arrived at their dest
                if cur.dest == self.address:
                    self.processor.instructions.append(Instruction(port, -1, cur.length, self.time))
                else:
                    new_instr = self.parse_header(cur, port)
                    self.ports[new_instr.dest].instructions.append(new_instr)
                cur.moved = True
                cur.parsed = True

            counter += 1
            


    def step(self, time):
        self.time = time

        #step processor
        self.processor.step(self.address)

        self.parse_all_inputs()
        
        self.move()

    def reset_moved(self):
        #reset all flits
        self.processor.reset_moved()
        for port in self.ports:
            port.reset_moved()
        
    
class TwoDToroidalNetwork:
    #routers in the self.routers matrix are connected to adjacent routers
    #connections apply modulo dim1 and dim2 (because it's a toroidal network)
    def __init__(self):
        random.seed()
        self.time = 0
        
        #table of routers
        self.routers = []
        for x in range(0, DIM1):
            cur_row = []
            for y in range(0, DIM2):
                #creates router with the address corresponding to network dimensions
                cur_row.append(Router([x, y]))
            self.routers.append(cur_row)

    def debug(self):
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                self.routers[i][j].debug()

    def step(self):
        #part 1: iterate over all routers, continue moving until there's nothign left to move
        moving = 0
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                #inter-router movement
                self.routers[i][j].step(self.time)

        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                #intra-router movement
                #[i][j] is rowsxcolumns
                for p in DIRS:
                    if self.routers[i][j].ports[p].peekO() != None and not self.routers[i][j].ports[p].peekO().moved:
                        if p == UP:
                            if self.routers[(i-1)%DIM1][j].ports[DOWN].peekI() == None:
                                self.routers[(i-1)%DIM1][j].ports[DOWN].putI(self.routers[i][j].ports[p].getO())
                                self.routers[i][j].move()
                        elif p == RIGHT:
                            if self.routers[i][(j+1)%DIM2].ports[LEFT].peekI() == None:
                                self.routers[i][(j+1)%DIM2].ports[LEFT].putI(self.routers[i][j].ports[p].getO())
                                self.routers[i][j].move()
                        elif p == DOWN:
                            if self.routers[(i+1)%DIM1][j].ports[UP].peekI() == None:
                                self.routers[(i+1)%DIM1][j].ports[UP].putI(self.routers[i][j].ports[p].getO())
                                self.routers[i][j].move()
                        elif p == LEFT:
                            if self.routers[i][(j-1)%DIM2].ports[RIGHT].peekI() == None:
                                self.routers[i][(j-1)%DIM2].ports[RIGHT].putI(self.routers[i][j].ports[p].getO())
                                self.routers[i][j].move()

                
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                self.routers[i][j].reset_moved()
                self.routers[i][j].debug()

        self.time += 1

test_net = TwoDToroidalNetwork()

for x in range(0,60000):
    print("\n\nSTEP {}".format(x))
    test_net.step()

print(lifetimes)
print("Average lifetime: {}".format(float(sum(lifetimes))/float(len(lifetimes))))
