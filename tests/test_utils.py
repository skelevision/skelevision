import os

import pytest

from skelevision import follows, successors, predecessors

from sortedcontainers import SortedSet

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "datasets")


def test_follows():
    t1 = ("a1","a2","a4","a5","a6","a2")
    target = {
        ("a1", "a2"): 1,
        ("a2", "a4"): 1,
        ("a4", "a5"): 1,
        ("a5", "a6"): 1,
        ("a6", "a2"): 1
    }
    f = follows(t1)

    for k, v in f.items():
        assert k in target
        assert target[k] == v

    for k, v in target.items():
        assert k in f
        assert f[k] == v

def test_follows_distance_2():
    t1 = ("a1","a2","a4","a5","a6","a2")
    target = {
        ("a1", "a4"): 1,
        ("a2", "a5"): 1,
        ("a4", "a6"): 1,
        ("a5", "a2"): 1
    }
    f = follows(t1, distance=2)

    for k, v in f.items():
        assert k in target
        assert target[k] == v

    for k, v in target.items():
        assert k in f
        assert f[k] == v


def test_follows_loop_len_1():
    t2 = ("a1","a2","a4","a5","a6","a2", "a2", "a2")
    target = {
        ("a1", "a2"): 1,
        ("a2", "a4"): 1,
        ("a4", "a5"): 1,
        ("a5", "a6"): 1,
        ("a6", "a2"): 1,
        ("a2", "a2"): 2
    }
    f = follows(t2, distance=1)

    for k, v in f.items():
        assert k in target
        assert target[k] == v

    for k, v in target.items():
        assert k in f
        assert f[k] == v

def test_follows_exception_no_integer_distance():
    t1_list = ["a1","a2","a4","a5","a6","a2"]
    with pytest.raises(ValueError):
        follows(t1_list)

def test_follows_exception_no_integer_distance():
    t1 = ("a1","a2","a4","a5","a6","a2")
    with pytest.raises(ValueError):
        follows(t1, distance=1.2)

def test_follows_exception_no_positive_integer():
    t1 = ("a1","a2","a4","a5","a6","a2")
    with pytest.raises(ValueError):
        follows(t1, distance=-3.3)

def test_successors():
    t1 = ("a1","a2","a4","a5","a6","a2")
    target = {
        "a1": SortedSet({"a2", "a4", "a5", "a6"}),
        "a2": SortedSet({"a2", "a4", "a5", "a6"}),
        "a4": SortedSet({"a2", "a5", "a6"}),              
        "a5": SortedSet({"a2", "a6"}),
        "a6": SortedSet({"a2"}),
    }
    assert successors(t1) == target

def test_predecessor():
    t1 = ("a1","a2","a4","a5","a6","a2")
    target = {
        "a2": SortedSet({"a1", "a2", "a4", "a5", "a6"}),
        "a6": SortedSet({"a1", "a2", "a4", "a5"}),
        "a5": SortedSet({"a1", "a2", "a4"}),
        "a4": SortedSet({"a1", "a2"}),
    }
    assert predecessors(t1) == target
