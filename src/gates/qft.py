import numpy as np
from projectq.meta import Dagger
from projectq.ops import H, CRz, X, Rz, Rx, R

from src.gates.rotate import calculate_phase
from src.topology.gates.gate_set import ISwap


def qft(eng, qubits):
    m = len(qubits)
    for i in range(m - 1, -1, -1):
        H | qubits[i]
        for j in range(2, i + 2):
            CRz(calculate_phase(j)) | (qubits[i - j + 1], qubits[i])


def qft2(eng, qubits):
    m = len(qubits)
    for i in range(m - 1, -1, -1):
        Rz(np.pi / 2) | qubits[i]
        Rx(np.pi / 2) | qubits[i]
        Rz(np.pi / 2) | qubits[i]
        for j in range(2, i + 2):
            Rz(-np.pi / 2) | qubits[i - j + 1]
            Rx(np.pi / 2) | qubits[i]
            Rz(np.pi / 2) | qubits[i]
            ISwap | (qubits[i - j + 1], qubits[i])
            Rx(np.pi / 2) | qubits[i - j + 1]
            ISwap | (qubits[i - j + 1], qubits[i])
            Rz(np.pi / 2) | qubits[i]

            R(-calculate_phase(i) / 4) | qubits[i]

            Rz(-np.pi / 2) | qubits[i - j + 1]
            Rx(np.pi / 2) | qubits[i]
            Rz(np.pi / 2) | qubits[i]
            ISwap | (qubits[i - j + 1], qubits[i])
            Rx(np.pi / 2) | qubits[i - j + 1]
            ISwap | (qubits[i - j + 1], qubits[i])
            Rz(np.pi / 2) | qubits[i]

            Rz(calculate_phase(i) / 4) | qubits[i - j + 1]
            Rz(calculate_phase(i) / 4) | qubits[i]


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
