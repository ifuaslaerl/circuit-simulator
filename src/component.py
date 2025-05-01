import abc
import typing
import numpy as np

class Component:

    def __init__(self, terminals: typing.List[str]) -> None:
        self.terminals: typing.List[str] = terminals
        self.s: complex = 0
        self.active: bool = False

    def set_s(self, s: complex) -> None:
        self.s: complex = s

    @abc.abstractmethod
    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        pass

    @abc.abstractmethod
    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        pass

    @abc.abstractmethod
    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        pass

class Resistor(Component):

    def __init__(self, positive: str, negative: str, resistence: float) -> None:
        super().__init__([positive, negative])
        self.positive: str = positive
        self.negative: str = negative
        self.resistence: float = resistence

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.negative], terminals[self.negative]] += 1/self.resistence
        matrix[terminals[self.positive], terminals[self.negative]] -= 1/self.resistence
        matrix[terminals[self.negative], terminals[self.positive]] -= 1/self.resistence
        matrix[terminals[self.positive], terminals[self.positive]] += 1/self.resistence

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return (self.voltage(terminals, voltages))/self.resistence

class CurrentFontControledByVoltage(Component):

    def __init__(self, positive: str, negative: str, positive_control: str, negative_control: str, transconductance: complex) -> None:
        super().__init__([positive, negative, positive_control, negative_control])
        self.positive: str = positive
        self.negative: str = negative
        self.positive_control: str = positive_control
        self.negative_control: str = negative_control
        self.transconductance: complex = transconductance

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, maping: typing.Dict[str, int]) -> None:
        matrix[maping[self.positive], maping[self.positive_control]] += self.transconductance
        matrix[maping[self.positive], maping[self.negative_control]] -= self.transconductance
        matrix[maping[self.negative], maping[self.positive_control]] -= self.transconductance
        matrix[maping[self.negative], maping[self.negative_control]] += self.transconductance

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.transconductance * (voltages[terminals[self.positive_control]] - voltages[terminals[self.negative_control]])

class CurrentFont(Component):

    def __init__(self, positive: str, negative: str, current_value: complex) -> None:
        super().__init__([positive, negative])
        self.positive: str = positive
        self.negative: str = negative
        self.current_value: complex = current_value
        self.active: bool = True

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        currents[terminals[self.positive]] -= self.current_value
        currents[terminals[self.negative]] += self.current_value

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.current_value

class Capacitor(Component):

    def __init__(self, positive: str, negative: str, capacitance: float, initial_voltage: float) -> None:
        super().__init__([positive, negative])
        self.positive: str = positive
        self.negative: str = negative
        self.capacitance: float = capacitance
        self.initial_voltage: float = initial_voltage

    @abc.abstractmethod
    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.negative], terminals[self.negative]] += self.s*self.capacitance
        matrix[terminals[self.positive], terminals[self.negative]] -= self.s*self.capacitance
        matrix[terminals[self.negative], terminals[self.positive]] -= self.s*self.capacitance
        matrix[terminals[self.positive], terminals[self.positive]] += self.s*self.capacitance

        currents[terminals[self.positive]] += self.capacitance*self.initial_voltage
        currents[terminals[self.negative]] -= self.capacitance*self.initial_voltage

    @abc.abstractmethod
    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    @abc.abstractmethod
    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.s*self.capacitance*self.voltage(terminals, voltages) - self.capacitance*self.initial_voltage

class Inductor(Component):
    
    def __init__(self, positive: str, negative: str, indutance: float, initial_current: float) -> None:
        super().__init__([positive, negative])
        self.positive: str = positive
        self.negative: str = negative
        self.indutance: float = indutance
        self.initial_current: float = initial_current

    @abc.abstractmethod
    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.negative], terminals[self.negative]] += 1/self.indutance*self.s
        matrix[terminals[self.positive], terminals[self.negative]] -= 1/self.indutance*self.s
        matrix[terminals[self.negative], terminals[self.positive]] -= 1/self.indutance*self.s
        matrix[terminals[self.positive], terminals[self.positive]] += 1/self.indutance*self.s

        currents[terminals[self.positive]] -= self.initial_current/self.s
        currents[terminals[self.negative]] += self.initial_current/self.s

    @abc.abstractmethod
    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    @abc.abstractmethod
    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return (self.initial_current/self.s) + (self.voltage(terminals, voltages)/(self.s*self.indutance))

class Transformer(Component):
    def __init__(self, inductor1: Inductor, inductor2: Inductor, m: float) -> None:
        super().__init__(inductor1.terminals + inductor2.terminals)
        self.inductor1: Inductor = inductor1
        self.inductor2: Inductor = inductor2
        self.m: float = m
        self.gama: np.ndarray = np.zeros((2, 2))
        self.gama[0, 0] = (inductor2.indutance)/(inductor2.indutance*inductor1.indutance - m*m)
        self.gama[1, 1] = (inductor1.indutance)/(inductor2.indutance*inductor1.indutance - m*m)
        self.gama[0, 1] = self.gama[1, 0] = (-m)/(inductor2.indutance*inductor1.indutance - m*m)

    def set_s(self, s: complex) -> None:
        self.s: complex = s

    @abc.abstractmethod
    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.inductor1.positive], terminals[self.inductor1.positive]] += self.gama[0, 0]/self.s
        matrix[terminals[self.inductor1.positive], terminals[self.inductor1.negative]] -= self.gama[0, 0]/self.s
        matrix[terminals[self.inductor1.positive], terminals[self.inductor2.positive]] += self.gama[0, 1]/self.s
        matrix[terminals[self.inductor1.positive], terminals[self.inductor2.negative]] -= self.gama[0, 1]/self.s

        matrix[terminals[self.inductor1.negative], terminals[self.inductor1.positive]] -= self.gama[0, 0]/self.s
        matrix[terminals[self.inductor1.negative], terminals[self.inductor1.negative]] += self.gama[0, 0]/self.s
        matrix[terminals[self.inductor1.negative], terminals[self.inductor2.positive]] -= self.gama[0, 1]/self.s
        matrix[terminals[self.inductor1.negative], terminals[self.inductor2.negative]] += self.gama[0, 1]/self.s

        matrix[terminals[self.inductor2.positive], terminals[self.inductor1.positive]] += self.gama[1, 0]/self.s
        matrix[terminals[self.inductor2.positive], terminals[self.inductor1.negative]] -= self.gama[1, 0]/self.s
        matrix[terminals[self.inductor2.positive], terminals[self.inductor2.positive]] += self.gama[1, 1]/self.s
        matrix[terminals[self.inductor2.positive], terminals[self.inductor2.negative]] -= self.gama[1, 1]/self.s

        matrix[terminals[self.inductor2.negative], terminals[self.inductor1.positive]] -= self.gama[1, 0]/self.s
        matrix[terminals[self.inductor2.negative], terminals[self.inductor1.negative]] += self.gama[1, 0]/self.s
        matrix[terminals[self.inductor2.negative], terminals[self.inductor2.positive]] -= self.gama[1, 1]/self.s
        matrix[terminals[self.inductor2.negative], terminals[self.inductor2.negative]] += self.gama[1, 1]/self.s

        currents[terminals[self.inductor1.positive]] -= self.inductor1.initial_current/self.s
        currents[terminals[self.inductor1.negative]] += self.inductor1.initial_current/self.s
        currents[terminals[self.inductor2.positive]] -= self.inductor2.initial_current/self.s
        currents[terminals[self.inductor2.negative]] += self.inductor2.initial_current/self.s

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        pass

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        pass

class VoltageFont(Component):
    pass

if __name__ == "__main__":
    pass