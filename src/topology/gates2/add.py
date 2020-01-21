import numpy as np
from projectq.meta import Dagger
from projectq.ops import Rz, Rx

from src.topology.gates2.qft import qft, qft_inverse
from src.topology.gates2.rotate import calculate_phase
from src.topology.gates2.simple import CRz, CNOT


def add(eng, circuit, qubits, value):
    length = len(qubits)
    for n in range(length - 1, -1, -1):
        for i in range(1, n + 2):
            ctrl = value & (1 << (n - i + 1))
            if ctrl > 0:
                circuit.apply_single_qubit_gate(Rz(calculate_phase(i)), qubits[n])


def add_inverse(eng, circuit, qubits, value):
    with Dagger(eng):
        add(eng, circuit, qubits, value)


def Cadd(eng, circuit, c, qubits, value):
    length = len(qubits)
    for n in range(length - 1, -1, -1):
        for i in range(1, n + 2):
            ctrl = value & (1 << (n - i + 1))
            if ctrl > 0:
                CRz(eng, circuit, c, qubits[n], calculate_phase(i))


def Cadd_inverse(eng, circuit, c, qubits, value):
    with Dagger(eng):
        Cadd(eng, circuit, c, qubits, value)


def CCRz(eng, circuit, c1, c2, qubit, angle):
    CRz(eng, circuit, c1, qubit, angle / 2)
    CNOT(eng, circuit, c2, c1)
    CRz(eng, circuit, c1, qubit, -angle / 2)
    CNOT(eng, circuit, c2, c1)
    CRz(eng, circuit, c2, qubit, angle / 2)


def CCadd(eng, circuit, c1, c2, qubits, value):
    length = len(qubits)
    for n in range(length - 1, -1, -1):
        for i in range(1, n + 2):
            ctrl = value & (1 << (n - i + 1))
            if ctrl > 0:
                CCRz(eng, circuit, c1, c2, qubits[n], calculate_phase(i))


def CCadd_inverse(eng, circuit, c1, c2, qubits, value):
    with Dagger(eng):
        CCadd(eng, circuit, c1, c2, qubits, value)


def addModN(eng, circuit, c1, c2, qubits, ancilla, a, N):
    m = len(qubits) - 1

    CCadd(eng, circuit, c1, c2, qubits, a)
    add_inverse(eng, circuit, qubits, N)
    qft_inverse(eng, circuit, qubits)
    CNOT(eng, circuit, qubits[m], ancilla)
    qft(eng, circuit, qubits)
    Cadd(eng, circuit, ancilla, qubits, N)
    CCadd_inverse(eng, circuit, c1, c2, qubits, a)
    qft_inverse(eng, circuit, qubits)
    circuit.apply_single_qubit_gate(Rx(np.pi), qubits[m])
    CNOT(eng, circuit, qubits[m], ancilla)
    circuit.apply_single_qubit_gate(Rx(np.pi), qubits[m])
    qft(eng, circuit, qubits)
    CCadd(eng, circuit, c1, c2, qubits, a)
