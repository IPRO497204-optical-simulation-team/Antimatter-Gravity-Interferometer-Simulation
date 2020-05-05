import sys

from optical_simulation.demo import multiCoreTest

import matplotlib.pyplot as plt
import argparse


def get_args_from_command_line():
    """Get arguments from the command line."""

    parser = argparse.ArgumentParser()

    parser.add_argument('--runs',
                        default=5,
                        type=int,
                        help="Number of times program is to run, with linearly increasing processes")

    parser.add_argument('--cores',
                        default=8,
                        type=int,
                        help="Number of cores to utilize with multiprocessor")

    parser.add_argument('--multiplier',
                        default=200000,
                        type=int,
                        help="Number of processes to increase by in each iteration of for loop")

    parser.add_argument('--time',
                        default=1.00,
                        type=float,
                        help="Sleep timer to mitigate our code's race condition")

    return parser.parse_args()


if __name__ == '__main__':

    args = get_args_from_command_line()

    runs = args.runs
    cores = args.cores
    multiplier = args.multiplier
    time = args.time

    # Arrays used for storing results
    timesArray = []
    ratioArray = []

    xLabel = 'Processes running *(' + str(multiplier) + ")"
    # Run demo n times, increasing number of processes to run each time by [multiplier], split between [cores] cores
    # append results to arrays
    for x in range(1, runs):
        print("{}th run".format(x))

        multi, single = multiCoreTest.run_multicore_test(cores, x * multiplier, time)
        timesArray.append((multi, single))
        ratioArray.append((((multi / single) * 100) - 100) * -1)

    # Plot the results: First subplot shows comparison in run time, second subplot shows the reduction (Or increase) in time to run-
    # - on multiple cores
    plt.subplot(2, 1, 1)
    plt.title(str(cores) + " cores (blue) vs Single core (Orange)")
    plt.ylabel('Time to run (s)')
    plt.plot(timesArray)

    plt.subplot(2, 1, 2)
    plt.xlabel(xLabel)
    plt.ylabel("Reduction in time (%)")
    plt.plot(ratioArray)
    plt.show()
