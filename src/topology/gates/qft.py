from projectq.meta import Dagger
from projectq.ops import H, CRz

from src.gates.rotate import calculate_phase


def qft(eng, circuit, qubits):
    m = len(qubits)
    for i in range(m - 1, -1, -1):
        circuit.apply_single_qubit_gate(H, qubits[i])
        for j in range(2, i + 2):
            circuit.apply_ld_two_qubit_gate(CRz(calculate_phase(j)), qubits[i - j + 1], qubits[i])


def qft_inverse(eng, circuit, qubits):
    with Dagger(eng):
        qft(eng, circuit, qubits)
