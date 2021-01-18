# README

## Overview

This code simulates a network of routers containing processors which process and produce messages. The routers pass messages between their processors. The messages themselves are chains of flits. At the front of the chain is a header flit which contains information about the message's destination, among other things.

The routers are arranged in a 2D toroidal network, i.e. every router is connected to four adjacent routers (one above, below, left, and right), there is a finite number of routers in any of the four directions, and then you "wrap back around" to the router where you started. For example, if you leave through the "up" output port of some router and keep proceeding through "up" ports, eventually you will return to your starting router through it's "down" input port.

In most standard routing systems, the input and output ports of every router can only hold one flit at a time. Because processing headers and other processes take time, chains of flits can get backed up throughout the system. This can potentially cause deadlock, which is a critical failure of the routing system.

The goal of this code is to demonstrate a particular routing methodology called "virtual cut-through routing." In this system, the output buffers of the routers have unlimited capacity to hold flits (with some specific caveats). An output buffer can hold many messages at once. As a result, deadlock can always be avoided.

Of theoretical interest is the latency of the system when it has reached a steady state of activity. To measure this, we will simulate a 2D toroidal network where messages are randomly generated in processors throughout at some fixed rate.

## How to use this code

Simulating a network is as simple as

1) Instantiating the network via "test_network = TwoDToroidalNetwork()"
2) Looping the method "test_network.step()"

In the parent directory, there are analytical tools in analyst.py, and
you can see some examples of use in test.py.

## Note On Optimized Computation

To run this code I used PyPy:

https://www.pypy.org/

This makes a marked improvement on the computation time.

## The Code

### Class Overviews

At the highest level, the system is a class, called "TwoDToroidalNetwork."
Within this is a "RouterGrid" of "Router" objects.
The Router objects are composed of four "Ports,"
which have input/output buffers, and one "Processor,"
which also has input/output buffers.
"Ports" and "Processors" are both implementations of the "Container" class.
"Containers" have an "InstructionQueue" which tells them
what flits are queued to arrive at this container.
"Containers" also have a "FlitQueue" which functions as the
unlimited storage buffer for outgoing flits.
"FlitQueue" sorts "Header" and their respective "Flit" objects
sorted into "Messages."

"Header" and "Flit" objects are created by Processors, hop along input/output buffers towards their destination port. Their path is controlled by the "Router" (intra-router movement) and "RouterGrid" (inter-router movement) objects.

### How it Runs

A TwoDToroidalNetwork object, let's call it example_net, is instantiated. Each time the method example_net.step() is called, the entire system progresses one time step. A time step has two parts:

Move: Flits are physically relocated
Step: New messages are generated, newly-arrived flits are parsed into inter-router instructions, and other things happen 

### Details on Routing

Intra-router routing is simple. Since every input port is connected to exactly one output port, there is no need for the implementation of queues, memory, etc.

Inter-router routing is more elaborate. When a header is received in an input, the correct output port must be determined by parsing the header destination and computing the shortest path. Once the destination port is determined, an instruction is generated and attached to the InstructionQueue for that port.

## Thoughts

### To Do:

1) Create unit tests for debugging
2) Rewrite documentation using docstring, PEP 8
3) Create process to automatically detect saturation/stability

### Long Term:

1) Implement higher dimensional networks (would require rewrite of Network logic and internal Router logic to handle arbitrary number of ports)

### Would Be Nice:

1) Create better/more visuals
