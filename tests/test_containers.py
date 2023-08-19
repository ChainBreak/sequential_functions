import pytest
from sequential_functions import Compose
import os
import threading
import time

  
@pytest.mark.parametrize("num_processes, num_threads",[
    (0,0),
    (3,0),
    (20,0),
    (0,3),
    (0,20),
])
def test_compose(num_processes, num_threads):

    f = Compose(
        double,
        sub_1,
        num_processes=num_processes,
        num_threads=num_threads,
    )

    n = 10

    x = list(f(range(n)))
    y = [sub_1(double(x)) for x in range(n)]
    assert set(x)==set(y)

@pytest.mark.parametrize("num_processes, num_threads",[
    (0,0),
    (3,0),
    (20,0),
    (0,3),
    (0,20),
])
def test_nested_compose(num_processes, num_threads):

    f = Compose(
        double,
        Compose(
            double,
            sub_1,
        ),
        sub_1,
        num_processes=num_processes,
        num_threads=num_threads,
    )

    n = 10

    x = list(f(range(n)))
    y = [sub_1(sub_1(double(double(x)))) for x in range(n)]
    assert set(x)==set(y)

@pytest.mark.parametrize("num_processes, num_threads",[
    (0,0),
    (3,0),
    (20,0),
    (0,3),
    (0,20),
])
def test_exception(num_processes, num_threads):
    f = Compose(
        throw_exception, 
        num_processes=num_processes,
        num_threads=num_threads,      
    )

    n = 10
    with pytest.raises(FakeException):
        x = list(f(range(n)))

@pytest.mark.parametrize("num_processes, num_threads",[
    (0,0),
    (3,0),
    (20,0),
    (0,3),
    (0,20),
])
def test_functions_that_yield_more_outputs_than_inputs(num_processes, num_threads):
    f = Compose(
        double,
        yield_twice,
        num_processes=num_processes,
        num_threads=num_threads,
    )

    x = list(f([1,2,3,4,5]))
    y = [2,2,4,4,6,6,8,8,10,10]
    assert set(x)==set(y)

@pytest.mark.parametrize("num_processes",[
    1,
    10,
])
def test_work_is_actually_done_different_processes(num_processes):
    
    f = Compose(
        get_process_pid,
        num_processes=num_processes,
    )

    pid_set = set(f(range(1000)))
    assert len(pid_set) == num_processes

@pytest.mark.parametrize("num_threads",[
    1,
    10,
])
def test_work_is_actually_done_different_threads(num_threads):
    
    f = Compose(
        get_thread_name,
        num_threads=num_threads,
    )

    pid_set = set(f(range(1000)))
    assert len(pid_set) == num_threads


@pytest.mark.parametrize("num_processes, num_threads",[
    (0,0),
    (3,0),
    (20,0),
    (0,3),
    (0,20),
])
def test_that_all_item_are_not_immediately_consumed(num_processes, num_threads):

    counts = {"in":0,"out":0}

    def generator():
        for x in range(1000):
            counts["in"] += 1
            # print("in",x)
            yield x

    f = Compose(
        double,
        num_processes=num_processes,
        num_threads=num_threads,
    )

    for x in f( generator()):
        counts["out"] += 1
        # print("out",x)

        num_workers = max(num_processes,num_threads)
        assert counts["in"] <= counts["out"] + num_workers + 2

def yield_twice(x):
    yield x
    yield x

def double(x):
    return 2 * x

def sub_1(x):
    return x - 1

def slow(x):
    time.sleep(0.0001)

def throw_exception(x):
    raise FakeException()
    return x

def get_process_pid(x):
    time.sleep(0.0001)
    return os.getpid()

def get_thread_name(x):
    time.sleep(0.0001)
    return threading.current_thread().name

    
class FakeException(Exception): pass