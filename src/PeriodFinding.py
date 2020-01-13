"""
This example is copied from https://github.com/ProjectQ-Framework/ProjectQ
and is covered under the Apache 2.0 license.
"""
import os
from getpass import getpass

from projectq.backends import ResourceCounter
from projectq.ops import CNOT
from projectq.setups import restrictedgateset
from quantuminspire.api import QuantumInspireAPI
from quantuminspire.credentials import load_account, get_token_authentication, get_basic_authentication

from src.engines.pq_engine import get_engine
from src.quantum.period_finding import find_period_1, find_period_2

QI_EMAIL = os.getenv('QI_EMAIL')
QI_PASSWORD = os.getenv('QI_PASSWORD')
QI_URL = os.getenv('API_URL', 'https://api.quantum-inspire.com/')


def get_authentication():
    """ Gets the authentication for connecting to the Quantum Inspire API."""
    token = load_account()
    if token is not None:
        return get_token_authentication(token)
    else:
        if QI_EMAIL is None or QI_PASSWORD is None:
            print('Enter email:')
            email = input()
            print('Enter password')
            password = getpass()
        else:
            email, password = QI_EMAIL, QI_PASSWORD
        return get_basic_authentication(email, password)


#
# def run_shor(eng, N, a, verbose=False):
#     """
#     Runs the quantum subroutine of Shor's algorithm for factoring.
#     Args:
#         eng (MainEngine): Main compiler engine to use.
#         N (int): Number to factor.
#         a (int): Relative prime to use as a base for a^x mod N.
#         verbose (bool): If True, display intermediate measurement results.
#     Returns:
#         r (float): Potential period of a.
#     """
#     n = int(math.ceil(math.log(N, 2)))
#
#     x = eng.allocate_qureg(n)
#
#     # X | x[0]
#
#     measurements = [0] * (2 * n)  # will hold the 2n measurement results
#
#     ctrl_qubit = eng.allocate_qubit()
#
#     for k in range(2 * n):
#         current_a = pow(a, 1 << (2 * n - 1 - k), N)
#         # one iteration of 1-qubit QPE
#         H | ctrl_qubit
#         with Control(eng, ctrl_qubit):
#             MultiplyByConstantModN(current_a, N) | x
#
#         # perform inverse QFT --> Rotations conditioned on previous outcomes
#         for i in range(k):
#             if measurements[i]:
#                 R(-math.pi / (1 << (k - i))) | ctrl_qubit
#         H | ctrl_qubit
#
#         # and measure
#         Measure | ctrl_qubit
#         eng.flush()
#         measurements[k] = int(ctrl_qubit)
#         if measurements[k]:
#             X | ctrl_qubit
#
#         if verbose:
#             print("\033[95m{}\033[0m".format(measurements[k]), end="")
#             sys.stdout.flush()
#
#     # All(Measure) | x
#     # turn the measured values into a number in [0,1)
#     y = sum([(measurements[2 * n - 1 - i] * 1. / (1 << (i + 1)))
#              for i in range(2 * n)])
#
#     # continued fraction expansion to get denominator (the period?)
#     r = Fraction(y).limit_denominator(N - 1).denominator
#
#     print("\tperiod:", r)
#
#     # return the (potential) period
#     return r
#
# if __name__ == "__main__":
#
#     # make the compiler and run the circuit on the simulator backend
#     eng, _ = get_engine()
#
#     # print welcome message and ask the user for the number to factor
#     print("\n\t\033[37mprojectq\033[0m\n\t--------\n\tImplementation of Shor"
#           "\'s algorithm.", end="")
#     N = int(input('\n\tNumber to factor: '))
#     print("\n\tFactoring N = {}: \033[0m".format(N), end="")
#
#     # choose a base at random:
#     a = int(numpy.random.randint(2, N))
#     print("Using a =", a)
#     if not numpy.gcd(a, N) == 1:
#         print("\n\n\t\033[92mOoops, we were lucky: Chose non relative prime"
#               " by accident :)")
#         print("\tFactor: {}\033[0m".format(numpy.gcd(a, N)))
#     else:
#         # run the quantum subroutine
#         r = run_shor(eng, N, a, True)
#
#         # try to determine the factors
#         if r % 2 != 0:
#             r *= 2
#         apowrhalf = pow(a, r >> 1, N)
#         f1 = numpy.gcd(apowrhalf + 1, N)
#         f2 = numpy.gcd(apowrhalf - 1, N)
#         if ((not f1 * f2 == N) and f1 * f2 > 1 and
#                 int(1. * N / (f1 * f2)) * f1 * f2 == N):
#             f1, f2 = f1*f2, int(N/(f1*f2))
#         if f1 * f2 == N and f1 > 1 and f2 > 1:
#             print("\n\n\t\033[92mFactors found :-) : {} * {} = {}\033[0m"
#                   .format(f1, f2, N))
#         else:
#             print("\n\n\t\033[91mBad luck: Found {} and {}\033[0m".format(f1,
#                                                                           f2))

# print(resource_counter)  # print resource usage

if __name__ == '__main__':
    name = 'TestProjectQ'
    authentication = get_authentication()
    qi_api = QuantumInspireAPI(QI_URL, authentication, project_name=name)

    compiler_engines = restrictedgateset.get_engine_list(one_qubit_gates="any", two_qubit_gates=(CNOT,))
    compiler_engines.extend([ResourceCounter()])

    engine, qi_backend = get_engine(qi_api)

    # X, CNOT, H, Measure, All
    N = 15

    find_period_2(engine, N)

    #              for i in range(2 * n)])
    # print('Probabilities {0}'.format(qi_backend.get_probabilities(qubits)))
