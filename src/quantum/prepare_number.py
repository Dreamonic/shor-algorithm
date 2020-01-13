import numpy as np
from projectq.ops import X


def prepare_number(eng, qubits, number):
    if np.ceil(np.log2(number)) > len(qubits):
        raise Exception("Not enough qubits to represent " + number)

    for i in range(len(qubits)):
        if (number & (1 << i)) > 0:
            X | qubits[i]
