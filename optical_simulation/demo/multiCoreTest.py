import multiprocessing
import sys
import time
from multiprocessing import Queue

from typing import Callable, List


def run_multicore_test(cpu_cores: int = 8, number_calculations: int = 1000000, sleep_time: float = 5):
    """

    :param cpu_cores: Number of cores to use.
    :param number_calculations: Number of calculations per core to run.
    :param sleep_time: Time to sleep.
    :return: TODO
    """

    # Initialize arrays based on arguments provided
    q = Queue()  # used to save information generated within child process in separate core
    array1 = []
    array2 = []

    if cpu_cores > 2:
        array3 = []
    if cpu_cores > 3:
        array4 = []
    if cpu_cores > 4:
        array5 = []
    if cpu_cores > 5:
        array6 = []
    if cpu_cores > 6:
        array7 = []
    if cpu_cores > 7:
        array8 = []

    # Independent functions to fill arrays within separate cores with corresponding values

    multiVal = int(
        number_calculations / cpu_cores)  # Splits val into [numberCores] parts, which will need to merge later

    def generate_core_fn(core_number, work_array: List[List[int]], multiVal) -> Callable[[int], None]:
        """Generate a function for a core to run. TODO"""

        def core_n(_):
            for i in range(0, multiVal):
                work_array.append(i)
            pass

        return core_n

        pass

    def core1(n):
        for i in range(0, multiVal):
            array1.append(i)
        q.put(array1)

    def core2(n):
        for i in range(0, multiVal):
            array2.append(i + multiVal)
        q.put(array2)

    def core3(n):
        for i in range(0, multiVal):
            array3.append(i + (multiVal * 2))
        q.put(array3)

    def core4(n):
        for i in range(0, int(number_calculations / cpu_cores)):
            array4.append(i + (multiVal * 3))
        q.put(array4)

    def core5(n):
        for i in range(0, multiVal):
            array5.append(i + (multiVal * 4))
        q.put(array5)

    def core6(n):
        for i in range(0, multiVal):
            array6.append(i + (multiVal * 5))
        q.put(array6)

    def core7(n):
        for i in range(0, multiVal):
            array7.append(i + (multiVal * 6))
        q.put(array7)

    def core8(n):
        for i in range(0, multiVal):
            array8.append(i + (multiVal * 7))
        q.put(array8)

    # Separate processeses between [numberCores] cores

    for i in range(1):  # Scaled to create between 2 to 8 cores based on args provided
        t = multiprocessing.Process(target=core1, args=(i,))
        t2 = multiprocessing.Process(target=core2, args=(i,))
        if cpu_cores > 2:
            t3 = multiprocessing.Process(target=core3, args=(i,))
        if cpu_cores > 3:
            t4 = multiprocessing.Process(target=core4, args=(i,))
        if cpu_cores > 4:
            t5 = multiprocessing.Process(target=core5, args=(i,))
        if cpu_cores > 5:
            t6 = multiprocessing.Process(target=core6, args=(i,))
        if cpu_cores > 6:
            t7 = multiprocessing.Process(target=core7, args=(i,))
        if cpu_cores > 7:
            t8 = multiprocessing.Process(target=core8, args=(i,))

        # 'daemon = true' stops the parent process from having to wait for child processes to end before terminating.
        t.daemon = True
        t2.daemon = True
        if cpu_cores > 2:
            t3.daemon = True
        if cpu_cores > 3:
            t4.daemon = True
        if cpu_cores > 4:
            t5.daemon = True
        if cpu_cores > 5:
            t6.daemon = True
        if cpu_cores > 6:
            t7.daemon = True
        if cpu_cores > 7:
            t8.daemon = True

        # START TIMER, run processes
        start = time.time()

        t.start()  # start processes
        t2.start()
        if cpu_cores > 2:
            t3.start()
        if cpu_cores > 3:
            t4.start()
        if cpu_cores > 4:
            t5.start()
        if cpu_cores > 5:
            t6.start()
        if cpu_cores > 6:
            t7.start()
        if cpu_cores > 7:
            t8.start()

    mylist = []  # Used to retrieve values from queue sequentially

    print("Sleeping for {} seconds.".format(sleep_time))
    time.sleep(sleep_time)  # FIXME: This is a race condition!

    # Get objects in queue
    if q.empty():
        print("\nFail: Timer too short to allow child processes enough time to join parent\nProgram terminated\n")
        sys.exit(0)
    # while not q.empty():
    #   mylist.append(q.get())

    # Merge objects from queue into a single array
    mergedArray = []
    for n in range(0, cpu_cores):
        mergedArray = mergedArray + q.get()

    # TOTAL operating time of split loops
    # print("\nTotal time multi:")
    multiTime = (time.time() - start) - sleep_time
    # print(multiTime)

    # Compare with making a single array on one core
    array = []
    newstart = time.time()
    for j in range(0, number_calculations):
        array.append(j)
    time.sleep(sleep_time)
    # print("\nTotal time single: ")
    singleTime = (time.time() - newstart) - sleep_time
    # print(singleTime)

    # print("\nEfficiency ratio:\n",(multiTime/singleTime), "\n")
    return (multiTime, singleTime)
