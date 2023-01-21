# Nesting
# Compose returns a callable that can be nesting inside another Compose.
# Each compose can use threads and processes independently.
import sequential_functions as sf
import threading
import time
import os

def function_a(x):
    print(f"function_a({x}) ran in main thread")
    return x

def function_b(x):
    time.sleep(1) # sleep 1 second
    print(f"function_b({x}) ran in thread {threading.current_thread().name}")
    return x

def function_c(x):
    time.sleep(1) # sleep 1 second
    print(f"function_c({x}) ran in process {os.getpid()}")
    return x

sequence = sf.Compose(
    function_a,

    sf.Compose(
        function_b,
        num_threads=3,
    ),

    sf.Compose(
        function_c,
        num_processes=3,
    ),
)
list(sequence(range(3)))