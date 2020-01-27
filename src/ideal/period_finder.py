from fractions import Fraction

import numpy as np
from projectq.ops import All, H, Measure, X, Rz

from src.classical import shor
from src.ideal.gates.gates import CMultModN
from src.ideal.gates import qft
from src.shared.rotate import calculate_phase


def find_period(engine, N):
    """
    Find the prime factors belonging to N, by finding the period using Shor's algorithm.
    This algorithm uses intermediate measurements to limit the amount of qubits needed to
    2n + 3.
    :param engine: The engine used for computations.
    :param N: The number to be factored into primes.
    """
    # If N is even, return 2.
    if N % 2 == 0:
        print("Factor is", 2)
        exit(0)

    # Find the number of bits needed to represent N.
    n = int(np.ceil(np.log2(N)))

    # Pick a random co-prime number.
    a = shor.find_co_prime_stochastic(N)

    # If the gcd(a, N) == 1, return the gcd.
    if a < 0:
        print("Factor is", -a)
        exit(0)

    # Initialize the classical register keeping track of the measurements.
    measurements = [0] * (2 * n)

    # Prepare the qubits needed for the algorithm
    x = engine.allocate_qureg(n)        # Used for the remainder
    b = engine.allocate_qureg(n + 1)    # Used for the addition
    c = engine.allocate_qubit()         # Used for the classical period
    ancilla = engine.allocate_qubit()   # Used to check for underflow

    # Initialize the remainder to 1
    X | x[0]

    # For every bit apply the module function.
    for i in range(2 * n):
        H | c
        CMultModN(engine, c, x, b, ancilla, pow(a, 2 ** i), N)

        # Apply QFT based on classical values.
        for j in range(i):
            if measurements[j]:
                Rz(-calculate_phase(i - j)) | c
        H | c

        # Intermediate measurement
        Measure | c
        engine.flush()
        measurements[i] = int(c)

        # Restore c to its original state
        if measurements[i]:
            X | c

    # This is so that projectQ correctly executes the algorithm.
    All(Measure) | b
    All(Measure) | x
    All(Measure) | ancilla

    # Find the decimal value corresponding to the binary results.
    y = sum([(measurements[2 * n - 1 - i] * 1. / (1 << (i + 1)))
             for i in range(2 * n)])
    period = Fraction(y).limit_denominator(N - 1).denominator
    if period % 2 != 0:
        period *= 2

    # Find the two prime factors.
    if np.mod(period, 2) == 0:
        print(shor.find_prime_factors(N, pow(a, int(period / 2))))


def find_period_4n(engine, N):
    """
    Find the prime factors belonging to N, by finding the period using Shor's algorithm.
    This algorithm does not use intermediate measurements, so that it can be optimized on a simulator.
    :param engine: The engine used for computations.
    :param N: The number to be factored into primes.
    """
    # Find the number of bits needed to represent N.
    n = int(np.ceil(np.log2(N)))

    # Pick a random co-prime number.
    a = shor.find_co_prime_stochastic(N)

    # If the gcd(a, N) == 1, return the gcd.
    if a < 0:
        print("Factor is", -a)
        exit(0)

    # Prepare the qubits needed for the algorithm
    ctrl = engine.allocate_qureg(2 * n) # Used for the period
    b = engine.allocate_qureg(n)        # Used for the addition
    x = engine.allocate_qureg(n)        # Used for the remainder
    ancilla = engine.allocate_qubit()   # Used to check for underflow

    # Create a maximal superposition
    All(H) | ctrl

    # Initialize the remainder to 1
    X | x[0]

    # Find the period
    for i in range(2 * n):
        CMultModN(engine, ctrl[i], x, b, ancilla, pow(a, 2 ** i), N)

    qft.qft_inverse(engine, ctrl)

    engine.flush()

    # Find the decimal value corresponding to the binary results.
    measurements = [int(q) for q in ctrl]
    y = sum([(measurements[2 * n - 1 - i] * 1. / (1 << (i + 1)))
             for i in range(2 * n)])
    period = Fraction(y).limit_denominator(N - 1).denominator
    print("period found =", period)
    if period % 2 != 0:
        period *= 2

    # Find the two prime factors.
    if np.mod(period, 2) == 0:
        print(shor.find_prime_factors(N, pow(a, int(period / 2))))
