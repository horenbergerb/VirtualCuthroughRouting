

##############
# PARAMETERS #
##############


# Length of a message. Includes header in count
MSG_LEN = 4
# Frequency at which processors create messages
# Message is created when rand(0, MSG_FREQ)==0
# big MSG_FREQ means smaller generation chance
MSG_FREQ = 20
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
