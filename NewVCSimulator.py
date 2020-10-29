import random
import abc

##########
#Thoughts#
##########
#needs a QUEUE internal to the router. currently preference is being given to ports in the order they're checked (0,1,2,3), so it's possible messages could be unduly neglected.

#i should add a locking system to the ports in the router that uses a queue of requests; sending a request adds you to the lock queue, then you simply wait until the lock says it is reserved for you. When done, you must tell the lock you have finished and it will move to the next item in its queue.

#############
#ASSUMPTIONS#
#############
#distance is always less than 1/2 size, so there is always a clear shortest path (used implicitly in Router for header parsing)
#NOTE: Does this need to be implemented in the Processor message generation?
#NOTE: DON'T WE NEED DIM1, DIM2 TO BE ODD?

############
#PARAMETERS#
############
#includes header in count
MSG_LEN = 4
#message is created when rand(0, MSG_FREQ)==0, i.e. big MSG_FREQ means smaller generation chance
MSG_FREQ = 20
DIM1 = 2
DIM2 = 2
PORTS = 4

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
        
    #puts an item in the input buffer
    #WARNING: DOES NOT CHECK FOR OVERWRITING
    def putI(self, package):
        self.Ibuffer = package
        package.moved = True

    #puts an item in the output buffer, moves to storage if buffer is full
    def putO(self, package):
        if self.Obuffer == None:
            self.Obuffer = package
            package.moved = True
        else:
            self.Ostorage.append(package)

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
        if self.Obuffer != None:
            self.Obuffer.moved = False
        for flit in self.Ostorage:
            flit.moved = False

#########
#CLASSES#
#########
    
class Flit:
    def __init__(self):
        self.moved = False
                
class Header:
    def __init__(self, dest, length=MSG_LEN):        
        self.dest = dest
        self.length = length
        self.moved = False
        
class Processor(Container):
    def __init__(self):
        self.Ibuffer = None
        self.Obuffer = None
        self.Ostorage = []
        #instructions are the memory that tells us whether we're in the middle of moving a message
        #they are read by the Router and used to direct movement from the processor OBuffer to a port OBuffer
        self.instructions = None

    #generates new msgs in processor; either sends straight to Obuffer or puts in storage
    #NOTE: Never sends message to itself
    def generate_msg(self, address):
        dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]
        #prevent messages sent to our own address
        while dest == address:
            dest = [random.randint(0, (DIM1-1)), random.randint(0, (DIM2-1))]

        print("    NEW MESSAGE W/ DEST: {}".format(dest))
        if self.Obuffer == None:
            self.Obuffer = Header(dest)
        else:
            self.Ostorage.append(Header(dest))
        #one taken off for header
        for x in range(0, MSG_LEN-1):
            self.Ostorage.append(Flit())

    #move is called many times per unit time
    def move(self):
        moved = 0
        #munch those inputs
        if self.Ibuffer != None and not self.Ibuffer.moved:
            self.Ibuffer = None
            moved = 1

        return moved

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
        self.instructions = None    
                    
