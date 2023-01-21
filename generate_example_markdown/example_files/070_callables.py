# Callables
# Functions can be any type of callable.
# Use closures and callable objects to change the behaviour of functions
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