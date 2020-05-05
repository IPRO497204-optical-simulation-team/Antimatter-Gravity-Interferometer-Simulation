# GPU memory in mb
GPU_MB = 12 * 1000

# Calculations from our CUDA GPU instrumentation
time_to_transfer_seconds = (386.861  # microseconds
                            / 1E6)  # to seconds
data_transferred_mb = 4.5  # data of mb

mb_per_second = data_transferred_mb / time_to_transfer_seconds
gb_per_second = mb_per_second / 1000

print("{:.2f} MB/s potential transfer speed from small CUDA test".format(mb_per_second))
print("{:.2f} GB/s potential transfer speed from small CUDA test".format(gb_per_second))
print("It would take {:.2f} seconds to fill the GPU's memory, according to our small CUDA test.".format(
    mb_per_second / GPU_MB))

################################################################
print()

# Calculated memory transfer using https://zsmith.co/bandwidth.php
# TODO, see bandwidth_output.txt and fill in numbers
mb_per_second_bandwidth = 8035

gb_per_second = mb_per_second_bandwidth / 1000

print("{:.2f} MB/s tested average speed".format(mb_per_second_bandwidth))
print("{:.2f} GB/s tested average transfer speed".format(gb_per_second))
print("It would take {:.2f} seconds to fill the GPU's memory, according to our memory speed test using the 'bandwidth' tool.".format(
    mb_per_second_bandwidth / GPU_MB))
