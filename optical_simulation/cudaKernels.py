# !/usr/bin/env python2
# -*- coding: utf-8 -*-
""" cudaKernels.py
  This module is used to house all of the CUDA Kernels for the antimatter gravity interferometer simulation code. 
  Attributes:
    <currently no module level variables>
  TODO:
    * rename calcIntensitiesCUDA_new
    * make new function to add some abstraction
  Author:
    Alec Buchanan - 03/2018
"""

from timeit import default_timer as timer

import cmath
import math

import numpy as np
from numba import cuda


# This function gets called for every observation point
@cuda.jit
def intensityKernel(GratingSeparation, WaveNumber, sourcePoints, obsPoints, sourceAmp, sourcePhase, out_phase, out_amp,
                    out_intense):
    """calculates intensity, amplitude and phases between sources points and observation points
       Since this a CUDA kernel. This function gets called for each observation point. It should be changed to be called for each calculation
    Args:
      GratingSeparation (float):Constant passed in and used as distance (on the x-plane) between source and observation points
      WaveNumber (float):	Constant defined in global variables. 
      sourcePoints (f4[:]):	Position of source points as an array of float32
      obsPoints (f4[:]):	Position of observation points as an array of float32
      sourceAmp (f4[:]):	Amplitudes from each source point as an array of float32
      sourcePhase (c8[:]):	Phase of each source point as an array of float32
      out_phase (c8[:]):	Reference to observation point phase array used for output as an array of complex128
      out_amp (f4[:]):		Reference to observation point amplitude array used for output as an array of float32
      out_intense (f4[:]):	Reference to observation point intensity array used for output as an array of float32
    Returns:
      Nothing, CUDA kernels can not return anything
    ChangeLog:
      
 
    TODO:
      * change function to be called for each calculation instead of each observation point.  
    Author:
      Alec Buchanan - 3/2018
    """
    # Basic CUDA code to determine which thread we are in
    #tx = cuda.threadIdx.x  # Thread id in a 1D block = particle index
    #ty = cuda.blockIdx.x  # Block id in a 1D grid = event index
    #bw = cuda.blockDim.x  # Block width, i.e. number of threads per block = particle number
    pos = cuda.grid(1)  # computed flattened index inside the array

    # initialize variables 
    phaseSum = 0
    ampSum = 0

    # Iterates over every source point for this observation point
    # TODO: Optimize code even more so we can increase number of threads and remove for loop
    for point in range(0, len(sourcePoints)):
        # Find the distance between source and observation point
        # dist = sqrt(x^2 + (source point - observation point)^2)

        dist = math.sqrt(GratingSeparation ** 2 + (obsPoints[pos] - sourcePoints[point]) ** 2)
        # TODO: Is this calculation better to do on CPU or GPU?

        # Determine the phase between points
        phase = cmath.exp(1j * WaveNumber * dist)
        # find Amplitudes
        U = sourceAmp[point] * (phase.real + 1j * phase.imag) * (
                sourcePhase[point].real + 1j * sourcePhase[point].imag) / dist
        # sum the totals
        phaseSum = phaseSum + phase
        ampSum = ampSum + U
    # Find Intensity
    intensitySum = (ampSum.real ** 2 + ampSum.imag ** 2)
    # take the square root of intensity
    preservedAmp = math.sqrt(intensitySum)

    # output results
    out_phase[pos] = phaseSum
    out_amp[pos] = preservedAmp
    out_intense[pos] = intensitySum


