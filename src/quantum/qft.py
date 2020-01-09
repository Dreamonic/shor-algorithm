import numpy as np
from projectq.meta import Dagger
from projectq.ops import H, CRz, X


def calculate_phase(m):
    return 2 * np.pi / (2 ** m)


def qft(eng, qubits):
    m = len(qubits)
    for i in range(m):
        H | qubits[i]
        for j in range(i+1, m):
            CRz(calculate_phase(j + 1)) | (qubits[j], qubits[i])


def qft_inverse(eng, qubits):
    with Dagger(eng):
        qft(eng, qubits)


def run(eng):
    qubits = eng.allocate_qureg(4)
    qft(eng, qubits)
    X | qubits[0]
    qft_inverse(eng, qubits)
    eng.flush()
    return qubits
