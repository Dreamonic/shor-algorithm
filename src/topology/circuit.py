from copy import deepcopy

import numpy as np
from projectq.ops import Rx, Swap, Measure

from src.topology.circuit_qubit import BUS, LOGICAL, CircuitQubit
from src.topology.gates2.gate_set import ISwap


class Circuit:

    def __init__(self, graph=None):
        if graph is None:
            graph = dict()
        self.graph = graph
        self.bus_count = 0
        self.logical_count = 0
        self.gates_applied = 0
        self.single_applied = 0
        self.two_applied = 0

    def get_qubit_nodes(self):
        return list(self.graph.keys())

    def get_qubits(self):
        qubits = dict()
        for q in self.get_qubit_nodes():
            qubits[q.name] = q.qubit
        return qubits

    def get_all_qubits(self):
        bits = []
        for val in self.get_qubits().values():
            bits.append(val.qubit)

    def get_qubit_node(self, name):
        for q in self.get_qubit_nodes():
            if q.name == name:
                return q

    def get_qubit(self, name):
        for q in self.get_qubit_nodes():
            if q.name == name:
                return q.qubit

    def add_qubit(self, qubit):
        if qubit not in self.graph:
            self.graph[qubit] = set()
            if qubit.qubit.bit_type == BUS:
                self.bus_count += 1
            if qubit.qubit.bit_type == LOGICAL:
                self.logical_count += 1

    def add_edge(self, qubit1, qubit2, directed=0):
        if not self.is_valid_edge(qubit1, qubit2, directed):
            raise Exception("No valid edge can be inserted between " + str(qubit1) + " and " + str(qubit2))
        if qubit1 in self.graph:
            self.graph[qubit1].add(qubit2)
        else:
            self.graph[qubit1] = {qubit2}
        if not directed:
            self.add_edge(qubit2, qubit1, directed=1)

    def create_bus(self, engine, n):
        prev = None
        for i in range(n):
            bit = CircuitQubit(engine, bit_type=BUS)
            node = CircuitNode("bus_" + str(self.bus_count), bit)
            self.add_qubit(node)
            if prev is not None:
                self.add_edge(prev, node)
            prev = node

    def add_all_logicals(self, engine):
        new = []
        c = self.logical_count
        for q, neighbours in self.graph.items():
            if q.qubit.bit_type == BUS:
                logical = 2
                for n in neighbours:
                    if n.qubit.bit_type == LOGICAL:
                        logical -= 1
                for i in range(logical):
                    bit = CircuitQubit(engine, bit_type=LOGICAL)
                    node = CircuitNode("log_" + str(c), bit)
                    new.append((q, node))
                    c += 1
        for q, node in new:
            self.add_qubit(node)
            self.add_edge(q, node)

    def is_valid_edge(self, qubit1, qubit2, directed=0):
        valid = True
        if qubit1 in self.graph:
            neighbours = deepcopy(self.graph[qubit1])
            neighbours.add(qubit2)
            valid = valid and qubit1.check_neighbours(neighbours)
        if directed and qubit2 in self.graph:
            neighbours = deepcopy(self.graph[qubit2])
            neighbours.add(qubit1)
            valid = valid and qubit2.check_neighbours(neighbours)
        return valid

    def apply_single_qubit_gate(self, gate, name):
        self.gates_applied += 1
        self.single_applied += 1
        gate | self.qubit(name)

    def apply_two_qubit_gate(self, gate, name1, name2):
        self.gates_applied += 1
        self.two_applied += 1
        gate | self.qubit(name1, name2)

    def apply_ld_two_qubit_gate(self, gate, name1, name2):
        if self.get_qubit(name1).bit_type == BUS or self.get_qubit(name2).bit_type == BUS:
            raise Exception("Long distance two qubit gate operations can only be applied to logical qubits")
        node = self.get_qubit_node(name1)
        target = self.get_qubit_node(name2)
        bus_connection = list(self.graph[node])[0]

        path = self.find_shortest_path(bus_connection, target)
        self.swap_path(reversed(path))
        self.apply_two_qubit_gate(gate, name1, bus_connection.name)
        self.swap_path(path)

    def swap_path(self, path):
        prev = None
        for i in path:
            if prev is not None:
                self.swap(prev, i)
            prev = i

    def find_shortest_path(self, source, target):
        q = [[source]]
        while len(q) != 0:
            path = q.pop(0)
            cur = path[-1]
            if cur == target:
                return path

            for n in self.graph[cur]:
                new_path = list(path)
                new_path.append(n)
                q.append(new_path)

    def swap(self, node1, node2):
        self.gates_applied += 1
        self.two_applied += 1
        Swap | (node1.qubit.qubit, node2.qubit.qubit)

    def qubit(self, name1, name2=None):
        if name2 is None:
            return self.get_qubit(name1).qubit

        q1 = self.get_qubit_node(name1)
        q2 = self.get_qubit_node(name2)
        if q2 not in self.graph[q1]:
            raise Exception("Can only apply two qubit gates on neighbouring qubits.")
        else:
            return q1.qubit.qubit, q2.qubit.qubit

    def __str__(self):
        bus = ""
        logical = ""
        for q in self.get_qubit_nodes():
            n = list(self.graph[q])
            n.sort()
            if q.qubit.bit_type == BUS:
                bus += "\t" + str(q) + " : " + str(n) + "\n"
            if q.qubit.bit_type == LOGICAL:
                logical += "\t" + str(q) + " : " + str(n) + "\n"

        return "<CIRCUIT\n" + bus + logical + ">"

    def __del__(self):
        for node in self.graph.keys():
            Measure | node.qubit.qubit
            del node.qubit.qubit


