from fractions import Fraction

import numpy as np
from projectq.ops import X, Measure, Rz, H

from src.classical import shor
from src.engines.pq_engine import get_engine
from src.shared.rotate import calculate_phase
from src.topology.all_gates.multiply import CMultModN
from src.topology.circuit import Circuit

if __name__ == '__main__':

    engine, backend = get_engine()

    N = 15
    n = int(np.ceil(np.log2(N)))

    a = shor.find_co_prime_stochastic(N)
    if a < 0:
        print("Factor is", -a)
        exit(0)
    print("a =", a)

    circuit = Circuit()
    circuit.create_bus(engine, n + 2)
    circuit.add_all_logicals(engine)

    x = [("log_" + str(i)) for i in range(n)]
    b = [("log_" + str(i)) for i in range(n, 2 * n + 1)]
    c = "log_" + str(2 * n + 1)
    ancilla = "log_" + str(2 * n + 2)
    measurements = [0] * (2 * n)

    circuit.apply_single_qubit_gate(X, x[0])

    for i in range(2 * n):
        circuit.apply_single_qubit_gate(X, c)
        CMultModN(engine, circuit, c, x, b, ancilla, pow(a, 2 ** i), N)

        for j in range(i):
            if measurements[j]:
                circuit.apply_single_qubit_gate(Rz(-calculate_phase(i - j)), c)
        circuit.apply_single_qubit_gate(H, c)

    for i in range(n + 1, 2 * n + 1):
        circuit.apply_single_qubit_gate(Measure, "log_" + str(i))

    engine.flush()

    y = sum([(measurements[2 * n - 1 - i] * 1. / (1 << (i + 1)))
             for i in range(2 * n)])
    period = Fraction(y).limit_denominator(N - 1).denominator
    print("period found =", period)
    if period % 2 != 0:
        period *= 2

    if np.mod(period, 2) == 0:
        print(shor.find_prime_factors(N, pow(a, int(period / 2))))

    del circuit
