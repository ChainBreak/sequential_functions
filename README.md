# Sequential Functions
Compose functions into a sequence that are called sequentially.  
This project is designed for fast readable code.  
Break your problem into small functional steps and let sequential functions run them sequentially.   
Want to go faster? Simply increase the number of threads or processes.

# Examples

## Toy Example
Toy example that highlights the syntax.
```python
import sequential_functions as sf

def main():
    # Compose an easy to read list of steps
    sequence = sf.Compose(
        square,
        plus_one,
    )

    # Use list to pull items through the sequence
    outputs = list(sequence(range(5)))

    print(outputs)

def square(x):
    return x*x

def plus_one(x):
    return x + 1

if __name__ == "__main__":
    main()
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

def main():
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
    print(outputs,"Method 2 - Generator Chain")

def square(x):
    return x*x

def plus_one(x):
    return x + 1

if __name__ == "__main__":
    main()
```
Output
```shell
[1, 2, 5, 10, 17] Method 1 - Composed Sequence
[1, 2, 5, 10, 17] Method 2 - Generator Chain
```
## Best Practice
It's best practice to pass a dict in and out of each function.
Each function can modify the dict as they complete their computation.
This design seems the most readable and extensible.
```python
import sequential_functions as sf

def main():
    sequence = sf.Compose(
        create_item_dict,
        load_image,
        preprocess_image,
        detect_objects,
    )

    paths = ["cat.jpg","dog.jpg"]
    for item in sequence(paths):
        print(f"Results: {item['image_path']}")
        print(item["detections"])
        print()

def create_item_dict(path):
    print(f"Item Dict: {path}")
    item = { "image_path": path}
    return item

def load_image(item):
    print(f"Loading: {item['image_path']}")
    item["image"] = "e.g. numpy array"
    return item

def preprocess_image(item):
    print(f"Preprocessing: {item['image_path']}")
    item["tensor"] = "e.g. torch tensor"
    return item

def detect_objects(item):
    print(f"Detecting: {item['image_path']}")
    item["detections"] = ["box 1", "box 2"]
    return item

if __name__ == "__main__":
    main()
```
Output
```shell
Item Dict: cat.jpg
Loading: cat.jpg
Preprocessing: cat.jpg
Detecting: cat.jpg
Results: cat.jpg
['box 1', 'box 2']

Item Dict: dog.jpg
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

def main():
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

def slow_task(x):
    time.sleep(1) # sleep 1 second
    return x

def record_process_id(x):
    return f"Task {x} completed by process {os.getpid()}"

if __name__ == "__main__":
    main()
```
Output
```shell
Task 0 completed by process 19228
Task 1 completed by process 19229
Task 2 completed by process 19230
Task 3 completed by process 19231
Task 4 completed by process 19232
total time: 1.0112877849987854
```
## Multi Threading
It's trivial to distribute work to multiple threads by providing the num_threads argument.
Work is still completed in order.
Use threading when IO is the bottle neck. e.g loading urls.
```python
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
```
Output
```shell
Task 0 completed by thread ThreadPoolExecutor-0_0
Task 1 completed by thread ThreadPoolExecutor-0_1
Task 2 completed by thread ThreadPoolExecutor-0_2
Task 3 completed by thread ThreadPoolExecutor-0_3
Task 4 completed by thread ThreadPoolExecutor-0_4
total time: 1.0028790479991585
```
## Nesting
Compose returns a callable that can be nesting inside another Compose.
Each compose can use threads and processes independently.
```python
import sequential_functions as sf
import threading
import time
import os

def main():
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
    outputs=list(sequence(range(3)))
    print(outputs)

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

if __name__ == "__main__":
    main()
```
Output
```shell
function_a(0) ran in main thread
function_a(1) ran in main thread
function_a(2) ran in main thread
function_b(0) ran in thread ThreadPoolExecutor-0_0
function_b(1) ran in thread ThreadPoolExecutor-0_1
function_b(2) ran in thread ThreadPoolExecutor-0_2
function_c(0) ran in process 19245
function_c(1) ran in process 19246
function_c(2) ran in process 19247
[0, 1, 2]
```
## Callables
Functions can be any type of callable.
Use closures and callable objects to change the behaviour of functions
```python
import sequential_functions as sf

def main():
    sequence = sf.Compose(
        to_string,
        append_string(" Hello"),
        append_string(" World!"),
        EncloseString("**"),
        EncloseString(".."),
    )

    for x in sequence(range(5)):
        print(x)

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

if __name__ == "__main__":
    main()
```
Output
```shell
..**0 Hello World!**..
..**1 Hello World!**..
..**2 Hello World!**..
..**3 Hello World!**..
..**4 Hello World!**..
```
## Item Growth
Functions can yield out more items than they take in.
```python
import sequential_functions as sf

def main():
    sequence = sf.Compose(
        yield_video_frames,
        detect_objects,
    )
    for x in sequence(range(3)):
        print(x)

def yield_video_frames(x):
    num_frames = 3
    for i in range(num_frames):
        yield f"Video {x}, Frame {i}"

def detect_objects(x):
    return f" Detecting objects in {x}"

if __name__ == "__main__":
    main()
```
Output
```shell
 Detecting objects in Video 0, Frame 0
 Detecting objects in Video 0, Frame 1
 Detecting objects in Video 0, Frame 2
 Detecting objects in Video 1, Frame 0
 Detecting objects in Video 1, Frame 1
 Detecting objects in Video 1, Frame 2
 Detecting objects in Video 2, Frame 0
 Detecting objects in Video 2, Frame 1
 Detecting objects in Video 2, Frame 2
```
