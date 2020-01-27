from projectq.meta import Dagger
from projectq.ops import H, CRz, X

from src.shared.rotate import calculate_phase


def qft(eng, qubits):
    m = len(qubits)
    for i in range(m - 1, -1, -1):
        H | qubits[i]
        for j in range(2, i + 2):
            CRz(calculate_phase(j)) | (qubits[i - j + 1], qubits[i])


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
