import numpy as np
from projectq import ops
from projectq.ops import Rz, Rx, R

from src.topology.limited_gates.gate_set import ISwap


def CNOT(eng, circuit, b1, b2):
    circuit.apply_single_qubit_gate(Rz(-np.pi / 2), b1)
    circuit.apply_single_qubit_gate(Rx(np.pi / 2), b2)
    circuit.apply_single_qubit_gate(Rz(np.pi / 2), b2)
    circuit.apply_ld_two_qubit_gate(ISwap, b1, b2)
    circuit.apply_single_qubit_gate(Rx(np.pi / 2), b1)
    circuit.apply_ld_two_qubit_gate(ISwap, b1, b2)
    circuit.apply_single_qubit_gate(Rz(np.pi / 2), b2)


def CRz(eng, circuit, b1, b2, angle):
    CNOT(eng, circuit, b1, b2)
    circuit.apply_single_qubit_gate(R(-angle / 4), b2)
    CNOT(eng, circuit, b1, b2)
    circuit.apply_single_qubit_gate(R(angle / 4), b1)
    circuit.apply_single_qubit_gate(R(angle / 4), b2)


def H(eng, circuit, b):
    circuit.apply_single_qubit_gate(Rz(np.pi / 2), b)
    circuit.apply_single_qubit_gate(Rx(np.pi / 2), b)
    circuit.apply_single_qubit_gate(Rz(np.pi / 2), b)


def Swap(eng, circuit, b1, b2):
    # circuit.apply_ld_two_qubit_gate(ops.Swap, b1, b2)
    circuit.apply_ld_two_qubit_gate(ISwap, b1, b2)
    circuit.apply_single_qubit_gate(Rx(-np.pi / 2), b2)
    circuit.apply_ld_two_qubit_gate(ISwap, b1, b2)
    circuit.apply_single_qubit_gate(Rx(-np.pi / 2), b1)
    circuit.apply_ld_two_qubit_gate(ISwap, b1, b2)
    circuit.apply_single_qubit_gate(Rx(-np.pi / 2), b2)
