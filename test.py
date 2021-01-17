from analyst import *
'''
dims = [2,4,6,8,16,32]
path_lens = [3,5,7,11,15]
msg_lens = [20,30,40,50]
test_all_combinations(dims, path_lens, msg_lens)
'''
# this is all the requested data
'''
dims = [16, 32]
path_lens = [3,5,7]
msg_lens = [20,30,40]
test_all_combinations(dims, path_lens, msg_lens)
'''
'''
dims = [32]
path_lens = [11]
msg_lens = [30,40]
test_all_combinations(dims, path_lens, msg_lens)
'''
'''
dims = [32]
path_lens = [15]
msg_lens = [40,50]
test_all_combinations(dims, path_lens, msg_lens)
'''

probs = [.01, .02, .03, .04, .045, .05, .06, .065, .07, .075, .08, .0825, .085, .0875,.09,.0925,.095,.0975,.1]

get_avg_lifetimes_vs_prob(2, 10, 50000, 2, probs)
make_plots_for_dir("latency2x2_10flit_path2")

get_avg_lifetimes_vs_prob(4, 10, 50000, 2, probs)
make_plots_for_dir("latency4x4_10flit_path2")

get_avg_lifetimes_vs_prob(6, 10, 50000, 2, probs)
make_plots_for_dir("latency6x6_10flit_path2")
