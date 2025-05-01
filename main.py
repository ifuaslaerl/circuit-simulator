import numpy as np

from src.circuit import Circuit
import src.component as Component

if __name__ == "__main__":

    circuit = Circuit()

    components = [
        Component.CurrentFont('a', 'b', 1),
        Component.Inductor('a', 'b', 2),
        Component.Capacitor('a', 'c', 2),
        Component.Resistor('c', 'b', 5),
        Component.VoltageFontControledByCurrent('c', 'd', 'b', 'c', 2),
        Component.Resistor('d', 'b', 3)
    ]

    for component in components:
        circuit.add_component(component)

    # circuit.solve('c')

    f = circuit.transfer_function('b', (4, "Current"), (0, "Current"))
    f.plot_laplace()
    f.plot_bode()