class CircuitNode:

    def __init__(self, name, qubit):
        self.name = name
        self.qubit = qubit

    def max_neighbours(self):
        if self.qubit.bit_type == BUS:
            return 2, 2
        if self.qubit.bit_type == LOGICAL:
            return 1, 0

    def check_neighbours(self, neighbours):
        bus, logical = self.max_neighbours()
        for n in neighbours:
            if n.qubit.bit_type == BUS:
                bus -= 1
            if n.qubit.bit_type == LOGICAL:
                logical -= 1
        return bus >= 0 and logical >= 0

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.name == self.name
        return False

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return "<QUBIT=" + self.name + " : " + str(self.qubit.qubit) + ">"

    def __repr__(self):
        return "<QUBIT=" + self.name + " : " + str(self.qubit.qubit) + ">"


class FakeCircuit(Circuit):
    def __init__(self, graph=None):
        super().__init__(graph)

    def create_bus(self, engine, n):
        self.bus_count = n
        return

    def add_all_logicals(self, engine):
        for i in range(2 * self.bus_count):
            bit = CircuitQubit(engine, bit_type=LOGICAL)
            node = CircuitNode("log_" + str(i), bit)
            self.add_qubit(node)
        return

    def is_valid_edge(self, qubit1, qubit2, directed=0):
        return True

    def apply_single_qubit_gate(self, gate, name):
        self.gates_applied += 1
        self.single_applied += 1
        gate | self.qubit(name)

    def apply_two_qubit_gate(self, gate, name1, name2):
        self.gates_applied += 1
        self.two_applied += 1
        gate | self.qubit(name1, name2)

    def apply_ld_two_qubit_gate(self, gate, name1, name2):
        if self.get_qubit(name1).bit_type == BUS or self.get_qubit(name2).bit_type == BUS:
            raise Exception("Long distance two qubit gate operations can only be applied to logical qubits")
        self.apply_two_qubit_gate(gate, name1, name2)

    def qubit(self, name1, name2=None):
        if name2 is None:
            return self.get_qubit(name1).qubit

        q1 = self.get_qubit_node(name1)
        q2 = self.get_qubit_node(name2)
        return q1.qubit.qubit, q2.qubit.qubit

    def __str__(self):
        bus = ""
        logical = ""
        for q in self.get_qubit_nodes():
            n = list(self.graph[q])
            n.sort()
            if q.qubit.bit_type == BUS:
                bus += "\t" + str(q) + " : " + str(n) + "\n"
            if q.qubit.bit_type == LOGICAL:
                logical += "\t" + str(q) + " : " + str(n) + "\n"

        return "<CIRCUIT\n" + bus + logical + ">"


class AdvancedCircuit(Circuit):
    def swap(self, node1, node2):
        self.gates_applied += 6
        self.single_applied += 3
        self.two_applied += 3
        ISwap | (node1.qubit.qubit, node2.qubit.qubit)
        Rx(-np.pi / 2) | node2.qubit.qubit
        ISwap | (node1.qubit.qubit, node2.qubit.qubit)
        Rx(-np.pi / 2) | node1.qubit.qubit
        ISwap | (node1.qubit.qubit, node2.qubit.qubit)
        Rx(-np.pi / 2) | node2.qubit.qubit

# # qi_api = get_api_session()
# qi_engine, qi_backend = get_engine()
#
# circuit = Circuit()
# circuit.create_bus(qi_engine, 3)
# circuit.add_all_logicals(qi_engine)
# print(circuit)
# circuit.apply_single_qubit_gate(X, 'log_0')
# circuit.apply_ld_two_qubit_gate(Swap, 'log_0', 'log_5')
# circuit.apply_single_qubit_gate(Measure, 'log_5')
# print("The amount of gates applied is:", circuit.gates_applied)
# print("The measurement result is:", int(circuit.get_qubits()['log_5'].qubit[0]))
