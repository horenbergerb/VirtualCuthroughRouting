

##############
# PARAMETERS #
##############


# Length of a message. Includes header in count
MSG_LEN = 20
# Frequency at which processors create messages
# Message is created when randuniform(0, 1) < MSG_FREQ
MSG_FREQ = .4
# Distance of destination from source for messages
PATH_LEN = 2
# Lowest time at which spawned headers will have lifetimes recorded
SAMPLE_THRESH = 50000
# Size of the network along each axis
DIM1 = 2
DIM2 = 2

#############
# CONSTANTS #
#############


UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
DIRS = [UP, RIGHT, DOWN, LEFT]
PORTS = 4
