#!/usr/bin/env bash

echo "This file runs a series of tests that vary the amount of source points per slit to see how runtime and memory \
usage will vary when increasing the number of source points."

OUT_DIR="out/gpu-memory-tests/" # Directory to save the text files containing each process' stdout to.
OUT_IMAGES="gpu-memory-tests-imagefiles" # Base directory for saving the images to.
OUT_CSV="out/gpu-memory-test.csv" # Place to save the CSV file to.

# Don't clobber their CSV if they don't know...
if [[ -f ${OUT_CSV} ]]; then
    echo "The file at ${OUT_CSV} will be destroyed after all tests run. You have 10 seconds to cancel this (CTRL-C)."
    sleep 10s
fi

source ./options.sh # Include file.
mkdir -p ${OUT_DIR} # Make directory unconditionally.

# List of point sources to try
POINTSOURCES=(5 25 50 75 100 200 300 400 600 800 1200 1600)

SLITHEIGHT=50 #15000 is realistic.

NUMOFSLITS=200

OBSPOINTS=150

## DEBUG PARAMS: These are fast but not realistic!
#POINTSOURCES=(5 10 20)
#POINTSOURCES=(5 10 20 30 40 50 60 70 80 90 100 200 300 400)
#SLITHEIGHT=5
#OBSPOINTS=30


# Vary point sources
for (( i = 0; i < ${#POINTSOURCES[@]}; ++i )); do

    # One of n point sources
    numpointsource=${POINTSOURCES[i]}

    # Place to redirect stdout of the nvprof command
    OUT_FILENAME="${OUT_DIR}/${numpointsource}-point-source.txt"
    OUT_PROFILE_NAME="${OUT_DIR}/${numpointsource}-point-source.prof"

    # If stdout file from nvprof command does not exist,
    if [[ ! -f ${OUT_DIR}/${numpointsource}-point-source.txt ]]; then
        echo "Have not run GPU memory test for ${numpointsource} point sources yet. Running..."

        # Run the profiling command.
        ${NVPROF_BIN} --print-gpu-trace --export-profile ${OUT_PROFILE_NAME} \
            python -m optical_simulation.run_simulation \
                --imageSubdirs "${OUT_IMAGES}" "${numpointsource}-point-sources" \
                --slitHeight ${SLITHEIGHT} \
                --numOfPointSources ${numpointsource} \
                --numObsPoints ${OBSPOINTS} \
                --numOfSlits ${NUMOFSLITS} > ${OUT_FILENAME} 2>&1
    else
        echo "Already run GPU memory test for ${numpointsource} point sources. Skipping. Delete file at ${OUT_FILENAME} to run again."
    fi

done

# From results, generate CSV file
echo "Generating CSV file at ${OUT_CSV}."

# This will destroy your CSV file.
echo "sourcePoints,\
total-time (ms),\
mem-to-gpu-time (ms),\
kernel-time (ms),\
slit-height,\
num-of-slits,\
obs-points,\
bytes-ram-used-at-end,\
bytes-transferred-total-gpu-to-cpu (DtoH),\
bytes-transferred-total-cpu-to-to-gpu (HtoD)" > ${OUT_CSV}

# TODO: We are still encoding the source points in the filename itself.
# TODO: This is poor form and parameters that vary should be stored in a JSON file or maybe an SQLITE database.
# TODO: Alternatively, Python should be used to manage and run experiments on parameters instead of Bash because
# TODO:     it is easier to model data with it. A re-write could make this shell script easier to use.
for f in ${OUT_DIR}/*-point-source.txt; do

    aline=""

    # The source points from the filename.
    # TODO: This is poor form to encode the source points here.
    # TODO: Ideally, we should be able to run over a matrix of varying parameters and see how they all affect runtime.
    # TODO: This information should be encoded elsewhere.
    aline+=$(echo "${f}" | tr -dc '0-9')
    aline+=","

    # total time in ms that it took to run the sim
    aline+=$(cat ${f} | grep "total time:" | head -1 | tr -dc '0-9.')
    aline+=","

    # Time in ms to transfer data from memory to GPU
    aline+=$(cat ${f} | grep "mem-to-gpu time:" | head -1 | tr -dc '0-9.')
    aline+=","

    # Time in ms to run gpu sims
    aline+=$(cat ${f} | grep "kernel time:" | head -1 | tr -dc '0-9.')
    aline+=","

    # Height of slit. Currently static.
    aline+=${SLITHEIGHT}
    aline+=","

    # Number of slits. Currently static.
    aline+=${NUMOFSLITS}
    aline+=","

    # Observation points. Currently static.
    aline+=${OBSPOINTS}
    aline+=","

    # RAM usage at the end of the simulation.
    # get line with 'total size', get part after equals sign, strip non-numeric chars.
    aline+=$(cat ${f} | grep " Total size =" | tr '=' "\n" | tail -1 | sed 's/[^0-9]*//g')
    aline+=","

    # GPU->CPU memory transfer total in bytes
    # Get the eighth field and sum all bytes in that.
    aline+=$(cat ${f} | grep "DtoH" | awk '{print $8}' | python3 scripts/byte_adder.py)
    aline+=","

    # CPU->GPU memory transfer total in bytes
    # Get the eighth field and sum all bytes in that.
    aline+=$(cat ${f} | grep "HtoD" | awk '{print $8}' | python3 scripts/byte_adder.py)
#    aline+=","

    echo ${aline} >> ${OUT_CSV}

done

cat ${OUT_CSV} # Echo the CSV to the user.
