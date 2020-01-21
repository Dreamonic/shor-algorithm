from math import ceil, sqrt

from projectq.ops import Swap

from src.topology.general.circuit import Circuit, LongDistanceAlgorithm, Statistics, Restrictions, Node
from src.topology.general.qubit import QubitHandler, QubitType


class GridSwap(LongDistanceAlgorithm):

    def prepare(self, circuit, src, tgt, **kwargs):
        path = self.find_shortest_path(circuit, src, tgt)
        self.swap_path(circuit, path)

    def teardown(self, circuit, src, tgt, **kwargs):
        path = self.find_shortest_path(circuit, src, tgt)
        self.swap_path(circuit, reversed(path))

    def find_shortest_path(self, circuit, src, tgt):
        q = [[src]]
        while len(q) != 0:
            path = q.pop(0)
            cur = path[-1]
            if cur == tgt:
                return path

            for n in circuit.graph[cur]:
                new_path = list(path)
                new_path.append(n)
                q.append(new_path)

    def swap_path(self, circuit, path):
        prev = None
        for i in path:
            if prev is not None:
                circuit.apply_two_qubit_gate(Swap, prev.name, i.name)
                self.swap(prev, i)
            prev = i


class GridCircuit(Circuit):
    def __init__(self, engine, n, graph: dict = None, stats: Statistics = None, restrictions: Restrictions = None,
                 handlers: [QubitHandler] = None, ld_gate_algorithm=None):
        super().__init__(graph=graph, stats=stats, restrictions=restrictions, handlers=handlers,
                         ld_gate_algorithm=ld_gate_algorithm)

        self.create_grid(engine, ceil(sqrt(n)), ceil(n / sqrt(n)))
        self.add_edges(ceil(sqrt(n)), ceil(n / sqrt(n)))

    def create_grid(self, engine, x, y):
        for idx in range(x):
            for idy in range(y):
                node = Node("log_" + str(idx) + "_" + str(idy), engine.allocate_qubit(), QubitType.LOGICAL,
                            restrictions=self.restrictions)
                self.add_node(node)

    def add_edges(self, x, y):
        for idx in range(1, x - 1):
            for idy in range(0, y):
                self.add_edge(self.node("log_" + str(idx) + "_" + str(idy)),
                              self.node("log_" + str(idx - 1) + "_" + str(idy)))
                self.add_edge(self.node("log_" + str(idx) + "_" + str(idy)),
                              self.node("log_" + str(idx + 1) + "_" + str(idy)))
        for idx in range(0, x):
            for idy in range(1, y - 1):
                self.add_edge(self.node("log_" + str(idx) + "_" + str(idy)),
                              self.node("log_" + str(idx) + "_" + str(idy - 1)))
                self.add_edge(self.node("log_" + str(idx) + "_" + str(idy)),
                              self.node("log_" + str(idx) + "_" + str(idy + 1)))
