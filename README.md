# README

## Overview

This code simulates a network of processors which process and produce messages. The processors pass messages between each other, and this process is facilitated by routers. Every messages is a chain of flits. At the front of the chain is a header which contains information about the message's destination.

Every processor is contained within a router. The routers are arranged in a 2D toroidal network, i.e. every router is connected to four adjacent routers (one above, below, left, and right), there is a finite number of routers in any of the four directions, and then you "wrap back around" to the router where you started. For example, if you leave through the "up" output port of some router and keep proceeding through "up" ports, eventually you will return to your starting router through it's "down" input port.

In most standard routing systems, the input and output ports of every router can only hold one flit at a time. Because processing headers and other processes take time, chains of flits can get backed up throughout the system. This can potentially cause deadlock, which is a critical failure of the routing system.

The goal of this code is to demonstrate a particular routing methodology called "virtual cut-through routing." In this system, the output buffers of the routers have unlimited memory. As a result, they can hold an entire chain of flits if need be. As a result, deadlock can always be avoided.

Of theoretical interest is the latency of the system when it has reached a steady state of activity. To measure this, we will simulate a 2D toroidal network where messages are randomly generated in processors throughout at some fixed rate.

## How to use this code

Currently, running the file runs a test network and prints a rudimentary visual output demonstrating the router processes. In general, running the code is as simple as:

1) Instantiating the network via "test_network = TwoDToroidalNetwork()"
2) Looping the method "test_network.step()"

There are many parameters within the code which can be tweaked. These are located at the top of the file and include message length, network size in each dimension, and number of ports (this one is NOT yet implemented).

## The Code

### Class Overviews

At the highest level, the system is a class, called "TwoDToroidalNetwork." Within this is a grid of "Router" objects. The Router objects are composed of four "Ports," which have input/output buffers, and one "Processor," which also has input/output buffers

"Header" and "Flit" objects are created by Processors, and these live in input/output buffers, and the system moves them between buffers at each time step according to some logic.

Processors and Ports are both implementations of the abstract class "Container," which has lots of boilerplate code for grabbing/storing information in buffers.

### How it Runs

A TwoDToroidalNetwork object, let's call it "network,"  is instantiated. Each time the method "network.step()" is called, the entire system progresses one time step. This is done in two parts, which I call "move" and "step." "Move" further breaks into two parts, the inter-router movement and intra-router movement. The former is handled within each router, via the router.move() method. The latter is handled within network.step().

The "Move" part iterates many times until no more movement occurs. This is a simple way to address logical problems where A wants to move to B, and B wants to move to C. In iteration 1, A sees B is occupied and doesn't move, then B moves to C. In iteration 2, A moves to B. In iteration 3, there is no more movement to be done this time step.

The "Step" part handles the rest of the logic for each time step. This includes random message generation. Additionally, we reset the status of which flits have already moved, so they are all ready to move again during then next time step. 

### Details on Routing

Intra-router routing is simple. Since every input port is connected to exactly one output port, there is no need for the implementation of queues, memory, etc.

Inter-router routing is more elaborate. When a header is received in an input, the correct output port must be determined by parsing the header destination and computing the shortest path. Then, the input port must "remember" the correct output port while it forwards the rest of the flits in the message. To handle this, I implemented the router.parse() method for determining the destination, and the "port.instruction" variable for tracking where flits are currently being directed.

*Currently, the inter-router routing does not have a queue system for obtaining access to an output port. If two input ports have many messages destined for the same output port, the input port which is checked first will always get priority.*

## Thoughts

### To Do:

1) Restrict flits to accumulate only when header is in the output port
2) Implement inter-router queue for output port access
3) Create unit tests for debugging
4) Rewrite documentation using docstring, PEP 8
5) Create measurement facilities (latency, detect saturation pt, count total number of messages, etc)
6) Test larger cases (msg len 200 flits)

### Long Term:

1) Implement higher dimensional networks (would require rewrite of Network logic and internal Router logic to handle arbitrary number of ports)

### Would Be Nice:

1) Create better visuals