from src.engines.pq_engine import get_engine
from src.topology.general.circuit import QubitCounter, Statistics, Restrictions, GateCounter
from src.topology.general.nn_circuit import GridCircuit
from src.topology.general.qubit import QubitType

qc = QubitCounter()
gc = GateCounter()
stats = Statistics()
rest = Restrictions()

rest.max_neighbours[QubitType.BUS] = {
    QubitType.NO_TYPE: 0,
    QubitType.BUS: 2,
    QubitType.LOGICAL: 2,
}

rest.max_neighbours[QubitType.LOGICAL] = {
    QubitType.NO_TYPE: 0,
    QubitType.BUS: 1,
    QubitType.LOGICAL: 4,
}

qi_engine, qi_backend = get_engine()

circuit = GridCircuit(qi_engine, 9, stats=stats, restrictions=rest, handlers=[qc, gc])
print(circuit.logical_map)
