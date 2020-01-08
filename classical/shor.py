import time

import numpy as np


def find_co_prime(n, at_least=0):
    if at_least < 2:
        at_least = 2

    while np.gcd(n, at_least) != 1:
        if at_least > n:
            raise Exception("There is no co-prime a, such that 1 < a < n.")
        n = n + 1

    return at_least


def find_prime_factors(n, a):
    return np.gcd(n, a - 1), np.gcd(n, a + 1)


def find_period(n, a):
    for i in range(2 * n ** 2)[1:]:
        if pow(a, i, n) == 1:
            return i


def shor(n, last_a=0):
    last_a = find_co_prime(n, last_a)
    period = find_period(n, last_a)
    if np.mod(period, 2) == 0:
        return find_prime_factors(n, pow(last_a, int(period / 2)))
    else:
        return shor(n, last_a)


start_time = time.time()
res = shor(53645351)  # Prime factors are: 8747 and 6133
end_time = time.time()

print("Found:", res, "in", (end_time - start_time), "seconds")
