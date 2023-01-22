# Under the Hood
# Compose uses generator chaining to run items through each of the functions.
# Both of these methods produce the same output
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