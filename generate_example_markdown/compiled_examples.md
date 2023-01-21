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
Task 0 completed by process 3973
Task 1 completed by process 3979
Task 2 completed by process 3999
Task 3 completed by process 4000
Task 4 completed by process 4001
total time: 1.0114223799901083
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
total time: 1.0030579089652747
```
## Nesting
Compose returns a callable that can be nesting inside another Compose.
Each compose can use threads and processes independently.
```python
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
```
Output
```shell
function_a(0) ran in main thread
function_a(1) ran in main thread
function_a(2) ran in main thread
function_b(0) ran in thread ThreadPoolExecutor-0_0
function_b(1) ran in thread ThreadPoolExecutor-0_1
function_b(2) ran in thread ThreadPoolExecutor-0_2
function_c(0) ran in process 4045
function_c(1) ran in process 4046
function_c(2) ran in process 4047
```
## Callables
Functions can be any type of callable.
Use closures and callable objects to change the behaviour of functions
```python


import sequential_functions as sf


def to_string(x):
    return str(x)

def append_string(s):
    # create new function on the fly
    def closure(x):
        return x + s
    # return this new function
    return closure

class EncloseString():
    # Callable class
    def __init__(self,s):
        self.s = s
    def __call__(self,x):
        return self.s + x + self.s

sequence = sf.Compose(
    to_string,
    append_string(" Hello"),
    append_string(" World!"),
    EncloseString("**"),
    EncloseString(".."),
)

for x in sequence(range(5)):
    print(x)
```
Output
```shell
..**0 Hello World!**..
..**1 Hello World!**..
..**2 Hello World!**..
..**3 Hello World!**..
..**4 Hello World!**..
```
