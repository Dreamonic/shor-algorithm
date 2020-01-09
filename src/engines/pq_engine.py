from projectq import MainEngine
from projectq.backends import ResourceCounter, Simulator
from projectq.ops import CNOT, CZ
from projectq.setups import restrictedgateset


def get_engine(api=None):
    compiler_engines = restrictedgateset.get_engine_list(one_qubit_gates="any", two_qubit_gates=(CNOT, CZ))
    compiler_engines.append(ResourceCounter())
    return MainEngine(Simulator(), compiler_engines)
