from twodtoroidalnetwork import TwoDToroidalNetwork
from matplotlib import pyplot as plt
import numpy as np

#test_net.routers[i][j].ports[k].Obuffer
#test_net.routers[0][0].ports[0].instructions.get()


def plot_birth_vs_lifetime(network, show=True, save=False, filename="birth_vs_lifetime.png"):
    lifetimes = network.get_lifetimes()
    lengths = [x[1]-x[0] for x in lifetimes]
    birth_time = [x[0] for x in lifetimes]

    plt.scatter(birth_time, lengths)
    if show:
        plt.show()
    if save:
        plt.savefig(filename)
    plt.clf()
    
def get_avg_lifetime(network):
    lifetimes = network.get_lifetimes()
    lengths = [x[1]-x[0] for x in lifetimes]
    return sum(lengths)/len(lengths)


def plot_avg_lifetimes_vs_prob(min_prob=.0025, max_prob=.0425, interval=.0025, save_mid_plots=False, show=True, save=False, filename="avg_lifetimes_vs_prob.png"):
    probs = []
    avgs = []
    for FREQ in np.arange(min_prob, max_prob, interval):
        cur_net = TwoDToroidalNetwork(MSG_FREQ=FREQ)
        cur_net.step(amount=70000)
        if save_mid_plots:
            plot_birth_vs_lifetime(cur_net,show=False, save=True, filename="birth_vs_lifetime_{}.png".format(FREQ))
        probs.append(FREQ)
        avgs.append(get_avg_lifetime(cur_net))
    plt.plot(probs, avgs)
    if save:
        plt.savefig(filename)
    if show:
        plt.show()
    plt.clf()


plot_avg_lifetimes_vs_prob(save_mid_plots=True,show=True,save=True)

# test_net = TwoDToroidalNetwork()
# test_net.step(amount=10000, do_print=False)