def intensityCalculations(GratingSeparation, WaveNumber, sourcePoints, obsPoints, sourceAmp, sourcePhase):
    """This function is used as an abstraction layer for the CUDA kernel. This function does the type casting and is able to return values.
      
    Args:
      GratingSeparation (float):Constant passed in and used as distance (on the x-plane) between source and observation points
      WaveNumber (float):       Constant defined in global variables. I think it has to do with wave length; not sure why its named wavenumber
      sourcePoints (f4[:]):     Position of source points as an array of float32
      obsPoints (f4[:]):        Position of observation points as an array of float32
      sourceAmp (f4[:]):        Amplitudes from each source point as an array of float32
      sourcePhase (c8[:]):      Phase of each source point as an array of complex128
    Returns:
      return intensities, amplituteds, phases;
        intensities (f4[:]):	Array of intensities for each observation point as an array of float32
        amplitudes  (f4[:]):	Array of amplitudes  for each observation point as an array of float32
        phases	    (c8[:]):	Array of phases      for each observation point as an array of complex128
    Changelog:
    TODO:
    Author:
      Alec Buchanan - 3/2018
    """
    # Specify the number of CUDA threads
    arraySize = len(obsPoints)
    threadsperblock = 32
    blockspergrid = (arraySize + (threadsperblock - 1)) // threadsperblock

    # initialize output variables
    out_i = [0.0] * arraySize  # intensity
    out_a = [0.0] * arraySize  # amplitude
    out_p = [0.0] * arraySize  # phase

    # Cast datatypes so the kernel does not complain
    GratingSeparation = float(GratingSeparation)
    WaveNumber = float(WaveNumber)
    sourcePoints = np.array(sourcePoints, dtype='f4')  # 32-bit float array, 4 bytes
    obsPoints = np.array(obsPoints, dtype='f4')  # 32-bit float array, 4 bytes
    sourcePhase = np.array(sourcePhase, dtype='c8')  # 64-bit complex array, 8 bytes
    out_p = np.array(out_p, dtype='c8')  # 64-bit complex array, 8 bytes
    out_a = np.array(out_a, dtype='f4')  # 32-bit float array, 4 bytes
    out_i = np.array(out_i, dtype='f4')  # 32-bit float array, 4 bytes


    evt_total_begin = cuda.event()
    evt_total_end = cuda.event()

    evt_mem_begin = cuda.event()
    evt_mem_end = cuda.event()

    evt_mem2_begin = cuda.event()
    evt_mem2_end = cuda.event()

    evt_kernel_begin = cuda.event()
    evt_kernel_end = cuda.event()

    evt_total_begin.record()
    evt_mem_begin.record()

    d_sourcePoints = cuda.to_device(sourcePoints)
    d_obsPoints = cuda.to_device(obsPoints)
    d_sourceAmp = cuda.to_device(sourceAmp)
    d_sourcePhase = cuda.to_device(sourcePhase)
    d_out_i = cuda.to_device(out_i)
    d_out_a = cuda.to_device(out_a)
    d_out_p = cuda.to_device(out_p)

    evt_mem_end.record()
    evt_mem_end.synchronize()

    evt_kernel_begin.record()
    # call CUDA kernel
    intensityKernel[blockspergrid, threadsperblock](GratingSeparation, WaveNumber, d_sourcePoints, d_obsPoints, d_sourceAmp,
                                                    d_sourcePhase, d_out_p, d_out_a, d_out_i)

    evt_kernel_end.record()
    evt_kernel_end.synchronize()
    
    evt_mem2_begin.record()

    out_i = d_out_i.copy_to_host()
    out_a= d_out_a.copy_to_host()
    out_p = d_out_p.copy_to_host()

    evt_mem2_end.record()
    evt_mem2_end.synchronize()

    evt_total_end.record()
    evt_total_end.synchronize()

    print('total time: %fms' % evt_total_begin.elapsed_time(evt_total_end))
    print('mem-to-gpu time: %fms' % evt_mem_begin.elapsed_time(evt_mem_end))
    print('kernel time: %fms' % evt_kernel_begin.elapsed_time(evt_kernel_end))
    print('mem-from-gpu time: %fms' % evt_mem2_begin.elapsed_time(evt_mem2_end))
    # Remove Imaginary parts
    out_i = np.array(out_i, dtype='f4')
    out_a = np.array(out_a, dtype='f4')

    return out_i, out_a, out_p
