# Qward

A framework for analyzing and validating quantum code execution quality on quantum processing units (QPUs). Qward helps developers and researchers understand how their quantum algorithms perform on real hardware, providing insights into QPU behavior and code quality metrics.

## Overview

Qward provides tools to:
- Execute quantum circuits on QPUs
- Collect comprehensive execution metrics
- Analyze circuit performance
- Validate algorithm correctness
- Generate insights about QPU behavior
- Compare results across different backends

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Set up your IBM Quantum credentials in a `.env` file:
```
IBM_QUANTUM_CHANNEL=ibm_quantum
IBM_QUANTUM_TOKEN=your_token_here
```

2. Run the example:
```python
from qward.validators.teleportation_validator import TeleportationValidator
from qward.experiments.experiments import Experiments

# Create a validator
validator = TeleportationValidator(
    payload_size=3,
    gates=["h", "x"],
    use_barriers=True
)

# Create experiments framework
experiments = Experiments()

# Run experiments
results = experiments.run_parameter_correlation(
    validator=validator,
    param_ranges={
        "payload_size": [2, 3, 4],
        "gates": [["h"], ["x"], ["h", "x"]]
    }
)

# Analyze results
experiments.plot_success_rates()
experiments.analyze_error_distribution()
```

## Core Components

### 1. Base Validator System

The framework provides a base validator system that can be extended for different quantum algorithms:

```python
from qward.validators.base_validator import BaseValidator

class YourAlgorithmValidator(BaseValidator):
    def __init__(self, params):
        super().__init__()
        self.params = params
        
    def validate(self):
        # Your validation logic
        pass
```

### 2. Experiments Framework

A flexible framework for running and analyzing quantum experiments:

```python
from qward.experiments.experiments import Experiments

experiments = Experiments()
results = experiments.run_parameter_correlation(
    validator=your_validator,
    param_ranges=param_ranges
)
```

## Features

1. **Multiple Experiment Types**
   - Parameter correlation analysis
   - Fixed parameter testing
   - Dynamic parameter testing
   - Depth analysis
   - Target performance testing

2. **Comprehensive Metrics**
   - Circuit metrics (depth, width, size)
   - Execution metrics (success rates, error rates)
   - Hardware metrics (job duration, quantum duration)

3. **Analysis Capabilities**
   - Statistical analysis
   - Error distribution analysis
   - Performance correlation
   - Visualization tools

4. **Data Management**
   - CSV export/import
   - Results serialization
   - Data preprocessing

## Contributing

We welcome contributions! To add your own validator:

1. Create a new validator class extending BaseValidator
2. Implement required methods
3. Add tests
4. Update documentation
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details. 