from abc import ABC, abstractmethod
from enum import Enum


class QubitType(Enum):
    NO_TYPE = "qubit_type.no_type"
    BUS = "qubit_type.bus"
    LOGICAL = "qubit_type.logical"


class QubitHandler(ABC):

    @abstractmethod
    def execute(self, **kwargs):
        pass
