import io
import sys
import tkinter as tk
import uuid

import numpy as np
from projectq import MainEngine
from projectq.backends import CommandPrinter
from projectq.ops import X, Rz

from src.classical import shor
from src.gui.circuit import CircuitGui
from src.gui.circuit_mapper import get_mapping, get_reg_to_coordinate_mapping, InstructionReducer, QubitController
from src.topology.all_gates.multiply import CMultModN
from src.topology.circuit import AdvancedCircuit, FakeCircuit, Circuit
from src.topology.parallel_gates.prepare_number import prepare_number
from src.topology.parallel_gates.rotate import calculate_phase
from src.topology.parallel_gates.simple import H

cache_file = None
max_instructions = 0


def callback(text, instr, controller):
    def f():
        controller.clean_up()
        text.delete(1.0, tk.END)
        next_instruction = instr.next()
        text.insert(tk.END, next_instruction)
        controller.execute_instr(next_instruction)

    return f


def timer_callback(text, instr, controller):
    controller.clean_up()
    text.delete(1.0, tk.END)
    next_instruction = instr.next()
    text.insert(tk.END, next_instruction)
    try:
        controller.execute_instr(next_instruction)
    except IndexError:
        pass


def close():
    exit(0)


def capture_output_mod(circuit, qi_engine, a, nx, N, n):
    _stdout = sys.stdout
    sys.stdout = io.StringIO()

    qubits = [("log_" + str(i)) for i in range(n + 1)]
    x = [("log_" + str(i)) for i in range(n + 1, 2 * n + 1)]
    c = "log_" + str(2 * n + 1)
    ancilla = "log_" + str(2 * n + 2)

    circuit.apply_single_qubit_gate(X, c)

    prepare_number(qi_engine, circuit, x, nx)

    CMultModN(qi_engine, circuit, c, x, qubits, ancilla, a, N)

    output = sys.stdout.getvalue()
    sys.stdout = _stdout

    return output


def capture_output(circuit, qi_engine, a, nx, N, n):
    _stdout = sys.stdout
    sys.stdout = io.StringIO()

    x = [("log_" + str(i)) for i in range(n)]
    b = [("log_" + str(i)) for i in range(n, 2 * n + 1)]
    c = "log_" + str(2 * n + 1)
    ancilla = "log_" + str(2 * n + 2)
    measurements = [0] * (2 * n)

    circuit.apply_single_qubit_gate(X, x[0])

    for i in range(2 * n):
        print("C", i)
        circuit.apply_single_qubit_gate(X, c)
        CMultModN(qi_engine, circuit, c, x, b, ancilla, pow(a, 2 ** i), N)

        for j in range(i):
            if measurements[j]:
                circuit.apply_single_qubit_gate(Rz(-calculate_phase(i - j)), c)
        H(qi_engine, circuit, c)

    output = sys.stdout.getvalue()
    sys.stdout = _stdout

    return output


if __name__ == '__main__':

    N = 15
    n = int(np.ceil(np.log2(N)))

    a = shor.find_co_prime_stochastic(N)
    if a < 0:
        print("Factor is", -a)
        exit(0)
    print("a =", a)
    nx = n + 1

    circuit_backend = CommandPrinter()
    qi_engine = MainEngine(circuit_backend)

    circuit = Circuit()
    circuit.create_bus(qi_engine, n + 2)
    circuit.add_all_logicals(qi_engine)

    output = None
    if cache_file is None:
        output = capture_output_mod(circuit, qi_engine, a, nx, N, n)
        f = open("../../cached/" + str(uuid.uuid4()) + ".cache", "w+")
        f.write(output)
        f.close()
        print("Amount of gate operations:", circuit.gates_applied)
        print("Amount of single gate operations:", circuit.single_applied)
        print("Amount of two qubit operations:", circuit.two_applied)
        print("Estimated amount of time (ns):", circuit.single_applied + circuit.two_applied * 10)
    else:
        f = open("../../cached/" + cache_file + ".cache", "r")
        output = f.read()
        f.close()
    instr = InstructionReducer(output)

    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', close)  # root is your root window
    canvas = tk.Canvas(root, width=600, height=600, borderwidth=0, highlightthickness=0)

    circuit_gui = CircuitGui(canvas)
    circuit_gui.draw_circle_grid(x=40, y=40, x_count=3, y_count=n + 2, width=600, height=600, r=20)
    circuit_gui.bus_line_connections(width=3)

    ls = get_mapping(str(circuit))
    mapping = get_reg_to_coordinate_mapping(ls)

    controller = QubitController(circuit_gui, mapping)

    text = tk.Text(canvas, height=2, width=40)
    button = tk.Button(canvas, text="NEXT INSTRUCTION", command=callback(text, instr, controller))
    canvas.create_window(100, 20, window=button)
    canvas.create_window(400, 20, window=text)

    canvas.grid()
    for i in range(len(instr)):
        root.after(100 * i, lambda: timer_callback(text, instr, controller))
        if max_instructions != 0 and i > max_instructions:
            break

    root.mainloop()
