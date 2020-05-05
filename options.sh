#!/usr/bin/env bash

DESIRED_CONDA_ENV='agis'

# Path to the CUDA binary folder.
CUDA_DIR="/usr/local/cuda-9.1/bin/"

if ! [[ -d ${CUDA_DIR} ]]; then
    echo "'${CUDA_DIR}' does not exist. Falling back to '/usr/bin/'."
    CUDA_DIR="/usr/bin/"
fi

# nvprof binary location
NVPROF_BIN=${CUDA_DIR}/nvprof

if ! hash conda &> /dev/null; then
    echo "Conda does not seem to be a command. Is it installed?"
    exit 1
fi

# Ensure our conda environment is activated to avoid confusion
case ${CONDA_DEFAULT_ENV} in
${DESIRED_CONDA_ENV})
    echo "Using '$DESIRED_CONDA_ENV' as conda environment."
   ;;
*)
    echo "Current conda environment '$CONDA_DEFAULT_ENV' != '${DESIRED_CONDA_ENV}'! Did you forget to run 'conda activate ${DESIRED_CONDA_ENV}'?";
    exit 1
    ;;
esac
