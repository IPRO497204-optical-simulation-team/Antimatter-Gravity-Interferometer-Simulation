#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 17:21:19 2017

"""
import argparse

from guppy import hpy
from memory_profiler import profile
import os  # Used in file saving function
from time import strftime
from time import time
from typing import Tuple, List

import matplotlib.pyplot as plt
import numpy as np
from numba import cuda

from optical_simulation.cudaKernels import intensityCalculations
from optical_simulation.gratingLib.Grating import Grating
from optical_simulation.gratingLib.InitialSource import InitialSource

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput


def get_args_from_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    """think the use of screen-distance and second_grating_distance is redundant. if both are identical, should be 4.5cm instead of 5e7"""

    """should be 4.5e7 but is 5e7 for sake of consistency when comparing to previous tests"""
    parser.add_argument('--screen_distance',
                        default=5e7,
                        type=int,
                        help='Distance between the two gratings')

    parser.add_argument('--screen_length',
                        default=1e7,
                        type=int,
                        help='Not sure what this is exactly. Contact group or review code.')

    """should be 4.5e7 but is 5e7 for sake of consistency when comparing to previous tests"""
    parser.add_argument('--second_grating_distance',
                        default=5e7,
                        type=int,
                        help='Not sure what this is exactly. Contact group or review code.')

    parser.add_argument('--wavelength',
                        default=.56,
                        type=float,
                        help='The wavelength of the wave in nanometers.')

    parser.add_argument('--U_0',
                        default=1,
                        type=float,
                        help='The initial amplitude of the point source')

    """slitHeight should be used as 15000 nanometers but too big"""
    parser.add_argument('--slitHeight',
                        default=5,
                        type=int,
                        help='Height of each slit in each grating (Used for 2D implementation)')

    """number of slits doesnt correlate with 1cm/(slitheight*slitlength) - use small numbers to just quickly run simulation for performance"""
    parser.add_argument('--numOfSlits',
                        default=200,
                        type=int,
                        help='Number of slits in each grating')

    parser.add_argument('--numOfPointSources',
                        default=100,
                        type=int,
                        help='Number of point sources in each slit')

    parser.add_argument('--numObsPoints',
                        default=1000,
                        type=int,
                        help='Number of observing points on the screen')

    parser.add_argument('--slitLength',
                        default=50,
                        type=int,
                        help='Length of the slits')

    parser.add_argument('--spacingType',
                        default='uniform',
                        type=str,
                        help='Geometry of the slits, Can be "uniform", "random", ...')

    parser.add_argument('--runNum',
                        default=1,
                        type=int,
                        help='Used to dynamically name files. Change every time you run a simulation. Otherwise it will write')

    parser.add_argument('--imageSubdirs',
                        default=['default_subdirectory'],
                        nargs='+',
                        help='Used to save images to a different subfolder. Useful for running multiple batches and examining images later.')

    parser.add_argument('--transparentImages',
                        default=False,
                        type=bool,
                        help='Should output images be transparent?')

    parser.add_argument('--showImages',
                        default=False,
                        type=bool,
                        help='Should images be shown?')

    parser.add_argument('--callGraph',
                        default=False,
                        type=bool,
                        help='Should there be a function call graph image saved?')

    parser.add_argument('--useRealisticParameters',
                        default=False,
                        type=bool,
                        help='Use realistic simulation parameters. This should take a long time.')

    # TODO: Fill in the rest of the arguments

    return parser.parse_args()


args = get_args_from_command_line()
screen_distance = args.screen_distance  # in nanometers
screen_length = args.screen_length  # in nanometers
second_grating_distance = args.second_grating_distance  # in nanometers
wavelength = args.wavelength  # nm is the de Broglie wavelength of muonium at 6300 meters/s
numOfSlits = args.numOfSlits  # number of slits in each grating
numOfPointSources = args.numOfPointSources  # number of point sources in each slit
numObsPoints = args.numObsPoints  # number of observing points on the screen
slitLength = args.slitLength  # nm
slitHeight = args.slitHeight  # Height of each slit in each grating (Used for 2D implementation)
runNum = args.runNum  # Used to dynamically name files. Change every time you run a simulation. Otherwise it will write
spacingType = args.spacingType
U_0 = args.U_0
imageSubdirs = args.imageSubdirs
transparency = args.transparentImages
shouldShowImages = args.showImages
shouldUseRealisticParameters = args.useRealisticParameters

# Should we use realistic presets?
if shouldUseRealisticParameters:
    numOfSlits = 66399336
    # Add math from notebook for explanation
    slitHeight = 15000
    # Add math from notebook for explanation
    second_grating_distance = 4.5e7
    screen_distance = 4.5e7

# Path to save images to.
current_path = os.path.abspath(os.path.dirname(__file__))
image_output_path = os.path.join(current_path, 'image_output', *imageSubdirs)

image_first_grating_path = os.path.join(image_output_path, '{}-first-grating.png'.format(imageSubdirs[-1]))
image_second_grating_path = os.path.join(image_output_path, '{}-second-grating.png'.format(imageSubdirs[-1]))
image_normalized_intensity_path = os.path.join(image_output_path,
                                               '{}-normalized-intensity.png'.format(imageSubdirs[-1]))
image_algorithm_runtime_path = os.path.join(image_output_path, '{}-algorithm-runtime.png'.format(imageSubdirs[-1]))
image_call_graph_path = os.path.join(image_output_path, '{}-call-graph.png'.format(imageSubdirs[-1]))


# Uncomment for line-by-line memory profiling info.
# @profile
def main():
    """The main function. This runs the simulation."""

    wavenumber = 2 * np.pi / wavelength
    newSimulation = False

    print(imageSubdirs)

    if not os.path.exists(image_output_path):
        os.makedirs(image_output_path)

    # Observing screen size
    # center of screen will automatically be at 0.5e7 nm
    # Change this based on size of gratings
    screenStart = 0e7
    screenEnd = 1e7

    timings = []
    initial_time = int(round(time() * 1000))

    def add_time(function_name):
        x = int(round(time() * 1000))
        timings.append([function_name, x])

    # create array of positions that represent an observing screen

    print("Starting observation points")
    observingPositions = np.linspace(screenStart, screenEnd, numObsPoints)
    add_time("observingPositions")
    print("Observation points made")

    # Build gratings and fill with point sources

    print("Starting first grating")

    firstGrating = Grating(x=0, length=screen_length, numberOfSlits=numOfSlits, slitWidth=slitLength,
                           slitHeight=slitHeight, sourcesPerSlit=numOfPointSources, sourceSpacing=spacingType)
    add_time("firstGrating")
    print("First grating done")

    # Build second grating and fill with point sources

    print("Starting second grating")
    secondGrating = Grating(x=second_grating_distance, length=screen_length, numberOfSlits=numOfSlits,
                            slitWidth=slitLength,
                            slitHeight=slitHeight, sourcesPerSlit=numOfPointSources, sourceSpacing=spacingType)
    add_time("secondGrating")
    print("Second grating done")

    # Define initial source
    # Options are 'spherical' and 'plane'
    # Initial source position is -(distance from first grating in nm)
    initSource = InitialSource(xPosition=-1e7, yPosition=screen_length / 2, waveType='plane', initialAmplitude=U_0)
    add_time("initSource")
    # generate source amplitudes and phases based on the initial source and the first gratings point source positions
    sourceAmps, sourcePhase = initSource.propogate(firstGrating.x, firstGrating.pointSourcePositions, wavenumber,
                                                   normalize=True)
    add_time("initSource.propogate")
    # add these amplitudes to the first grating's point sources
    firstGrating.addAmplitudes(sourceAmps, sourcePhase)
    add_time("firstGrating.addAmplitudes")
    # calculate information from firstGrating propagating to secondGrating
    intensities, amplitudes, phases = intensityCalculations(screen_distance, wavenumber,
                                                            firstGrating.pointSourcePositions,
                                                            secondGrating.pointSourcePositions,
                                                            firstGrating.pointSourceAmplitudes,
                                                            firstGrating.pointSourcePhases)
    add_time("intensityCalculations1")
    # add necessary results to secondGrating's point sources
    # print('Populating grating 2\n')
    secondGrating.addAmplitudes(amplitudes, phases)
    add_time("secondGrating.addAmplitudes")
    # calculate information from secondGrating propagation to observingPositions
    # print('Grating 2 to Screen:\n')
    intensities2, amplitudes2, phases2 = intensityCalculations(screen_distance, wavenumber,
                                                               secondGrating.pointSourcePositions, observingPositions,
                                                               secondGrating.pointSourceAmplitudes,
                                                               secondGrating.pointSourcePhases)
    add_time("intensityCalculations2")

    if newSimulation:
        with open("onSecondGratingResults_%s_run00%s.txt" % (initSource.waveType, runNum), 'w') as f:
            f.write("#source wave type: %s, time taken: %s\n" % (initSource.waveType, tf1 - t01))
            f.write("#Intensity\tAmplitudes\t\tPhase\t\t\t\tPosition\n")
            for i, a, p, o in zip(intensities, amplitudes, phases, secondGrating.pointSourcePositions):
                f.write("%s\t%s\t%s\t%s\n" % (i, a, p, o))

        with open("onScreenResults_%s_run00%s.txt" % (initSource.waveType, runNum), 'w') as f:
            f.write("#source wave type: %s, time taken: %s" % (initSource.waveType, tf2 - t02))
            f.write("#Intensity\tAmplitudes\t\tPhase\t\t\t\tPosition\n")
            for i, a, p, o in zip(intensities2, amplitudes2, phases2, observingPositions):
                f.write("%s\t%s\t%s\t%s\n" % (i, a, p, o))

    cuda.close()

    # quickly plot data to see if results are reasonable
    plt.figure(figsize=(15, 8))
    plt.plot(firstGrating.pointSourcePositions, firstGrating.pointSourceAmplitudes, '.r')
    plt.xlabel('Position on First Grating (nm)', fontsize=25)
    plt.ylabel('Amplitude', fontsize=25)
    plt.title('Incident on First Grating', fontsize=30)
    plt.savefig(image_first_grating_path, transparent=transparency)
    # plt.show()

    plt.figure(figsize=(15, 8))
    plt.plot(secondGrating.pointSourcePositions, intensities, '.r')
    plt.xlabel('Position on Second Grating (nm)', fontsize=25)
    plt.ylabel('Normalized Intensity (lux)', fontsize=25)
    plt.title('Incident on Second Grating', fontsize=30)
    plt.savefig(image_second_grating_path, transparent=transparency)
    # plt.show()

    maxIntensities2 = max(intensities2)
    intensities2 = [i / maxIntensities2 for i in intensities2]

    obsPositionsMicrons = [i / 1000 for i in observingPositions]

    plt.figure(figsize=(15, 8))
    plt.plot(obsPositionsMicrons, intensities2, 'r')
    plt.xlabel('Position on Observing Screen (nm)', fontsize=25)
    plt.ylabel('Normalized Intensity (lux)', fontsize=25)
    plt.title('Uniform Grating', fontsize=30)
    plt.savefig(image_normalized_intensity_path, transparent=transparency)
    # plt.show()

    last_time = initial_time
    for i in range(len(timings)):
        temp = timings[i][1]
        timings[i][1] -= last_time
        last_time = temp

    print(str(timings))

    fig, axs = plt.subplots(ncols=2, figsize=(8, 4))
    #   axs[0].axis('tight')
    axs[1].axis('off')
    x = list(range(len(timings)))
    function_names = list(map(lambda x: x[0], timings))
    runtimes = list(map(lambda x: x[1], timings))
    function_numbers = list(range(len(timings)))
    cell_text = list(map(lambda i: [function_numbers[i], timings[i][0], timings[i][1]], range(len(timings))))

    table = axs[1].table(cellText=cell_text, colLabels=['#', 'Function', 'Runtime'],
                         loc='center').auto_set_column_width([0, 1, 2])
    bar = axs[0].bar(x, runtimes)
    plt.xticks(x, x)
    plt.xlabel('Function #', fontsize=20)
    plt.ylabel('Runtime (ms)', fontsize=20)
    plt.savefig(image_algorithm_runtime_path, transparent=transparency)

    if shouldShowImages:
        plt.show()

    print("Image files:")
    print(image_first_grating_path)
    print(image_second_grating_path)
    print(image_normalized_intensity_path)
    print(image_algorithm_runtime_path)

    print("Guppy3 mem usage info:")
    print(hpy().heap())


if __name__ == '__main__':

    if args.callGraph:
        graphviz = GraphvizOutput()
        graphviz.output_file = image_call_graph_path
        with PyCallGraph(output=graphviz):
            main()
    else:
        main()
