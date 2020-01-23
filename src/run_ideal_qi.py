"""
This example is copied from https://github.com/ProjectQ-Framework/ProjectQ
and is covered under the Apache 2.0 license.
"""
import time

from src.engines.qi_engine import get_engine
from src.ideal.period_finder import find_period_4n

if __name__ == '__main__':
    engine, qi_backend = get_engine()

    N = 15

    start = time.time()
    find_period_4n(engine, N)
    end = time.time()
    print("Time elapsed:", end - start, "seconds")
