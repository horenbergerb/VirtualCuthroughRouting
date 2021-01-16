from analyst import test_all_combinations

dims = [2,4,6,8,16,32]
path_lens = [3,5,7,11,15]
msg_lens = [20,30,40,50]
test_all_combinations(dims, path_lens, msg_lens)
