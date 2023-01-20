import pytest
from sequential_functions import Compose
import os

  
@pytest.mark.parametrize("num_processes",[
    0,
    3,
    20,
])
def test_compose(num_processes):

    f = Compose(
        double,
        sub_1,
        num_processes=num_processes,
    )

    n = 10

    x = list(f(range(n)))
    y = [sub_1(double(x)) for x in range(n)]
    assert x==y

@pytest.mark.parametrize("num_processes",[
    0,
    3,
    20,
])
def test_nested_compose(num_processes):

    f = Compose(
        double,
        Compose(
            double,
            sub_1,
        ),
        sub_1,
        num_processes=num_processes,
    )

    n = 10

    x = list(f(range(n)))
    y = [sub_1(sub_1(double(double(x)))) for x in range(n)]
    assert x==y

@pytest.mark.parametrize("num_processes",[
    0,
    3,
    20,
])
def test_exception(num_processes):
    f = Compose(
        throw_exception, 
        num_processes=num_processes,      
    )

    n = 10
    with pytest.raises(FakeException):
        x = list(f(range(n)))

@pytest.mark.parametrize("num_processes",[
    0,
    3,
    20,
])
def test_functions_that_yield_more_outputs_than_inputs(num_processes):
    f = Compose(
        double,
        yield_twice,
        num_processes=num_processes,
    )

    x = list(f([1,2,3,4,5]))
    y = [2,2,4,4,6,6,8,8,10,10]
    assert x==y


def yield_twice(x):
    yield x
    yield x

def double(x):
    return 2 * x

def sub_1(x):
    return x - 1

def throw_exception(x):
    raise FakeException()
    return x
    
class FakeException(Exception): pass