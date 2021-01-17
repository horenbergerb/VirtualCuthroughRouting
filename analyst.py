from Classes.twodtoroidalnetwork import TwoDToroidalNetwork
from matplotlib import pyplot as plt
import numpy as np
import csv
import itertools
import os

def save(cols, col_names, dest):
    with open(dest, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)
        rows = list(itertools.zip_longest(*cols))
        writer.writerows(rows)

#######################
# CALCULATION/UTILITY #
#######################
        
        
def get_avg_lifetime(network):
    lifetimes = network.get_lifetimes()
    if len(lifetimes) == 0:
        return 0
    lengths = [x[1]-x[0] for x in lifetimes]
    return sum(lengths)/len(lengths)


def get_lifetime_lengths(network):
    lifetimes = network.get_lifetimes()
    return [x[1]-x[0] for x in lifetimes]


def get_birth_times(network):
    lifetimes = network.get_lifetimes()
    return [x[0] for x in lifetimes]


###############################
# NUMERICAL EXPERIMENTAL DATA #
###############################


def get_avg_lifetimes_vs_prob(DIM, MSG_LEN, SAMPLE_THRESH, PATH_LEN, probs, do_save=True):
    avgs = []
    dir_name = "latency{}x{}_{}flit_path{}".format(DIM, DIM, MSG_LEN, PATH_LEN)
    try:
        os.mkdir(dir_name)
    except:
        pass
    
    for FREQ in probs:
        cur_net = TwoDToroidalNetwork(DIM1=DIM, DIM2=DIM, MSG_LEN=MSG_LEN, SAMPLE_THRESH=SAMPLE_THRESH, MSG_FREQ=FREQ, PATH_LEN=PATH_LEN)
        #max time simulated is based on section 4.1 of the paper
        cur_net.step(amount=int(SAMPLE_THRESH+(40*PATH_LEN/FREQ)))
        if do_save:
            x = get_birth_times(cur_net)
            y = get_lifetime_lengths(cur_net)
            save([x,y],["Birth Time", "Lifetime"], dir_name+"/birth_vs_lifetime_{}.csv".format(FREQ))
        avgs.append(get_avg_lifetime(cur_net))
        if get_avg_lifetime(cur_net) == 0:
            break

    if do_save:
        save([probs, avgs],["Probability", "Average Lifetime"], dir_name+"/avg_lifetimes_vs_prob.csv")
    return probs, avgs


def test_all_combinations(dims, path_lens, msg_lens, probs):
    for dim in dims:
        for path_len in path_lens:
            if path_len > dim:
                break
            for msg_len in msg_lens:
                get_avg_lifetimes_vs_prob(dim, msg_len, 50000, path_len, probs, do_save=True)
                make_plots_for_dir("latency{}x{}_{}flit_path{}".format(dim, dim, msg_len, path_len))


############
# PLOTTING #
############


def plot_scatter(x, y, labels, show=True, do_save=False, filename="plot.png"):
    plt.scatter(x, y)
    plt.xlabel(labels[0])
    plt.ylabel(labels[1])
    if show:
        plt.show()
    if do_save:
        plt.savefig(filename)
    plt.clf()


def plot_lifetimes(network, show=True, do_save=False, filename="lifetimes.pngs"):
    x = [a[0] for a in network.get_lifetimes()]
    y = get_lifetime_lengths(network)
    plot_scatter(x, y, ['Birth Time', 'Lifetime Length'], show=show, do_save=do_save, filename=filename)

def make_plots_for_dir(dir):
    csvs = [f for f in os.listdir(dir) if f.endswith('.csv')]
    for cur_csv in csvs:
        with open(dir+"/" + cur_csv) as f:
            csv_reader = csv.reader(f, delimiter=',')
            labels = next(csv_reader, None)
            x = []
            y = []
            for row in csv_reader:
                x.append(float(row[0]))
                y.append(float(row[1]))
            if len(x) > 0:
                plot_scatter(x, y, labels, show=False, do_save=True,filename=dir+"/"+cur_csv[:-4]+".png")
