from fractions import Fraction

import numpy as np
from projectq.libs.math import MultiplyByConstantModN
from projectq.ops import All, H, C, Measure

from src.classical import shor
from src.gates import qft
from src.gates.multiply import CMultModN


def find_period_1(engine, N):
    n = int(np.ceil(np.log2(N)))

    a = shor.find_co_prime_stochastic(N)
    if a < 0:
        print("Factor is", -a)
        exit(0)
    print("a =", a)
    qubits = engine.allocate_qureg(3 * n)

    All(H) | qubits[0:(2 * n)]

    for i in range(2 * n):
        # with Control(engine, qubits[i]):
        C(MultiplyByConstantModN(pow(a, 2 ** i, N), N)) | (qubits[i], qubits[(2 * n):(3 * n)])

    qft.qft_inverse(engine, qubits[0:(2 * n)])

    All(Measure) | qubits

    engine.flush()
    measurements = [int(q) for q in qubits[0:(2 * n)]]
    y = sum([(measurements[2 * n - 1 - i] * 1. / (1 << (i + 1)))
             for i in range(2 * n)])
    period = Fraction(y).limit_denominator(N - 1).denominator
    print("period found =", period)
    if period % 2 != 0:
        period *= 2

    if np.mod(period, 2) == 0:
        print(shor.find_prime_factors(N, pow(a, int(period / 2))))
    print('\nMeasured: {0}'.format([int(q) for q in qubits]))


def find_period_2(engine, N):
    n = int(np.ceil(np.log2(N)))

    a = shor.find_co_prime_stochastic(N)
    if a < 0:
        print("Factor is", -a)
        exit(0)
    print("a =", a)
    ctrl = engine.allocate_qureg(2 * n)
    b = engine.allocate_qureg(n)
    x = engine.allocate_qureg(n)
    ancilla = engine.allocate_qubit()

    All(H) | ctrl

    for i in range(2 * n):
        # with Control(engine, qubits[i]):
        CMultModN(engine, ctrl[i], x, b, ancilla, pow(a, 2 ** i), N)

    qft.qft_inverse(engine, ctrl)

    All(Measure) | ctrl
    All(Measure) | b
    All(Measure) | x
    Measure | ancilla

    engine.flush()
    measurements = [int(q) for q in ctrl]
    y = sum([(measurements[2 * n - 1 - i] * 1. / (1 << (i + 1)))
             for i in range(2 * n)])
    period = Fraction(y).limit_denominator(N - 1).denominator
    print("period found =", period)
    if period % 2 != 0:
        period *= 2

    if np.mod(period, 2) == 0:
        print(shor.find_prime_factors(N, pow(a, int(period / 2))))
