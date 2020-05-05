#!/usr/bin/env bash

#python -m ${module_name} --imageSubdirs slitHeight1 --slitHeight=1
#python -m ${module_name} --imageSubdirs slitHeight2 --slitHeight=2
#python -m ${module_name} --imageSubdirs slitHeight3 --slitHeight=3

module_name="optical_simulation.run_simulation"

if ! [[ -d "./optical_simulation/image_output/timingTests" ]]; then
    echo "Running timing tests..."
    for (( n=0; n<=5; n+=1)); do
        python -m ${module_name} --imageSubdirs "timingTests" "timingTest${n}"
    done
else
    echo "Timing tests already ran. Delete the folder to run them again."
fi

if ! [[ -d "./optical_simulation/image_output/pointSource_x_obsPoints" ]]; then
    echo "Running tests varying point source number AND observation point number"

    # From 0 to 100 step 10 in point sources,
    for (( point_src=0; point_src<=100; point_src+=10)); do

        # From 0 to 1000 step 100 in observation points,
        for (( obs_point=0; obs_point<=1000; obs_point+=100 )); do

            # Run the simulation with two variables.
            python -m ${module_name} --imageSubdirs "pointSource_x_obsPoints" "pointSource${point_src}_x_obsPoint${obs_point}" \
                --numOfPointSources="${point_src}" --numObsPoints="${obs_point}"
        done
    done
else
    echo "Point source number + observation point number tests already ran. Delete the folder to run them again."
fi

# If we haven't ran the 'numOfPointSourcesRuns' simulations, then run a LARGE amount of those simulations and create that directory.
if ! [[ -d "./optical_simulation/image_output/numOfPointSourcesRuns" ]]; then
    echo "Running tests varying point source number..."
    for (( n=0; n<=1000; n+=100)); do
        python -m ${module_name} --imageSubdirs "numOfPointSourcesRuns" "numOfPointSources${n}" --numOfPointSources="${n}"
    done
else
    echo "Point source tests already ran. Delete the folder to run them again."
fi

# If we haven't ran the 'numObsPoints' simulations, then run a LARGE amount of those simulations and create that directory.
if ! [[ -d "./optical_simulation/image_output/numObsPointsRuns/" ]]; then
    for (( n=0; n<=1000; n+=50 )); do
        python -m ${module_name} --imageSubdirs "numObsPointsRuns" "numObsPoints${n}" --numObsPoints="${n}"
    done
else
    echo "Observation point tests already ran. Delete the folder to run them again."
fi

num=$(awk 'BEGIN{for(i=0; i<=10; i+=0.25)print i}')
if ! [[ -d "./optical_simulation/image_output/U_0/" ]]; then
    echo "Running tests varying U_0 number..."
    for n in $num; do
        python -m ${module_name} --imageSubdirs "U_0" "u_0${n}" --U_0="${n}"
    done
else
    echo "U_0 tests already ran. Delete the folder to run them again."
fi
