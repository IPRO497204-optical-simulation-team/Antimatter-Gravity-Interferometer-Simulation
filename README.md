# X-Ray Optics Simulation

## Dependencies

### Hardware/OS

You will need a computer with an NVIDIA GPU that supports CUDA.

You will also need to use Linux. WSL may work. Virtualization will likely not work unless it offers GPU passthrough.

We used a system with the following configuration:

#### CPU

(2) Intel(R) Xeon(R) CPU E5-2630 v2 @ 2.60GHz

#### Memory

(5) Micron 4GB MT9JSF51272PZ-1G9E2

### GPU

(1) TITAN Xp

(1) Tesla K40c

### Software

Install [Conda](https://docs.conda.io/en/latest/) with Python 3.6 or greater.

Install the [NVIDIA CUDA Toolkit](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html).

Once installed, you should edit `/options.sh` to update the path of the CUDA binary folder. 

By default, we use `/usr/local/cuda-9.1/bin/` because we have multiple versions and want to use that specific version of NVIDIA CUDA.

## Editor/IDE

We all used PyCharm to edit this code, but command-line will also work perfectly fine.

## Running this code

Run `conda deactivate` to deactivate the `base` environment.

Run `conda env create -f environment.yml` in this directory to create a Conda environment with all dependencies specified in `environment.yml`.

The environment is called `agis`.

Run `conda activate agis` to use the virtual environment configured with Conda for this project.

Run `bash scripts/install_extra_conda_dependencies.sh` to install dependencies we cannot specify in the `environment.yml` file.

Then run `python -m optical_simulation.run_simulation` to run the slit simulation.

You can also run `python -m optical_simulation.demo.runMultiCoreTest` to run the multi-core test.

There is a shell script called `RunMultipleTests.sh` that will run multiple simulations with slightly different parameters.

There are also profiling scripts called `profile-*.sh`.

## Installing new packages

Add the package to `environment.yml`.

Run `conda env update -f environment.yml` in this directory to update Conda's environment from this file.
