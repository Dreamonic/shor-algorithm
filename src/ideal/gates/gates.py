from projectq.meta import Control, Dagger
from projectq.ops import Rz, CNOT, X, Swap

from src.ideal.gates.qft import qft, qft_inverse
from src.shared.rotate import calculate_phase
from src.util.math import modinv


def add(eng, qubits, value):
    """
    Adder gate which adds a classical value to a quantum value.
    :param eng: The engine used for computations.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param value: The classical value which should be added.
    """
    length = len(qubits)
    # Perform addition for every qubit
    for n in range(length - 1, -1, -1):
        # Perform addition for every classical bit
        for i in range(1, n + 2):
            ctrl = value & (1 << (n - i + 1))
            # Only perform the addition 1 should be added to the qubit,
            # else keep the original state
            if ctrl > 0:
                Rz(calculate_phase(i)) | qubits[n]


def add_inverse(eng, qubits, value):
    """
    The inverse adder gate, which effectively performs a subtraction of the classical value.
    :param eng: The engine used for computations.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param value: The classical value which should be subtracted.
    """
    with Dagger(eng):
        add(eng, qubits, value)


def Cadd(eng, c, qubits, value):
    """
    Similar to the adder gate which adds a classical value to a quantum value.
    However, this gate is controlled by a qubit c.
    :param eng: The engine used for computations.
    :param c: The qubit control of the gate.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param value: The classical value which should be added.
    """
    with Control(eng, c):
        add(eng, qubits, value)


def Cadd_inverse(eng, c, qubits, value):
    """
    Similar to the inverse adder gate, which effectively performs a subtraction of the classical value.
    However, this gate is controlled by a qubit c.
    :param eng: The engine used for computations.
    :param c: The qubit control of the gate.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param value: The classical value which should be subtracted.
    """
    with Dagger(eng):
        Cadd(eng, c, qubits, value)


def CCadd(eng, c1, c2, qubits, value):
    """
    Similar to the adder gate which adds a classical value to a quantum value.
    However, this gate is controlled by two qubits c1 and c2.
    :param eng: The engine used for computations.
    :param c1: A qubit control of the gate.
    :param c2: A qubit control of the gate.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param value: The classical value which should be added.
    """
    with Control(eng, c1):
        Cadd(eng, c2, qubits, value)


def CCadd_inverse(eng, c1, c2, qubits, value):
    """
    Similar to the inverse adder gate, which effectively performs a subtraction of the classical value.
    However, this gate is controlled by two qubits c1 and c2.
    :param eng: The engine used for computations.
    :param c1: A qubit control of the gate.
    :param c2: A qubit control of the gate.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param value: The classical value which should be subtracted.
    """
    with Dagger(eng):
        CCadd(eng, c1, c2, qubits, value)


def addModN(eng, c1, c2, qubits, ancilla, a, N):
    """
    This gate performs the operation (a + b)mod(N), where b is stored in the qubits and a is a classical value.
    :param eng: The engine used for computations.
    :param c1: A qubit control of the gate.
    :param c2: A qubit control of the gate.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param ancilla: This is needed to check for overflows.
    :param a: The classical value 'a' which is used in (a + b)mod(N).
    :param N: The number to be factored into primes.
    """
    m = len(qubits) - 1

    # Perform a + b - N.
    CCadd(eng, c1, c2, qubits, a)
    add_inverse(eng, qubits, N)

    # Check if there is an underflow.
    qft_inverse(eng, qubits)
    CNOT | (qubits[m], ancilla)
    qft(eng, qubits)

    # Reset to its original state if there was an underflow,
    # else subtract a
    Cadd(eng, ancilla, qubits, N)
    CCadd_inverse(eng, c1, c2, qubits, a)

    # Reset the ancilla back to its original state.
    qft_inverse(eng, qubits)
    X | qubits[m]
    CNOT | (qubits[m], ancilla)
    X | qubits[m]
    qft(eng, qubits)

    # Finally add 'a', to get the result of (a + b)modN.
    CCadd(eng, c1, c2, qubits, a)


def _CMultModN(eng, c, x, qubits, ancilla, a, N):
    n = len(x)

    qft(eng, qubits)
    for i in range(n):
        addModN(eng, c, x[i], qubits, ancilla, (2 ** i) * a % N, N)
    qft_inverse(eng, qubits)


def CMultModN(eng, c, x, qubits, ancilla, a, N):
    """
    This gate performs the operation (ax)mod(N), where x is stored in the qubits and a is a classical value.
    This gate also has a control.
    :param eng: The engine used for computations.
    :param c: A qubit control of the gate.
    :param qubits: The qubits representing the quantum value (superposition of classical values).
    :param ancilla: This is needed to check for overflows.
    :param a: The classical value 'a' which is used in (a + b)mod(N).
    :param N: The number to be factored into primes.
    """
    n = len(x)
    _CMultModN(eng, c, x, qubits, ancilla, a, N)
    for i in range(n):
        Swap | (x[i], qubits[i])
    # All(Swap) | zip(x, qubits)
    with Dagger(eng):
        _CMultModN(eng, c, x, qubits, ancilla, modinv(a, N), N)
