import pandas as pd
import numpy as np

from src.circuit import Circuit
import src.component as Component

# Ler e salvar a Netlist
# Funções personalizadas de erro
# Concertar a Transfer Funcion
# Adaptar para uma análise DC

if __name__ == "__main__":

    circuit = Circuit()

    components = [
        Component.CurrentFont("I1", 'a', 'b', 1j),
        Component.Inductor("L1", 'a', 'b', 2),
        Component.Capacitor("C1", 'a', 'c', 2),
        Component.Resistor("R1", 'c', 'b', 5),
        Component.VoltageFontControledByCurrent("Gm1", 'c', 'd', 'b', 'c', 2),
        Component.Resistor("R2", 'd', 'b', 3)
    ]

    for component in components:
        circuit.add_component(component)

    f = circuit.transfer_function('b', ("R2", "Current"), ("I1", "Current"))
    f.plot_laplace()
    f.plot_bode()

    circuit.solve('b', sweep=1j)
    
    df = circuit.table()

    print(df)
