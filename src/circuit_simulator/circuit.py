import typing
import numpy as np
import pandas as pd

from . import components as Component
from .graphical import ComplexFunction

class Circuit:
    def __init__(self) -> None:
        self.n: int = 0
        self.temp_n: int = 0
        self.matrix: np.ndarray = np.zeros(shape=(0, 0), dtype=complex)
        self.voltages: np.ndarray = np.zeros(shape=(0, 1), dtype=complex)
        self.currents: np.ndarray = np.zeros(shape=(0, 1), dtype=complex)

        self.components: typing.Dict[str, Component.Component] = dict()
        self.active_components: typing.List[Component.Component] = []
        self.passive_components: typing.List[Component.Component] = []
        self.terminals: typing.Dict[str, int] = dict()
        self.real_terminals: typing.Dict[str, int] = dict()

    def check_terminals(self, component: Component.Component):
        for terminal in component.terminals:
            if terminal not in self.terminals:
                self.terminals[terminal] = self.temp_n
                self.temp_n += 1
                self.matrix = np.pad(self.matrix, ((0, 1), (0, 1)), "constant")
                self.currents = np.pad(self.currents, ((0, 1), (0, 0)), "constant")
                # Pad voltages to match dimensions
                self.voltages = np.pad(self.voltages, ((0, 1), (0, 0)), "constant")

            if terminal not in self.real_terminals:
                self.real_terminals[terminal] = self.n
                self.n += 1

    def add_component(self, component: Component.Component) -> None:
        self.components[component.name] = component
        self.check_terminals(component)

    def solve(self, ground: str, sweep: complex = None) -> None:
        # Reset voltages for superposition
        self.voltages = np.zeros(shape=(self.n, 1), dtype=complex)

        self.active_components = []
        self.passive_components = []

        for name, component in self.components.items():
            if component.active:
                self.active_components.append(component)
            else:
                self.passive_components.append(component)

        # Superposition Loop
        for active_component in self.active_components:
            self.temp_n = 0
            self.matrix = np.zeros(shape=(0, 0), dtype=complex)
            self.currents = np.zeros(shape=(0, 1), dtype=complex)
            self.terminals = dict()

            # Stamp active component
            self.check_terminals(active_component)
            active_component.stamp(self.matrix, self.currents, self.terminals)
            
            s = sweep if sweep else active_component.s

            # Stamp passive components
            for passive_component in self.passive_components:
                self.check_terminals(passive_component)
                passive_component.set_s(s)
                passive_component.stamp(self.matrix, self.currents, self.terminals)

            assert ground in self.terminals, f"Ground node '{ground}' not found in circuit."

            # Remove ground row/col for calculation
            g_idx = self.terminals[ground]
            matrix_reduced = np.delete(np.delete(self.matrix, g_idx, axis=0), g_idx, axis=1)
            current_reduced = np.delete(self.currents, g_idx, axis=0)

            try:
                voltages_solved = np.linalg.solve(matrix_reduced, current_reduced)
            except np.linalg.LinAlgError:
                raise ValueError("Singular matrix. Circuit may be unsolvable or nodes are floating.")

            # Re-insert ground (0V)
            voltages_solved = np.insert(voltages_solved, g_idx, 0).reshape(-1, 1)

            # Superposition sum
            for key in self.terminals:
                 if key in self.real_terminals:
                    self.voltages[self.real_terminals[key]] += voltages_solved[self.terminals[key]]

    def component_info(self, name: str) -> pd.Series:
        assert name in self.components
        info = pd.Series(index=["Name", "Voltage", "Current", "Power"], dtype=object)
        info["Name"] = self.components[name].name
        info["Voltage"] = self.components[name].voltage(self.terminals, self.voltages)
        info["Current"] = self.components[name].current(self.terminals, self.voltages)
        info["Power"] = info["Voltage"] * info["Current"]
        return info

    def transfer_function(self, earth: str,
                        input_node: typing.Tuple[str, str], 
                        output_node: typing.Tuple[str, str]) -> ComplexFunction:
        
        assert input_node[0] in self.components, f"Input component {input_node[0]} not found"
        assert output_node[0] in self.components, f"Output component {output_node[0]} not found"
        valid_types = ["Voltage", "Current", "Power"]
        assert input_node[1] in valid_types
        assert output_node[1] in valid_types

        # Capture 'self' for the closure
        circuit_instance = self

        class TransferFunctionImpl(ComplexFunction):
            @staticmethod
            def f(s_values):
                # Optimization: Handle scalar complex value directly
                if isinstance(s_values, (complex, float, int)):
                     s = s_values
                     circuit_instance.components[input_node[0]].set_s(s)
                     circuit_instance.solve(earth, s)
                     
                     in_val = circuit_instance.component_info(input_node[0])[input_node[1]]
                     out_val = circuit_instance.component_info(output_node[0])[output_node[1]]
                     return out_val / in_val

                # Handle numpy array (meshgrids or linear arrays)
                if isinstance(s_values, np.ndarray):
                    input_comp = circuit_instance.components[input_node[0]]
                    
                    # We flatten the input array to iterate over it linearly
                    flat_s = s_values.flatten()
                    results = []
                    
                    for s in flat_s:
                        input_comp.set_s(s)
                        circuit_instance.solve(earth, s)
                        
                        in_val = circuit_instance.component_info(input_node[0])[input_node[1]]
                        out_val = circuit_instance.component_info(output_node[0])[output_node[1]]
                        
                        # Avoid division by zero if input is 0 (though unlikely in AC analysis unless DC)
                        if in_val == 0:
                            results.append(0)
                        else:
                            results.append(out_val / in_val)
                    
                    # Reshape results back to original shape (e.g., for meshgrid)
                    return np.array(results).reshape(s_values.shape)

        return TransferFunctionImpl()

    def table(self, components: typing.List[str] = None) -> pd.DataFrame:
        series = []
        if not components: 
            components = list(self.components.keys())

        for component_name in components:
            series.append(self.component_info(component_name))

        return pd.concat(series, axis=1).T
