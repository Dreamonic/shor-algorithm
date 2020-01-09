from projectq import MainEngine
from projectq.backends import ResourceCounter
from projectq.ops import CNOT, CZ, Toffoli
from projectq.setups import restrictedgateset
from quantuminspire.projectq.backend_qx import QIBackend


def get_engine(api=None):
    compiler_engines = restrictedgateset.get_engine_list(one_qubit_gates="any", two_qubit_gates=(CNOT, CZ, Toffoli))
    compiler_engines.extend([ResourceCounter()])
    qi_backend = QIBackend(quantum_inspire_api=api)
    return MainEngine(backend=qi_backend, engine_list=compiler_engines), qi_backend
