# Cell 1 - Imports and Setup
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from qiskit.visualization import circuit_drawer

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.getcwd())
sys.path.append(project_root)

from qward.validators.teleportation_validator import TeleportationValidator
from qward.experiments.experiments import Experiments

# Cell 2 - Create and Display Circuit
# Create a teleportation validator
validator = TeleportationValidator(
    payload_size=3,
    gates=["h", "x"],  # Apply Hadamard and X gates to the payload qubit
    use_barriers=True
)

# Display the circuit
print("Quantum Teleportation Circuit:")
circuit_fig = validator.draw()
display(circuit_fig)

# Cell 3 - Run Simulation
# Create experiments framework
experiments = Experiments()

# Run simulation
print("\nRunning simulation...")
results = validator.run_simulation(show_histogram=True)

# Display results
print("\nSimulation Results:")
print(f"Success Rate: {results['results_metrics']['success_rate']:.2%}")
print("\nCircuit Metrics:")
for metric, value in results['circuit_metrics'].items():
    print(f"{metric}: {value}")

# Cell 4 - Parameter Analysis
# Run parameter correlation analysis
param_ranges = {
    "payload_size": [2, 3, 4],
    "gates": [["h"], ["x"], ["h", "x"]]
}

print("Running parameter correlation analysis...")
results = experiments.run_parameter_correlation(validator, param_ranges)
print("\nResults:")
print(results)

# Cell 5 - Visualization
# Plot success rates
print("\nPlotting success rates...")
experiments.plot_success_rates("payload_size")

# Cell 6 - Error Analysis
# Analyze error distribution
print("\nAnalyzing error distribution...")
error_analysis = experiments.analyze_error_distribution()
print("\nError Analysis:")
for key, value in error_analysis.items():
    print(f"{key}: {value}")

# Cell 7 - Export Results
# Export results
print("\nExporting results...")
experiments.export_results("teleportation_results.csv")

# Cell 8 - Fixed Parameter Test
# Run fixed parameter test
print("\nRunning fixed parameter test...")
fixed_params = {
    "payload_size": 3,
    "gates": ["h", "x"]
}
results = experiments.run_fixed_parameter_test(validator, fixed_params)
print("\nFixed Parameter Test Results:")
print(results)

# Cell 9 - Depth Analysis
# Run depth analysis
print("\nRunning depth analysis...")
results = experiments.run_depth_analysis(
    validator,
    depth_range=range(1, 6),
    fixed_params={"payload_size": 3}
)
print("\nDepth Analysis Results:")
print(results)

# Cell 10 - Direct Qiskit Features
# Use Qiskit features directly
validator.draw()  # Draw the circuit
print("\nCircuit depth:", validator.depth())  # Get circuit depth
print("\nOperation counts:", validator.count_ops())  # Count operations 