## Toy Example
This example is too simple for a real use case but it highlights the syntax.
```python
import sequential_functions as sf

def square(x):
    return x*x

def plus_one(x):
    return x + 1

# Build a generator chain using Compose
sequence = sf.Compose(
    square,
    plus_one,
)

# Use list to pull items through the generator chain
outputs = list(sequence(range(5)))

print(outputs)
```
Output
```shell
[1, 2, 5, 10, 17]
```
## Under the Hood
Compose uses generator chaining to run items through each of the functions.
Both of these methods produce the same output
```python
import sequential_functions as sf

def square(x):
    return x*x

def plus_one(x):
    return x + 1

# Method 1
sequence = sf.Compose(
    square,
    plus_one,
)
outputs = list(sequence(range(5)))
print(outputs,"Method 1 - Composed Sequence")

# Method 2
generator_chain = range(5)
generator_chain = (square(x) for x in generator_chain)
generator_chain = (plus_one(x) for x in generator_chain)
output = list(generator_chain)
print(outputs,"Method 1 - Generator Chain")
```
Output
```shell
[1, 2, 5, 10, 17] Method 1 - Composed Sequence
[1, 2, 5, 10, 17] Method 1 - Generator Chain
```
## Best Practice
It's best practice to pass a dict in and out of each function.
Each function can modify the dict as they complete their computation.
This design seems the most readable and extensible.
```python
import sequential_functions as sf

def create_task_dict(path):
    print(f"Tasking: {path}")
    task = { "image_path": path}
    return task

def load_image(task):
    print(f"Loading: {task['image_path']}")
    task["image"] = "e.g. numpy array"
    return task

def preprocess_image(task):
    print(f"Preprocessing: {task['image_path']}")
    task["tensor"] = "e.g. torch tensor"
    return task

def detect_objects(task):
    print(f"Detecting: {task['image_path']}")
    task["detections"] = ["box 1", "box 2"]
    return task


sequence = sf.Compose(
    create_task_dict,
    load_image,
    preprocess_image,
    detect_objects,
)

paths = ["cat.jpg","dog.jpg"]
for task in sequence(paths):
    print(f"Results: {task['image_path']}")
    print(task["detections"])
    print()



```
Output
```shell
Tasking: cat.jpg
Loading: cat.jpg
Preprocessing: cat.jpg
Detecting: cat.jpg
Results: cat.jpg
['box 1', 'box 2']

Tasking: dog.jpg
Loading: dog.jpg
Preprocessing: dog.jpg
Detecting: dog.jpg
Results: dog.jpg
['box 1', 'box 2']

```
## Multi Processing
It's trivial to distribute work to multiple processes by providing the num_processes argument.
Work is still completed in order.
Use multiprocessing when computation is the bottle neck.
```python
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

```
Output
```shell
Task 0 completed by process 14303
Task 1 completed by process 14304
Task 2 completed by process 14305
Task 3 completed by process 14307
Task 4 completed by process 14306
total time: 1.0114389980444685
```
## Multi Threading
It's trivial to distribute work to multiple threads by providing the num_threads argument.
Work is still completed in order.
Use threading when IO is the bottle neck. e.g loading urls.
```python
import sequential_functions as sf
import time
import threading

def slow_task(x):
    time.sleep(1) # sleep 1 second
    return x

def record_thread_name(x):
    name = threading.current_thread().name
    return f"Task {x} completed by thread {name}"


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

```
Output
```shell
Task 0 completed by thread ThreadPoolExecutor-0_0
Task 1 completed by thread ThreadPoolExecutor-0_1
Task 2 completed by thread ThreadPoolExecutor-0_2
Task 3 completed by thread ThreadPoolExecutor-0_3
Task 4 completed by thread ThreadPoolExecutor-0_4
total time: 1.002888128045015
```
