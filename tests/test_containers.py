import pytest
from sequential_functions import Compose

def double(x):
    return 2 * x

def sub_1(x):
    return x - 1


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

