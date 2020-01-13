from projectq.meta import Dagger
from projectq.ops import Swap

from src.gates.add import addModN
from src.gates.qft import qft, qft_inverse
from src.util.math import modinv


def _CMultModN(eng, c, x, qubits, ancilla, a, N):
    n = len(qubits)

    qft(eng, qubits)
    for i in range(n):
        addModN(eng, c, x[i], qubits, ancilla, (2 ** i) * a % N, N)
    qft_inverse(eng, qubits)


def CMultModN(eng, c, x, qubits, ancilla, a, N):
    n = len(qubits)
    _CMultModN(eng, c, x, qubits, ancilla, a, N)
    for i in range(n):
        Swap | (x[i], qubits[i])
    # All(Swap) | zip(x, qubits)
    with Dagger(eng):
        _CMultModN(eng, c, x, qubits, ancilla, modinv(a, N), N)
