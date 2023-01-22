# Toy Example
# Toy example that highlights the syntax.
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