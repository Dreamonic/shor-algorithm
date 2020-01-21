from projectq.meta import Dagger
from projectq.ops import Swap

from src.topology.gates.add import addModN
from src.topology.gates.qft import qft, qft_inverse
from src.util.math import modinv


def _CMultModN(eng, circuit, c, x, qubits, ancilla, a, N):
    n = len(x)

    qft(eng, circuit, qubits)
    for i in range(n):
        addModN(eng, circuit, c, x[i], qubits, ancilla, (2 ** i) * a % N, N)
    qft_inverse(eng, circuit, qubits)


def CMultModN(eng, circuit, c, x, qubits, ancilla, a, N):
    n = len(x)
    _CMultModN(eng, circuit, c, x, qubits, ancilla, a, N)
    for i in range(n):
        circuit.apply_ld_two_qubit_gate(Swap, x[i], qubits[i])
    # All(Swap) | zip(x, qubits)
    with Dagger(eng):
        _CMultModN(eng, circuit, c, x, qubits, ancilla, modinv(a, N), N)
