BUS = 0
LOGICAL = 1


class CircuitQubit:

    def __init__(self, engine, bit_type=BUS):
        self.qubit = engine.allocate_qubit()
        self.bit_type = bit_type

