import projectq
from projectq import MainEngine
from projectq.backends import ResourceCounter, Simulator
from projectq.cengines import DecompositionRuleSet, AutoReplacer, InstructionFilter, TagRemover, LocalOptimizer
from projectq.ops import BasicMathGate, get_inverse, QFT, Swap
from projectq.setups import restrictedgateset


def high_level_gates(eng, cmd):
    g = cmd.gate
    if g == QFT or get_inverse(g) == QFT or g == Swap:
        return True
    if isinstance(g, BasicMathGate):
        return False
        if isinstance(g, AddConstant):
            return True
        elif isinstance(g, AddConstantModN):
            return True
        return False
    return eng.next_engine.is_available(cmd)


def get_engine(api=None):
    resource_counter = ResourceCounter()
    rule_set = DecompositionRuleSet(modules=[projectq.libs.math,
                                             projectq.setups.decompositions])
    compilerengines = [AutoReplacer(rule_set),
                       InstructionFilter(high_level_gates),
                       TagRemover(),
                       LocalOptimizer(3),
                       AutoReplacer(rule_set),
                       TagRemover(),
                       LocalOptimizer(3),
                       resource_counter]

    # make the compiler and run the circuit on the simulator backend
    return MainEngine(Simulator(), compilerengines), None
