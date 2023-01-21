# Multi Processing
# It's trivial to distribute work to multiple processes by providing the num_processes argument.
# Work is still completed in order.
# Use multiprocessing when computation is the bottle neck.
import sequential_functions as sf
import time
import os

def slow_task(x):
    time.sleep(1) # sleep 1 second
    return x

def record_process_id(x):
    return f"Task {x} completed by process {os.getpid()}"


sequence = sf.Compose(
    slow_task,
    record_process_id,
    num_processes=5, # Simply choose the number of processes
)

start_time = time.perf_counter()

for x in sequence(range(5)):
    print(x)

end_time = time.perf_counter()

print(f"total time: {end_time-start_time}")
