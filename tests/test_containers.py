import pytest
from sequential_functions import Compose, MultiProcess
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
    f = MultiProcess(
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
    f = MultiProcess(
        double,     
        throw_exception,  
        num_workers=1,
    )

    n = 10
    with pytest.raises(FakeException):
        x = list(f(range(n)))

def print_process(x):
    print(os.getpid())
    return x

def double(x):
    return 2 * x

def sub_1(x):
    return x - 1

def assert_batch_double(x_batch):
    assert type(x_batch) is list
    assert len(x_batch) > 0
    y_batch = [double(x) for x in x_batch]
    return y_batch

def throw_exception(x):
    raise FakeException()
    return x

    
class FakeException(Exception): pass