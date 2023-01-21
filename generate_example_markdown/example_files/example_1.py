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