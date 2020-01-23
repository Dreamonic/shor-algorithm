from projectq.meta import Dagger

from src.shared.rotate import calculate_phase
from src.topology.parallel_gates.simple import H, CRz


def qft(eng, circuit, qubits):
    m = len(qubits)
    for i in range(m - 1, -1, -1):
        H(eng, circuit, qubits[i])
        for j in range(2, i + 2):
            CRz(eng, circuit, qubits[i - j + 1], qubits[i], calculate_phase(j))


def qft_inverse(eng, circuit, qubits):
    with Dagger(eng):
        qft(eng, circuit, qubits)
