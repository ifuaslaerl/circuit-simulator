import overrides
import typing
import numpy as np
import pandas as pd

from src.component import Component
from src.grafical import ComplexFunction

class Circuit:

    def __init__(self, path: str = None) -> None:
        self.n: int = 0
        self.temp_n: int = 0
        self.matrix: np.ndarray = np.zeros(shape=(0, 0), dtype=complex)
        self.voltages: np.ndarray = np.zeros(shape=(0, 1), dtype=complex)
        self.currents: np.ndarray = np.zeros(shape=(0, 1), dtype=complex)

        self.components: typing.List[Component] = []
        self.active_components: typing.List[Component] = []
        self.passive_components: typing.List[Component] = []
        self.terminals: typing.Dict[str, int] = dict()
        self.real_terminals: typing.Dict[str, int] = dict()

        self.path: str = path if path else self.read_netlist(path)

    def read_netlist(self, path: str) -> str:
        pass

    def check_terminals(self, component: Component):
        for terminal in component.terminals:
            if not terminal in self.terminals:
                self.terminals[terminal] = self.temp_n
                self.temp_n += 1
                self.matrix = np.pad(self.matrix, ((0, 1), (0, 1)), "constant")
                self.currents = np.pad(self.currents, ((0, 1), (0, 0)), "constant")
                self.voltages = np.pad(self.currents, ((0, 1), (0, 0)), "constant")

            if not terminal in self.real_terminals:
                self.real_terminals[terminal] = self.n
                self.n += 1
                self.voltages = np.pad(self.voltages, ((0, 1), (0, 0)), "constant")

    def add_component(self, component: Component) -> None:
        self.components.append(component)
        self.check_terminals(component)

    def solve(self, earth: str, sweep: complex = None) -> None:

        self.voltages: np.ndarray = np.zeros(shape=(0, 1))

        self.active_components: typing.List[Component] = []
        self.passive_components: typing.List[Component] = []

        for component in self.components:
            if component.active:
                self.active_components.append(component)
            else:
                self.passive_components.append(component)

        for active_component in self.active_components:
            self.temp_n = 0
            self.matrix: np.ndarray = np.zeros(shape=(0, 0), dtype=complex)
            self.currents: np.ndarray = np.zeros(shape=(0, 1), dtype=complex)
            self.terminals: typing.Dict[str, int] = dict()

            self.check_terminals(active_component)
            active_component.stamp(self.matrix, self.currents, self.terminals)
            if sweep: s = sweep
            else: s = active_component.s

            for passive_component in self.passive_components:
                self.check_terminals(passive_component)
                passive_component.set_s(s)
                passive_component.stamp(self.matrix, self.currents, self.terminals)

            assert earth in self.terminals

            matrix = np.delete(np.delete(self.matrix, self.terminals[earth], axis=0) , self.terminals[earth], axis=1)
            current = np.delete(self.currents, self.terminals[earth], axis=0)
            voltages = np.linalg.solve(matrix, current)
            voltages = np.insert(voltages, self.terminals[earth], 0).reshape(-1, 1)

            if self.voltages.dtype != voltages.dtype:
                self.voltages = self.voltages.astype(complex)
                voltages = voltages.astype(complex)

            for key in self.terminals:
                self.voltages[self.real_terminals[key]] += voltages[self.terminals[key]]

    def component_info(self, id: int) -> pd.Series:
        info: pd.Series = pd.Series(index = ["Voltage", "Current", "Power"], dtype=complex)
        info["Voltage"] = self.components[id].voltage(self.terminals, self.voltages)
        info["Current"] = self.components[id].current(self.terminals, self.voltages)
        info["Power"] = info["Voltage"]*info["Current"]
        return info

    def transfer_function(self, earth: str,
                        input: typing.Tuple[int, str], 
                        output: typing.Tuple[int, str]) \
                        -> ComplexFunction:

        assert input[0] <= self.n
        assert output[0] <= self.n

        assert input[1] in ["Voltage", "Current", "Power"]
        assert output[1] in ["Voltage", "Current", "Power"]

        class function(ComplexFunction):
            @staticmethod
            def f(values):
                if type(values) == np.ndarray:
                    if len(values.shape) == 2:
                        answer = []
                        for values_list in values:
                            for s in values_list:
                                self.components[input[0]].set_s(s)
                                self.solve(earth, s)

                                input_component_info = self.component_info(input[0])[input[1]]
                                output_component_info = self.component_info(output[0])[output[1]]
                                answer.append(output_component_info/input_component_info)
                        answer = np.array(answer).reshape(values.shape)
                        return answer
                    elif len(values.shape) == 1:
                        answer = []
                        for s in values:
                            self.components[input[0]].set_s(s)
                            self.solve(earth, s)

                            input_component_info = self.component_info(input[0])[input[1]]
                            output_component_info = self.component_info(output[0])[output[1]]
                            answer.append(output_component_info/input_component_info)
                        answer = np.array(answer).reshape(values.shape)
                        return answer
                elif type(values) == complex:
                    self.components[input[0]].set_s(s)
                    self.solve(earth, s)

                    input_component_info = self.component_info(input[0])[input[1]]
                    output_component_info = self.component_info(output[0])[output[1]]
                    return output_component_info/input_component_info

        return function()