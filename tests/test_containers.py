import pytest
from sequential_functions import Compose
import os

  

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

def test_multi_process():
    f = Compose(
        double,
        sub_1,       
        num_workers=2,
    )

    n = 10

    x = list(f(range(n)))
    y = [sub_1(double(x)) for x in range(n)]
    assert x==y


def test_exception():
    f = Compose(
        throw_exception,       
    )

    n = 10
    with pytest.raises(FakeException):
        x = list(f(range(n)))

def test_multi_process_exception():
    f = Compose(
        double,     
        throw_exception,  
        num_workers=3,
    )

    n = 10
    with pytest.raises(FakeException):
        x = list(f(range(n)))

# def test_multi_process_exit():
#     f = Compose(
#         double,     
#         system_exit,  
#         num_workers=3,
#     )

#     n = 10

#     x = list(f(range(n)))

def test_functions_that_yield_more_outputs_than_inputs_Compose():
    f = Compose(
        double,
        yield_twice,
        num_workers=3,
    )

    x = list(f([1,2,3,4,5]))
    y = [2,2,4,4,6,6,8,8,10,10]
    assert x==y

def test_functions_that_yield_more_outputs_than_inputs():
    f = Compose(
        double,
        yield_twice,
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

def system_exit(x):
    if x == 2:
        exit(1)
    return x

    
class FakeException(Exception): pass