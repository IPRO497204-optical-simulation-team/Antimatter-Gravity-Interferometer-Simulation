#!/usr/bin/env bash

source ./options.sh # Include file.

echo "Use these settings for nvvp:"
echo "Toolkit/Script: CUDA Toolkit 9.1 (/usr/local/cuda-9.1/bin/)
"

echo "The executable file is the Python 3 env that has all necessary dependencies, like numba, etc."
echo "Executable file: /home/`whoami`/miniconda3/envs/agis/bin/python3.7
"

echo "The working directory should be the place you have cloned the repo."
echo "Working directory: WORK_DIR/XRay-Optics-Simulation/
"

echo "Arguments: '-m optical_simulation.run_simulation'"

sleep 3

# Nvidia visual profiler
${CUDA_DIR}/nvvp "python -m optical_simulation.run_simulation" &
