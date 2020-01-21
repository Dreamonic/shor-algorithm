import re


def get_mapping(mapping):
    res = {}
    for line in mapping.split("\n")[1:-1]:
        line = re.search(r'<(.*?)>', line)
        bit, reg = line.group(1).split(" : ")
        res[bit[6:]] = reg
    return res


def get_reg_to_coordinate_mapping(mapping):
    res = {}
    for bit_name, reg in mapping.items():
        group = re.match(r'bus_(.+)', bit_name)
        if group is not None:
            res[reg] = 1, int(group.group(1))
        group = re.match(r'log_(.+)', bit_name)
        if group is not None:
            idx = int(group.group(1))
            res[reg] = (idx % 2) * 2, int(idx / 2)
    return res


class QubitController:

    def __init__(self, circuit, mapping):
        self.qubits = circuit
        self.mapping = mapping
        self.active = []

    def execute_instr(self, string):
        qubits = string.split("|")[1]
        group = re.search(r"\((.+), (.+)\)", qubits)
        if group is not None:
            x1, y1 = self.mapping[str(group.group(1)).strip()]
            x2, y2 = self.mapping[str(group.group(2)).strip()]
            self.qubits.set_active(x1, y1, active_color="dodger blue")
            self.qubits.set_active(x2, y2, active_color="deep sky blue")
            self.active.append((x1, y1))
            self.active.append((x2, y2))
        else:
            group = re.search(r"(.+)", qubits)
            if group is not None:
                x1, y1 = self.mapping[str(group.group(1)).strip()]
                self.qubits.set_active(x1, y1)
                self.active.append((x1, y1))

    def clean_up(self):
        for x, y in self.active:
            self.qubits.set_inactive(x, y)
        self.active = []


class InstructionReducer:

    def __init__(self, instructions):
        self.instructions = instructions
        self.index = -1

    def next(self):
        self.index += 1
        while self.should_skip(self.instructions.split("\n")[self.index]):
            pass
        return self.instructions.split("\n")[self.index]

    def should_skip(self, instruction):
        if "Allocate" in instruction:
            self.index += 1
            return True
        if "Deallocate" in instruction:
            self.index += 1
            return True
        return False

    def __len__(self):
        count = 0
        for i in self.instructions.split("\n"):
            if not self.should_skip(i):
                count += 1
        return count
