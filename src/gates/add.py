from projectq.meta import Control, Dagger
from projectq.ops import Rz, CNOT, X

from src.gates.qft import qft, qft_inverse
from src.gates.rotate import calculate_phase


def add(eng, qubits, value):
    length = len(qubits)
    for n in range(length - 1, -1, -1):
        for i in range(1, n + 2):
            ctrl = value & (1 << (n - i + 1))
            if ctrl > 0:
                Rz(calculate_phase(i)) | qubits[n]


def add_inverse(eng, qubits, value):
    with Dagger(eng):
        add(eng, qubits, value)


def Cadd(eng, c, qubits, value):
    with Control(eng, c):
        add(eng, qubits, value)


def Cadd_inverse(eng, c, qubits, value):
    with Dagger(eng):
        Cadd(eng, c, qubits, value)


def CCadd(eng, c1, c2, qubits, value):
    with Control(eng, c1):
        Cadd(eng, c2, qubits, value)


def CCadd_inverse(eng, c1, c2, qubits, value):
    with Dagger(eng):
        CCadd(eng, c1, c2, qubits, value)


def addModN(eng, c1, c2, qubits, ancilla, a, N):
    m = len(qubits) - 1

    CCadd(eng, c1, c2, qubits, a)
    add_inverse(eng, qubits, N)
    qft_inverse(eng, qubits)
    CNOT | (qubits[m], ancilla)
    qft(eng, qubits)
    Cadd(eng, ancilla, qubits, N)
    CCadd_inverse(eng, c1, c2, qubits, a)
    qft_inverse(eng, qubits)
    X | qubits[m]
    CNOT | (qubits[m], ancilla)
    X | qubits[m]
    qft(eng, qubits)
    CCadd(eng, c1, c2, qubits, a)
