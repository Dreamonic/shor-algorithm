import numpy as np
from projectq.ops import SelfInverseGate


class ISwapGate(SelfInverseGate):

    def __init__(self):
        SelfInverseGate.__init__(self)
        self.interchangeable_qubit_indices = [[0, 1]]

    def __str__(self):
        return "iSwap"

    @property
    def matrix(self):
        return np.matrix([[1, 0, 0, 0],
                          [0, 0, 1j, 0],
                          [0, 1j, 0, 0],
                          [0, 0, 0, 1]])


ISwap = ISwapGate()

