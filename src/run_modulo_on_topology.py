import numpy as np
from projectq.ops import X, Measure

from src.engines.pq_engine import get_engine
from src.topology.circuit import AdvancedCircuit, Circuit
from src.topology.parallel_gates.multiply import CMultModN
from src.topology.parallel_gates.prepare_number import prepare_number


def pretty_print(ol):
    result = [0] * (int(max(ol, key=int)) + 1)
    for idx, li in ol.items():
        result[int(idx)] = li
    return result


def normalize(wanted):
    return [i / sum(wanted) for i in wanted]


if __name__ == '__main__':
    # print("ESTABLISHING SESSION")
    # qi = get_api_session()
    # print("SESSION ESTABLISHED")

    qi_engine, qi_backend = get_engine()

    # circuit_backend = CommandPrinter()
    # qi_engine = MainEngine(circuit_backend)

    a = 4
    nx = 4
    N = 7
    n = int(np.ceil(np.log2(N)))
    print("Running (", a, "*", nx, ")mod", N, " on ", n, " qubits", sep="")

    circuit = Circuit()
    circuit.create_bus(qi_engine, n + 2)
    circuit.add_all_logicals(qi_engine)

    qubits = [("log_" + str(i)) for i in range(n + 1)]
    x = [("log_" + str(i)) for i in range(n + 1, 2 * n + 1)]
    c = "log_" + str(2 * n + 1)
    ancilla = "log_" + str(2 * n + 2)

    circuit.apply_single_qubit_gate(X, c)

    prepare_number(qi_engine, circuit, x, nx)

    CMultModN(qi_engine, circuit, c, x, qubits, ancilla, a, N)

    # if qi_backend is None:
    for i in range(n + 1, 2 * n + 2):
        circuit.apply_single_qubit_gate(Measure, "log_" + str(i))
    # All(Measure) | x

    qi_engine.flush()

    result_qi = [circuit.get_qubit(name).qubit for name in x]

    print(circuit.gates_applied)
    print('\nMeasured: {0}'.format([int(q) for q in result_qi]))
    # print(circuit_backend.get_latex())
    # print('Probabilities {0}'.format(qi_backend.get_probabilities(result_qi)))
    del circuit
