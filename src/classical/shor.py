import numpy as np


def find_co_prime(n, stochastic=False, at_least=0):
    """
    This finds a number that is co-prime with n, such that it is larger than 'at_least'.
    In case there is no such number it will raise an exception.

    :param n: The number that should be factored into primes.
    :param at_least: The threshold for the co-prime number, i.e. the result should be larger than 'at_least'.
    :return: A number co-prime with n.
    """
    if stochastic:
        return find_co_prime_stochastic(n)
    else:
        return find_co_prime_deterministic(n, at_least)


def find_co_prime_deterministic(n, at_least=0):
    """
    This finds a number that is co-prime with n, such that it is larger than 'at_least'.
    In case there is no such number it will raise an exception.

    :param n: The number that should be factored into primes.
    :param at_least: The threshold for the co-prime number, i.e. the result should be larger than 'at_least'.
    :return: A number co-prime with n.
    """
    # The number should be at least 2, since 0 and 1 cannot be co-prime with any number.
    if at_least < 2:
        at_least = 2

    # If the numbers are co-prime they share no common factor larger than 1.
    while np.gcd(n, at_least) != 1:
        if at_least > n:
            raise Exception("There is no co-prime a, such that 1 < a < n.")
        n = n + 1

    return at_least


def find_co_prime_stochastic(n):
    """
    Find a factor that is coprime with n randomly.
    :param n:  The number that should be factored into primes.
    :return: A number co-prime with n.
    """
    a = int(np.random.randint(2, high=n))
    if np.gcd(n, a) != 1:
        return -np.gcd(n, a)
    return a


def find_prime_factors(n, a):
    """
    Finds the prime factors based on the fact that the gcd(a^r/2 + 1, N) is a prime factor of N, given that a is
    co-prime with N.
    :param n: The number that should be factored into primes.
    :param a: A number co-prime with n.
    :return: The 2 prime factors of n.
    """
    p1 = np.gcd(n, a - 1)
    p2 = np.gcd(n, a + 1)
    if (p1 == 1 and p2 == 1) or (p1 == n and p2 == n) or (p1 == 1 and p2 == n) or (p1 == n and p2 == 1):
        return "\033[91mBad luck: Found {} and {}\033[0m".format(p1, p2)
    else:
        if p1 == 1 or p1 == n:
            return p2, int(n / p2)
        else:
            return p1, int(n / p1)


def find_period(n, a):
    """
    Classical period-finding algorithm, by simply increasing the power by 1, till the a^p mod n = 1.
    :param n: The number that should be factored into primes.
    :param a: A number co-prime with n.
    :return: The period after which a^p mod n = 1.
    """
    for i in range(2 * n ** 2)[1:]:
        if pow(a, i, n) == 1:
            return i


def shor(n, last_a=0):
    """
    Execute Shor's algorithm.
    :param n: The number that should be factored into primes.
    :param last_a: The last tried co-prime number.
    :return: The prime factors of n.
    """
    last_a = find_co_prime_deterministic(n, last_a)
    period = find_period(n, last_a)
    if np.mod(period, 2) == 0:
        return find_prime_factors(n, pow(last_a, int(period / 2)))
    else:
        return shor(n, last_a)

#
# start_time = time.time()
# res = shor(53645351)  # Prime factors are: 8747 and 6133
# end_time = time.time()
#
# print("Found:", res, "in", (end_time - start_time), "seconds")
