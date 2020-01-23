from projectq.meta import Dagger
from projectq.ops import Rz, CNOT, X, CRz, CX

from src.topology.all_gates.qft import qft, qft_inverse
from src.topology.all_gates.rotate import calculate_phase


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
                circuit.apply_ld_two_qubit_gate(CRz(calculate_phase(i)), c, qubits[n])


def Cadd_inverse(eng, circuit, c, qubits, value):
    with Dagger(eng):
        Cadd(eng, circuit, c, qubits, value)


def CCRz(eng, circuit, c1, c2, qubit, angle):
    circuit.apply_ld_two_qubit_gate(CRz(angle / 2), c1, qubit)
    circuit.apply_ld_two_qubit_gate(CX, c2, c1)
    circuit.apply_ld_two_qubit_gate(CRz(-angle / 2), c1, qubit)
    circuit.apply_ld_two_qubit_gate(CX, c2, c1)
    circuit.apply_ld_two_qubit_gate(CRz(angle / 2), c2, qubit)


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
    circuit.apply_ld_two_qubit_gate(CNOT, qubits[m], ancilla)
    qft(eng, circuit, qubits)
    Cadd(eng, circuit, ancilla, qubits, N)
    CCadd_inverse(eng, circuit, c1, c2, qubits, a)
    qft_inverse(eng, circuit, qubits)
    circuit.apply_single_qubit_gate(X, qubits[m])
    circuit.apply_ld_two_qubit_gate(CNOT, qubits[m], ancilla)
    circuit.apply_single_qubit_gate(X, qubits[m])
    qft(eng, circuit, qubits)
    CCadd(eng, circuit, c1, c2, qubits, a)
