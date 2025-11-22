import pandas as pd
from circuit_simulator.circuit import Circuit
import circuit_simulator.components as Component

if __name__ == "__main__":
    circuit = Circuit()

    # Note: Renamed classes to standard English (CurrentFont -> CurrentSource)
    components = [
        Component.CurrentSource("I1", 'a', 'b', 1j),
        Component.Inductor("L1", 'a', 'b', 2),
        Component.Capacitor("C1", 'a', 'c', 2),
        Component.Resistor("R1", 'c', 'b', 5),
        Component.VoltageControlledCurrentSource("Gm1", 'c', 'd', 'b', 'c', 2), 
        Component.Resistor("R2", 'd', 'b', 3)
    ]

    for component in components:
        circuit.add_component(component)

    # Solve the circuit
    circuit.solve(ground='b', sweep=1j)
    
    df = circuit.table()
    print("Circuit Analysis Results:")
    print(df)