#receives messages from other routers in input ports, redirects to output ports or processor based on the header destination
class Router:
    def __init__(self, address, ports = PORTS):
        #address (used for header parsing and in router's processor for message generation)
        self.address = address

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
    def parse_header(self, cur):
        instructions = [-1, cur.length]
        #find best choice out of l/r (denoted false/true) options
        lr_dir = -1
        if ((self.address[1]-cur.dest[1])%DIM1 > (cur.dest[1]-self.address[1])%DIM1):
            lr_dir = 1
        else:
            lr_dir = 3
        #note if we're already done moving l/r
        if self.address[1] == cur.dest[1]:
            lr_dir = -1

        #find best choice out of up/down (denoted false/true) options
        ud_dir = -1
        if ((self.address[0]-cur.dest[0])%DIM2 > (cur.dest[0]-self.address[0])%DIM2):
            ud_dir = 0
        else:
            ud_dir = 2
        #note if we're already done moving up/down
        if self.address[0] == cur.dest[0]:
            ud_dir = -1

        #if there's only one choice, return it
        if lr_dir == -1:
            instructions[0] = ud_dir
            return instructions
        if ud_dir == -1:
            instructions[0] = lr_dir
            return instructions
    
            
        #pick choice with shortest queue
        if (len(self.ports[lr_dir].Ostorage) +(self.ports[lr_dir].Obuffer != None)) < (len(self.ports[ud_dir].Ostorage) + (self.ports[ud_dir].Obuffer != None)):
            instructions[0] = lr_dir
        else:
            #tie breaker goes with ud_dir
            instructions[0] = ud_dir
        print("L/R: {}, U/D: {}".format(lr_dir, ud_dir))
        print("Chosen port: {}".format(instructions[0]))
        return instructions

    #called many times per time unit; all about moving flits from IBuffers to OBuffers or to processor
    def move(self):
        moved = 0
        #################
        #PROCESSOR LOGIC#
        #################
        #internal processor movement (Munching inputs)
        moved = self.processor.move()

        #if our processor has a header in OBuffer, parse it into processor instructions
        cur = self.processor.peekO()
        if isinstance(cur, Header) and not cur.moved:
            new_instructions = self.parse_header(cur)
            #IMPORTANT! Only give the processor instructions if no other port is already transporting flits to destination port
            locked = False
            for x in range(0, len(self.ports)):
                if self.ports[x].instructions != None and self.ports[x].instructions[0] == new_instructions[0] and self.ports[x].instructions[1] > 0:
                    locked = True
                    break
            if not locked:
                self.processor.instructions = self.parse_header(cur)

        #if our processor has instructions from a parsed header, try to sent the contents of the out buffer to the desired port
        if self.processor.instructions != None:
            #print("Found Instructions for processor output in router ({},{}): ({},{})".format(*(self.address+self.processor.instructions)))
            if self.processor.instructions[1] > 0 and self.processor.peekO() != None and not self.processor.peekO().moved:
                self.ports[self.processor.instructions[0]].putO(self.processor.getO())
                self.processor.instructions[1] -= 1
                moved = 1
            elif self.processor.instructions[1] <= 0:
                self.processor.instructions = None

        ############
        #PORT LOGIC#
        ############
        #moving the contents of INPUT buffer in ports
        counter = 0
        for port in self.ports:
            #If we have already parsed a header and have instructions:
            if port.instructions != None:
                #print("Found Instructions for port {} in router ({},{}): ({},{})".format(*([counter]+self.address+port.instructions)))
                #flits which have reached their destination go to processor
                if port.instructions[0] == -1 and port.instructions[1] > 0:
                    if self.processor.peekI() == None and port.peekI() != None and not port.peekI().moved:
                        self.processor.putI(port.getI())
                        moved = 1
                        port.instructions[1] -= 1
                #otherwise just send the flits along
                elif port.instructions[1] > 0 and port.peekI() != None and not port.peekI().moved:
                    self.ports[port.instructions[0]].putO(port.getI())
                    moved = 1
                    port.instructions[1] -= 1
                #erase instructions if we've moved all the expected flits
                elif port.instructions[1] <= 0:
                    print("   WIPING INSTRUCTIONS")
                    port.instructions = None

            #otherwise we expect either a header or nothing
            cur = port.peekI()
            if cur != None and port.instructions == None:
                #NOTE: Parsing the header here takes up one flit, which is why moving a header takes 2 time units
                if isinstance(cur, Header) and not cur.moved:
                    #eat headers that have arrived at their dest
                    if cur.dest == self.address:
                        port.instructions = [-1, cur.length]
                        cur.moved = True
                        moved = 1
                    else:
                        new_instructions = self.parse_header(cur)
                        locked = False
                        for x in range(0, len(self.ports)):
                            if self.ports[x].instructions != None and self.ports[x].instructions[0] == new_instructions[0] and self.ports[x].instructions[1] > 0:
                                locked = True
                                break
                        if not locked:
                            port.instructions = self.parse_header(cur)
                            cur.moved = True
                            moved = 1
                    
                if isinstance(cur, Flit):
                    raise Exception("Rogue flit in port of router [{},{}]".format(*(self.address)))
            counter += 1
            
        return moved

    #takes router id
    def step(self):
        #step processor
        self.processor.step(self.address)

        #reset all flits
        self.processor.reset_moved()
        for port in self.ports:
            port.reset_moved()
    
class TwoDToroidalNetwork:
    #routers in the self.routers matrix are connected to adjacent routers
    #connections apply modulo dim1 and dim2 (because it's a toroidal network)
    def __init__(self):
        random.seed()
                
        #table of routers
        self.routers = []
        for x in range(0, DIM1):
            cur_row = []
            for y in range(0, DIM2):
                #creates router with the address corresponding to network dimensions
                cur_row.append(Router([x, y]))
            self.routers.append(cur_row)

    def step(self):
        #part 1: iterate over all routers, continue moving until there's nothign left to move
        moving = 1
        while moving > 0:
            moving = 0
            for i in range(0, len(self.routers)):
                for j in range(0, len(self.routers[0])):
                    #inter-router movement
                    moving += self.routers[i][j].move()

                    #intra-router movement
                    #[i][j] is rowsxcolumns
                    for p in range(0, PORTS):
                        if self.routers[i][j].ports[p].peekO() != None and not self.routers[i][j].ports[p].peekO().moved:
                            if p == 0:
                                if self.routers[(i-1)%DIM1][j].ports[2].peekI() == None:
                                    moving += 1
                                    self.routers[(i-1)%DIM1][j].ports[2].putI(self.routers[i][j].ports[p].getO())
                            elif p == 1:
                                if self.routers[i][(j+1)%DIM2].ports[3].peekI() == None:
                                    moving += 1
                                    self.routers[i][(j+1)%DIM2].ports[3].putI(self.routers[i][j].ports[p].getO())
                            elif p == 2:
                                if self.routers[(i+1)%DIM1][j].ports[0].peekI() == None:
                                    moving += 1
                                    self.routers[(i+1)%DIM1][j].ports[0].putI(self.routers[i][j].ports[p].getO())
                            elif p == 3:
                                if self.routers[i][(j-1)%DIM2].ports[1].peekI() == None:
                                    moving += 1
                                    self.routers[i][(j-1)%DIM2].ports[1].putI(self.routers[i][j].ports[p].getO())
                            
        #(electric boogaloo) part 2: step all the routers internally
        for i in range(0, len(self.routers)):
            for j in range(0, len(self.routers[0])):
                self.routers[i][j].step()
                self.routers[i][j].debug()


test_net = TwoDToroidalNetwork()

for x in range(0,20):
    print("\n\nSTEP {}".format(x))
    test_net.step()
