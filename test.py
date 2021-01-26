from analyst import *

# A comprehensive test
'''
dims = [2,4,6,8,16,32]
path_lens = [3,5,7,11,15]
msg_lens = [20,30,40,50]
test_all_combinations(dims, path_lens, msg_lens)
'''

# This is all the requested data
def get_requested_data():
    probs = [.01, .02, .025, .0275, .03, .0325, .035, .0375, .04, .0425, .045, .0475, .05, .0525, .055, .0575, .06, .0625, .065, .0675, .07, .0725, .075, .0775, .08, .0825, .085, .0875, .09, .0925, .095, .0975, .1]

    dims = [16, 32]
    path_lens = [3,5,7]
    msg_lens = [20,30,40]
    test_all_combinations(dims, path_lens, msg_lens, probs)

    dims = [32]
    path_lens = [11]
    msg_lens = [30,40]
    test_all_combinations(dims, path_lens, msg_lens, probs)

    dims = [32]
    path_lens = [15]
    msg_lens = [40,50]
    test_all_combinations(dims, path_lens, msg_lens, probs)

def get_test_data():
    # Just noodling
    probs = [.01, .02, .03, .035, .04, .0425, .045, .0475, .05, .0525, .055, .0575, .06, .0625, .065, .0675, .07, .0725, .075, .0775, .08, .0825, .085, .0875, .09, .0925, .095, .0975, .1]
    dims = [4]
    path_lens = [2]
    msg_lens = [20]
    test_all_combinations(dims, path_lens, msg_lens, probs)

#get_requested_data()
get_test_data()
