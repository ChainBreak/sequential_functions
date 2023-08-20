# Multi Threading
# It's trivial to distribute work to multiple threads by providing the num_threads argument.
# Order is not preserved with multithreading.
# Use threading when IO is the bottle neck. e.g loading urls.
import sequential_functions as sf
import time
import threading

def main():
    sequence = sf.Compose(
        slow_task,
        record_thread_name,
        num_threads=5, # Simply choose the number of thread
    )

    start_time = time.perf_counter()

    for x in sequence(range(5)):
        print(x)

    end_time = time.perf_counter()

    print(f"total time: {end_time-start_time}")

def slow_task(x):
    time.sleep(1) # sleep 1 second
    return x

def record_thread_name(x):
    name = threading.current_thread().name
    return f"Task {x} completed by thread {name}"

if __name__ == "__main__":
    main()