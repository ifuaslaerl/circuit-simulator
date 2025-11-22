# Circuit Simulator

A Python-based linear circuit simulator utilizing Modified Nodal Analysis (MNA) to solve for voltages and currents in the frequency domain.

## Features
- **Components**: Resistors, Inductors, Capacitors, Transformers, and Controlled Sources.
- **Analysis**: AC analysis (Frequency sweep), Transfer Functions, Bode Plots, and Pole-Zero plots (3D).
- **Output**: Pandas DataFrames for easy data manipulation.

## Installation

# ```bash
# pip install .
# ```

## Usage

See `examples/simple_circuit.py` for a full example.

```python
from circuit_simulator.circuit import Circuit
from circuit_simulator.components import Resistor, VoltageSource

circuit = Circuit()
circuit.add_component(VoltageSource("V1", "a", "b", 10))
circuit.add_component(Resistor("R1", "a", "b", 100))
circuit.solve("b")
print(circuit.table())
```
