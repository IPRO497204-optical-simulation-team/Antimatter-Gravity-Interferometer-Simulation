#!/usr/bin/env bash

source ./options.sh # Include file.

# Nvidia command-line profiler
${CUDA_DIR}/nvprof python3 -m optical_simulation.run_simulation
