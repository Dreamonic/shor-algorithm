import numpy as np
from projectq.meta import Dagger
from projectq.ops import Rz, Rx, R

from src.shared.rotate import calculate_phase
from src.topology.limited_gates.gate_set import ISwap


def qft(eng, circuit, qubits):
    m = len(qubits)
    for i in range(m - 1, -1, -1):
        circuit.apply_single_qubit_gate(Rz(np.pi / 2), qubits[i])
        circuit.apply_single_qubit_gate(Rx(np.pi / 2), qubits[i])
        circuit.apply_single_qubit_gate(Rz(np.pi / 2), qubits[i])
        for j in range(2, i + 2):
            circuit.apply_single_qubit_gate(Rz(-np.pi / 2), qubits[i - j + 1])
            circuit.apply_single_qubit_gate(Rx(np.pi / 2), qubits[i])
            circuit.apply_single_qubit_gate(Rz(np.pi / 2), qubits[i])
            circuit.apply_ld_two_qubit_gate(ISwap, qubits[i - j + 1], qubits[i])
            circuit.apply_single_qubit_gate(Rx(np.pi / 2), qubits[i - j + 1])
            circuit.apply_ld_two_qubit_gate(ISwap, qubits[i - j + 1], qubits[i])
            circuit.apply_single_qubit_gate(Rz(np.pi / 2), qubits[i])

            circuit.apply_single_qubit_gate(R(-calculate_phase(i) / 4), qubits[i])

            circuit.apply_single_qubit_gate(Rz(-np.pi / 2), qubits[i - j + 1])
            circuit.apply_single_qubit_gate(Rx(np.pi / 2), qubits[i])
            circuit.apply_single_qubit_gate(Rz(np.pi / 2), qubits[i])
            circuit.apply_ld_two_qubit_gate(ISwap, qubits[i - j + 1], qubits[i])
            circuit.apply_single_qubit_gate(Rx(np.pi / 2), qubits[i - j + 1])
            circuit.apply_ld_two_qubit_gate(ISwap, qubits[i - j + 1], qubits[i])
            circuit.apply_single_qubit_gate(Rz(np.pi / 2), qubits[i])

            circuit.apply_single_qubit_gate(Rz(calculate_phase(i) / 4), qubits[i - j + 1])
            circuit.apply_single_qubit_gate(Rz(calculate_phase(i) / 4), qubits[i])


def qft_inverse(eng, circuit, qubits):
    with Dagger(eng):
        qft(eng, circuit, qubits)
