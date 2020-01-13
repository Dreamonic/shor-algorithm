import numpy as np
from projectq.ops import X, All, Measure

from src.connection.qi_api import get_api_session
from src.engines.qi_engine import get_engine
from src.gates.multiply import CMultModN
from src.quantum.prepare_number import prepare_number

wanted = [1, 1, 1, 1]


def pretty_print(ol):
    result = [0] * (int(max(ol, key=int)) + 1)
    for idx, li in ol.items():
        result[int(idx)] = li
    return result


def normalize(wanted):
    return [i / sum(wanted) for i in wanted]


if __name__ == '__main__':
    print("ESTABLISHING SESSION")
    qi = get_api_session()
    print("SESSION ESTABLISHED")

    qi_engine, qi_backend = get_engine(qi)

    a = 4
    nx = 4
    N = 7
    n = int(np.ceil(np.log2(N)))
    print("Running (", a, "*", nx, ")mod", N, " on ", n, " qubits", sep="")

    qubits = qi_engine.allocate_qureg(n+1)
    x = qi_engine.allocate_qureg(n)
    c = qi_engine.allocate_qubit()
    ancilla = qi_engine.allocate_qubit()

    X | c

    prepare_number(qi_engine, x, nx)

    CMultModN(qi_engine, c, x, qubits, ancilla, a, N)

    if qi_backend is None:
        All(Measure) | x

    qi_engine.flush()

    result_qi = x

    print('\nMeasured: {0}'.format([int(q) for q in result_qi]))
    # print('Probabilities {0}'.format(qi_backend.get_probabilities(result_qi)))
