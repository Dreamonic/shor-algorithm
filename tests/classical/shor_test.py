from src.classical.shor import *


def test_find_co_prime():
    assert find_co_prime(15) == 2


def test_large_prime():
    assert shor(53645351) == (8747, 6133)
