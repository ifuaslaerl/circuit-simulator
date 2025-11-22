import numpy as np
from circuit_simulator.circuit import Circuit
from circuit_simulator.components import VoltageSource, Resistor, Inductor, Capacitor

def main():
    # 1. Initialize the Circuit
    circuit = Circuit()
    
    # 2. Define Components for a Series RLC Circuit
    # Values chosen to create an underdamped response with poles visible near origin
    # V1 (Input) -> R1 -> L1 -> C1 -> Ground
    components = [
        VoltageSource("Vin", "n1", "gnd", 1.0),
        Resistor("R1", "n1", "n2", 0.5),      # Low resistance = High 'Q' factor (sharp peaks)
        Inductor("L1", "n2", "n3", 1.0),
        Capacitor("C1", "n3", "gnd", 1.0)     # Output voltage is taken across C1
    ]

    # 3. Add components to the circuit
    for comp in components:
        circuit.add_component(comp)

    print("Circuit constructed. Calculating Transfer Function...")

    # 4. Generate the Transfer Function H(s) = V_out / V_in
    # We look at the Voltage across C1 relative to the Voltage of Vin
    H_s = circuit.transfer_function(
        earth="gnd", 
        input_node=("Vin", "Voltage"), 
        output_node=("C1", "Voltage")
    )

    # 5. Customize the Plot Range
    # The default range is (-1000, 1000), but our poles are at small values.
    # We modify the ranges directly on the function object for a better zoom.
    H_s.real_range = (-2, 0.5)  # Focus on the negative real axis (stable region)
    H_s.imag_range = (-2, 2)    # Focus around DC and low frequency
    H_s.resolution = 50         # Lower resolution renders faster

    # 6. Plotting
    print("Generating Bode Plot...")
    H_s.plot_bode()

    print("Generating 3D Laplace Plot...")
    print("Tip: Click and drag the 3D plot to rotate it.")
    H_s.plot_laplace()

if __name__ == "__main__":
    main()
