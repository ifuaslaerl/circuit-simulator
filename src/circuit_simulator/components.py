import abc
import typing
import numpy as np

class Component(abc.ABC):
    def __init__(self, terminals: typing.List[str], name: str) -> None:
        self.name = name
        self.terminals: typing.List[str] = terminals
        self.s: complex = 0
        self.active: bool = False

    def set_s(self, s: complex) -> None:
        self.s = s

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
    def __init__(self, name: str, positive: str, negative: str, resistance: float) -> None:
        # Deterministic internal node name
        self.x: str = f"{name}_internal_i"
        super().__init__([positive, negative, self.x], name)
        self.positive = positive
        self.negative = negative
        self.resistance = resistance

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.positive], terminals[self.x]] += 1
        matrix[terminals[self.negative], terminals[self.x]] -= 1
        matrix[terminals[self.x], terminals[self.positive]] -= 1
        matrix[terminals[self.x], terminals[self.negative]] += 1
        matrix[terminals[self.x], terminals[self.x]] += self.resistance

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.voltage(terminals, voltages) / self.resistance

class CurrentSource(Component):
    def __init__(self, name: str, positive: str, negative: str, current_value: complex) -> None:
        super().__init__([positive, negative], name)
        self.positive = positive
        self.negative = negative
        self.s = current_value
        self.active = True

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        currents[terminals[self.positive]] -= self.s
        currents[terminals[self.negative]] += self.s

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.s

class VoltageSource(Component):
    def __init__(self, name: str, positive: str, negative: str, voltage_value: complex) -> None:
        self.x = f"{name}_internal_i"
        super().__init__([positive, negative, self.x], name)
        self.positive = positive
        self.negative = negative
        self.s = voltage_value
        self.active = True

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.positive], terminals[self.x]] += 1
        matrix[terminals[self.negative], terminals[self.x]] -= 1
        matrix[terminals[self.x], terminals[self.positive]] -= 1
        matrix[terminals[self.x], terminals[self.negative]] += 1
        currents[terminals[self.x]] -= self.s

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.s

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.x]]

class Inductor(Component):
    def __init__(self, name: str, positive: str, negative: str, inductance: float, initial_current: float = 0) -> None:
        self.x = f"{name}_internal_i"
        super().__init__([positive, negative, self.x], name)
        self.positive = positive
        self.negative = negative
        self.inductance = inductance
        self.initial_current = initial_current

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.positive], terminals[self.x]] += 1
        matrix[terminals[self.negative], terminals[self.x]] -= 1
        matrix[terminals[self.x], terminals[self.positive]] -= 1
        matrix[terminals[self.x], terminals[self.negative]] += 1
        matrix[terminals[self.x], terminals[self.x]] += self.s * self.inductance

        currents[terminals[self.x]] += self.initial_current / self.s

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return (self.initial_current / self.s) + (self.voltage(terminals, voltages) / (self.s * self.inductance))

class Capacitor(Component):
    def __init__(self, name: str, positive: str, negative: str, capacitance: float, initial_voltage: float = 0) -> None:
        super().__init__([positive, negative], name)
        self.positive = positive
        self.negative = negative
        self.capacitance = capacitance
        self.initial_voltage = initial_voltage

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.negative], terminals[self.negative]] += self.s * self.capacitance
        matrix[terminals[self.positive], terminals[self.negative]] -= self.s * self.capacitance
        matrix[terminals[self.negative], terminals[self.positive]] -= self.s * self.capacitance
        matrix[terminals[self.positive], terminals[self.positive]] += self.s * self.capacitance

        currents[terminals[self.positive]] += self.capacitance * self.initial_voltage
        currents[terminals[self.negative]] -= self.capacitance * self.initial_voltage

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.s * self.capacitance * self.voltage(terminals, voltages) - self.capacitance * self.initial_voltage

class VoltageControlledCurrentSource(Component):
    def __init__(self, name: str, positive: str, negative: str, positive_control: str, negative_control: str, transconductance: complex) -> None:
        super().__init__([positive, negative, positive_control, negative_control], name)
        self.positive = positive
        self.negative = negative
        self.positive_control = positive_control
        self.negative_control = negative_control
        self.transconductance = transconductance

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, maping: typing.Dict[str, int]) -> None:
        matrix[maping[self.positive], maping[self.positive_control]] += self.transconductance
        matrix[maping[self.positive], maping[self.negative_control]] -= self.transconductance
        matrix[maping[self.negative], maping[self.positive_control]] -= self.transconductance
        matrix[maping[self.negative], maping[self.negative_control]] += self.transconductance

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.positive]] - voltages[terminals[self.negative]]

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.transconductance * (voltages[terminals[self.positive_control]] - voltages[terminals[self.negative_control]])

class CurrentControlledVoltageSource(Component):
    def __init__(self, name: str, positive: str, negative: str, positive_control: str, negative_control: str, transresistance: complex):
        self.x = f"{name}_internal_i"
        super().__init__([positive, negative, positive_control, negative_control, self.x], name)
        self.positive = positive
        self.negative = negative
        self.positive_control = positive_control
        self.negative_control = negative_control
        self.transresistance = transresistance

    def stamp(self, matrix: np.ndarray, currents: np.ndarray, terminals: typing.Dict[str, int]) -> None:
        matrix[terminals[self.positive], terminals[self.x]] += 1
        matrix[terminals[self.negative], terminals[self.x]] -= 1
        matrix[terminals[self.x], terminals[self.positive]] -= 1
        matrix[terminals[self.x], terminals[self.negative]] += 1
        matrix[terminals[self.x], terminals[self.positive_control]] += self.transresistance
        matrix[terminals[self.x], terminals[self.negative_control]] -= self.transresistance

    def voltage(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return self.transresistance * (voltages[terminals[self.positive_control]] - voltages[terminals[self.negative_control]])

    def current(self, terminals: typing.Dict[str, int], voltages: np.ndarray) -> complex:
        return voltages[terminals[self.x]]
