from math import ceil

from projectq.ops import Swap

from src.topology.general.circuit import Circuit, LongDistanceAlgorithm, Statistics, Restrictions, Node
from src.topology.general.qubit import QubitHandler, QubitType


class BusSwap(LongDistanceAlgorithm):

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


class BusCircuit(Circuit):
    def __init__(self, engine, n, graph: dict = None, stats: Statistics = None, restrictions: Restrictions = None,
                 handlers: [QubitHandler] = None, ld_gate_algorithm=None):
        super().__init__(graph=graph, stats=stats, restrictions=restrictions, handlers=handlers,
                         ld_gate_algorithm=ld_gate_algorithm)

        self.create_bus_line(engine, ceil(n / 2))
        self.add_all_logicals(engine)

    def create_bus_line(self, engine, n):
        prev = None
        for i in range(n):
            node = Node("bus_" + str(i), engine.allocate_qubit(), QubitType.BUS, restrictions=self.restrictions)
            self.add_node(node)
            if prev is not None:
                self.add_edge(prev, node)
            prev = node

    def add_all_logicals(self, engine):
        new = []
        c = self.stats.stats[QubitType.LOGICAL.value]
        for q, neighbours in self.graph.items():
            if q.qubit_type == QubitType.BUS:
                logical = self.restrictions.get_max_neighbours(QubitType.BUS)[QubitType.LOGICAL]
                for n in neighbours:
                    if n.qubit_type == QubitType.LOGICAL:
                        logical -= 1
                for i in range(logical):
                    node = Node("log_" + str(c), engine.allocate_qubit(), QubitType.LOGICAL,
                                restrictions=self.restrictions)
                    new.append((q, node))
                    c += 1
        for q, node in new:
            self.add_node(node)
            self.add_edge(q, node)
