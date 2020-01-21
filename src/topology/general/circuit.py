from abc import abstractmethod
from copy import deepcopy

from src.topology.general.qubit import QubitType, QubitHandler


class Statistics:
    TOTAL_GATES = "gates_applied"
    SINGLE_GATES = "single_gates_applied"
    TWO_GATES = "two_gates_applied"

    def __init__(self):
        self.stats = dict()
        self._default_stats()

    def _default_stats(self):
        self.stats[self.TOTAL_GATES] = 0
        self.stats[self.SINGLE_GATES] = 0
        self.stats[self.TWO_GATES] = 0

    def add_stat(self, name: str):
        self.stats[name] = 0

    def increment_stat(self, name: str):
        self.stats[name] += 1

    def should_track(self, name: str) -> bool:
        return self.stats[name] is not None


class Restrictions:
    def __init__(self):
        self.max_neighbours = dict()
        self.available_gates = dict()

    def get_max_neighbours(self, qubit_type: QubitType):
        return self.max_neighbours[qubit_type]

    def get_available_gates(self, qubit_type: QubitType):
        return self.available_gates[qubit_type]


class QubitCounter(QubitHandler):

    def execute(self, stats: Statistics = None, qubit_type: QubitType = QubitType.NO_TYPE, **kwargs):
        if stats is None:
            return
        if stats.should_track(qubit_type.value):
            stats.increment_stat(qubit_type.value)


class GateCounter(QubitHandler):

    def execute(self, stats: Statistics = None, single_gate_amount: int = 0, two_gate_amount: int = 0, **kwargs):
        if stats is None:
            return
        stats.stats[Statistics.TOTAL_GATES] += single_gate_amount + two_gate_amount
        stats.stats[Statistics.SINGLE_GATES] += single_gate_amount
        stats.stats[Statistics.TWO_GATES] += two_gate_amount


class Node:
    def __init__(self, name: str, qubit, qubit_type: QubitType = QubitType.NO_TYPE, restrictions: Restrictions = None):
        if restrictions is None:
            restrictions = Restrictions()
        self.name = name
        self.qubit = qubit
        self.qubit_type = qubit_type
        self.restrictions = restrictions

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.name == self.name
        return False

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return "<QUBIT=" + self.name + " : " + str(self.qubit) + ">"

    def __repr__(self):
        return "<QUBIT=" + self.name + " : " + str(self.qubit) + ">"


class LongDistanceAlgorithm:
    @abstractmethod
    def prepare(self, circuit, src, tgt, **kwargs):
        raise Exception("No long distance algorithm implemented.")

    @abstractmethod
    def teardown(self, circuit, src, tgt, **kwargs):
        raise Exception("No long distance algorithm implemented.")


class Circuit:
    def __init__(self, graph: dict = None, stats: Statistics = None, restrictions: Restrictions = None,
                 handlers: [QubitHandler] = None, ld_gate_algorithm=None):
        if graph is None:
            graph = dict()
        self.graph = graph
        if stats is None:
            stats = Statistics()
        self.stats = stats
        if restrictions is None:
            restrictions = Restrictions()
        self.restrictions = restrictions
        if handlers is None:
            handlers = []
        self.handlers = handlers
        if ld_gate_algorithm is None:
            ld_gate_algorithm = LongDistanceAlgorithm()
        self.ld_gate_algorithm = ld_gate_algorithm

        self.stats.add_stat(QubitType.BUS.value)
        self.stats.add_stat(QubitType.LOGICAL.value)

        self.logical_map = dict()

    def add_node(self, node: Node):
        if node not in self.graph:
            self.graph[node] = set()
            if node.qubit_type == QubitType.LOGICAL:
                self.logical_map[len(self.logical_map)] = node
            for handler in self.handlers:
                handler.execute(stats=self.stats, qubit_type=node.qubit_type)

    def add_edge(self, node1: Node, node2: Node, directed: int = 0):
        if not self.is_valid_edge(node1, node2, directed):
            raise Exception("No valid edge can be inserted between " + str(node1) + " and " + str(node2))
        if node1 in self.graph:
            self.graph[node1].add(node2)
        else:
            self.graph[node1] = {node2}
        if not directed:
            self.add_edge(node2, node1, directed=1)

    def is_valid_edge(self, qubit1: Node, qubit2: Node, directed: int = 0):
        valid = True
        if qubit1 in self.graph:
            neighbours = deepcopy(self.graph[qubit1])
            neighbours.add(qubit2)
            valid = valid and self.check_neighbours(qubit1, neighbours)
        if directed and qubit2 in self.graph:
            neighbours = deepcopy(self.graph[qubit2])
            neighbours.add(qubit1)
            valid = valid and self.check_neighbours(qubit2, neighbours)
        return valid

    def check_neighbours(self, node: Node, neighbours: [Node]):
        bus = self.restrictions.get_max_neighbours(node.qubit_type)[QubitType.BUS]
        logical = self.restrictions.get_max_neighbours(node.qubit_type)[QubitType.LOGICAL]
        for n in neighbours:
            if n.qubit_type == QubitType.BUS:
                bus -= 1
            if n.qubit_type == QubitType.LOGICAL:
                logical -= 1
        return bus >= 0 and logical >= 0

    def apply_single_qubit_gate(self, gate, name):
        if gate not in self.restrictions.available_gates:
            raise Exception("Gate" + str(gate) + "is not part of available set")
        gate | self.qubit(name)
        for handler in self.handlers:
            handler.execute(single_gate_amount=1, two_gate_amount=0)

    def apply_two_qubit_gate(self, gate, name1, name2):
        q1 = self.node(name1)
        q2 = self.node(name2)
        if q2 not in self.graph[q1]:
            raise Exception("Can only apply two qubit gates on neighbouring qubits.")
        else:
            if gate not in self.restrictions.available_gates:
                raise Exception("Gate" + str(gate) + "is not part of available set")
            gate | self.qubit(name1), self.qubit(name2)
            for handler in self.handlers:
                handler.execute(single_gate_amount=0, two_gate_amount=1)

    def apply_ld_two_qubit_gate(self, gate, name1, name2):
        node = self.node(name1)
        target = self.node(name2)

        self.ld_gate_algorithm.prepare(self, node, target)
        self.apply_two_qubit_gate(gate, name1, name2)
        self.ld_gate_algorithm.teardown(self, node, target)

    def node(self, name):
        for q in self.get_nodes():
            if q.name == name:
                return q

    def qubit(self, name):
        for q in self.get_nodes():
            if q.name == name:
                return q.qubit

    def get_nodes(self):
        return list(self.graph.keys())
