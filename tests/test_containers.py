import pytest
from sequential_functions import Compose, Batch


  

def test_compose_build_generator_chain():

    f = Compose(
        double,
        sub_1,
    )

    n = 10

    x = list(f(range(n)))
    y = [sub_1(double(x)) for x in range(n)]
    assert x==y


def test_nested_compose():

    f = Compose(
        double,
        Compose(
            double,
            sub_1,
        ),
        sub_1,
    )

    n = 10

    x = list(f(range(n)))
    y = [sub_1(sub_1(double(double(x)))) for x in range(n)]
    assert x==y

def test_batch():
    f = Batch(
        assert_batch_double,
        batch_size=2,
    )

    n = 10

    x = list(f(range(n)))
    y = [double(x) for x in range(n)]
    assert x==y

def test_batch_nested():
    f = Compose(
        Batch(
            Compose(
                assert_batch_double,
            ),
            batch_size=2,
        ),
    )

    n = 10

    x = list(f(range(n)))
    y = [double(x) for x in range(n)]
    assert x==y

def double(x):
    return 2 * x

def sub_1(x):
    return x - 1

def assert_batch_double(x_batch):
    assert type(x_batch) is list
    assert len(x_batch) > 0
    y_batch = [double(x) for x in x_batch]
    return y_batch
