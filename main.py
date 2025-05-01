import numpy as np

from src.circuit import Circuit
import src.component as Component

if __name__ == "__main__":

    circuit = Circuit()

    components = [
        Component.Resistor('a', 'b', 1),
        Component.CurrentFont('a', 'c', 10),
        Component.Transconductor('c', 'b', 'a', 'b', 3),
        Component.Resistor('b', 'c', 2)
    ]

    for component in components:
        circuit.add_component(component)

    # circuit.solve('c')

    f = circuit.transfer_function('c', (1, "Current"), (3, "Voltage"))
    f.plot_laplace()
    f.plot_bode()