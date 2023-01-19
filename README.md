# Sequential Functions
Compose functions into a sequence that are called sequentially.

Under the hood, functions are wrapped in generators so that a sequence can be composed as a generator chain.

# Examples
```Python
import sequential_functions as sf

def main():
    
    # Build a generator chain using Compose
    sequence = sf.Compose([
        square,
        plus_one,
    ])

    # Use list to pull items through the generator chain
    outputs = list(sequence(range(5)))
    
    # outputs = [1,2,5,10,17]

def square(x):
    return x*x

def plus_one(x):
    return x + 1

```
