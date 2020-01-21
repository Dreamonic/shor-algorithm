from src.engines.pq_engine import get_engine
from src.gates.qft import qft, qft2, qft_inverse
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
    # qi = get_api_session()
    print("SESSION ESTABLISHED")

    qi_engine, qi_backend = get_engine()

    q = qi_engine.allocate_qureg(6)

    prepare_number(qi_engine, q[0:3], 5)
    prepare_number(qi_engine, q[3:6], 5)

    qft(qi_engine, q[0:3])
    qft2(qi_engine, q[3:6])
    qft_inverse(qi_engine, q[0:3])
    qft_inverse(qi_engine, q[3:6])

    # CRz(calculate_phase(i)) | (q[2], q[3])
    # CNOT | (q[2], q[3])

    # Rz(-np.pi/2) | q[0]
    # Rx(np.pi/2) | q[1]
    # Rz(np.pi/2) | q[1]
    # ISwap | (q[0], q[1])
    # Rx(np.pi/2) | q[0]
    # ISwap | (q[0], q[1])
    # Rz(np.pi/2) | q[1]
    #
    # R(-calculate_phase(i+1)) | q[1]
    #
    # Rz(-np.pi/2) | q[0]
    # Rx(np.pi/2) | q[1]
    # Rz(np.pi/2) | q[1]
    # ISwap | (q[0], q[1])
    # Rx(np.pi/2) | q[0]
    # ISwap | (q[0], q[1])
    # Rz(np.pi/2) | q[1]
    #
    # R(calculate_phase(i+1)) | q[0]
    # R(calculate_phase(i+1)) | q[1]

    # All(Measure) | [q1, q2, q3, q4]

    # circuit_backend = CommandPrinter()
    # qi_engine = MainEngine(circuit_backend)

    # a = 4
    # nx = 4
    # N = 7
    # n = int(np.ceil(np.log2(N)))
    # print("Running (", a, "*", nx, ")mod", N, " on ", n, " qubits", sep="")
    #
    # qubits = qi_engine.allocate_qureg(n + 1)
    # x = qi_engine.allocate_qureg(n)
    # c = qi_engine.allocate_qubit()
    # ancilla = qi_engine.allocate_qubit()
    #
    # X | c
    #
    # prepare_number(qi_engine, x, nx)
    #
    # CMultModN(qi_engine, c, x, qubits, ancilla, a, N)
    #
    # # if qi_backend is None:
    # All(Measure) | x

    qi_engine.flush()

    # print('\nMeasured: {0}'.format([int(q) for q in result_qi]))
    # print(circuit_backend.get_latex())
    print('Probability 001: {0}'.format(qi_backend.get_probability("001", q[0:3])))
    print('Probability 010: {0}'.format(qi_backend.get_probability("010", q[0:3])))
    print('Probability 011: {0}'.format(qi_backend.get_probability("011", q[0:3])))
    print('Probability 100: {0}'.format(qi_backend.get_probability("100", q[0:3])))
    print('Probability 101: {0}'.format(qi_backend.get_probability("101", q[0:3])))
    print('Probability 110: {0}'.format(qi_backend.get_probability("110", q[0:3])))
    print('Probability 111: {0}'.format(qi_backend.get_probability("111", q[0:3])))
    print('Probability 000: {0}'.format(qi_backend.get_probability("000", q[3:6])))
    print('Probability 001: {0}'.format(qi_backend.get_probability("001", q[3:6])))
    print('Probability 010: {0}'.format(qi_backend.get_probability("010", q[3:6])))
    print('Probability 011: {0}'.format(qi_backend.get_probability("011", q[3:6])))
    print('Probability 100: {0}'.format(qi_backend.get_probability("100", q[3:6])))
    print('Probability 101: {0}'.format(qi_backend.get_probability("101", q[3:6])))
    print('Probability 110: {0}'.format(qi_backend.get_probability("110", q[3:6])))
    print('Probability 111: {0}'.format(qi_backend.get_probability("111", q[3:6])))
