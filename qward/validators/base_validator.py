from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit.visualization import plot_histogram
from qiskit.providers import Backend
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Type
from dotenv import load_dotenv
from ..analysis.analysis import Analysis

# Load environment variables
load_dotenv()

# Get IBM Quantum credentials from environment variables
IBM_QUANTUM_CHANNEL = os.getenv('IBM_QUANTUM_CHANNEL', 'ibm_quantum')
IBM_QUANTUM_TOKEN = os.getenv('IBM_QUANTUM_TOKEN')

class BaseValidator(QuantumCircuit):
    """
    Base class for quantum algorithm validators in the Qiskit ecosystem.
    Extends Qiskit's QuantumCircuit to provide standardized validation capabilities.
    """
    
    def __init__(self, num_qubits: int = 1, num_clbits: int = 1, use_barriers: bool = True, name: str = None):
        """
        Initialize the base validator with a quantum circuit.
        
        Args:
            num_qubits (int): Number of qubits in the circuit
            num_clbits (int): Number of classical bits for measurement
            use_barriers (bool): Whether to include barriers in the circuit
            name (str): Name of the circuit
        """
        # Create quantum and classical registers
        qr = QuantumRegister(num_qubits, "q")
        cr = ClassicalRegister(num_clbits, "c")
        
        # Initialize the quantum circuit
        super().__init__(qr, cr, name=name)
        
        # Store additional attributes
        self.use_barriers = use_barriers
        self.analyzers: List[Analysis] = []
    
    def add_analyzer(self, analyzer: Analysis):
        """
        Add an analyzer to the validator.
        
        Args:
            analyzer (Analysis): The analyzer to add
        """
        self.analyzers.append(analyzer)
    
    def _simulate(self, shots: int = 1024, show_histogram: bool = False):
        """
        Simulate the circuit using Qiskit's Aer simulator.
        
        Args:
            shots (int): Number of shots per simulation
            show_histogram (bool): Whether to display the measurement histogram
            
        Returns:
            dict: Dictionary containing simulation results
        """
        simulator = AerSimulator()
        result = simulator.run(self, shots=shots).result()
        counts = result.get_counts()
        
        if show_histogram:
            display(plot_histogram(counts))
        
        return {
            "counts": counts,
            "shots": shots
        }
    
    def run_simulation(self, show_histogram: bool = False, num_jobs: int = 1000, shots_per_job: int = 1024):
        """
        Run a simulation of the circuit and return comprehensive results.
        
        Args:
            show_histogram (bool): Whether to display the measurement histogram
            num_jobs (int): Number of jobs to run (each job is an independent experiment)
            shots_per_job (int): Number of shots per job
            
        Returns:
            dict: Dictionary containing simulation results and circuit metrics
        """
        # Get first simulation results
        sim_results = self._simulate(shots=shots_per_job, show_histogram=show_histogram)
        
        # Circuit metrics
        circuit_metrics = {
            "depth": self.depth(),
            "width": self.width(),
            "size": self.size(),
            "count_ops": self.count_ops(),
            "num_qubits": self.num_qubits,
            "num_clbits": self.num_clbits,
            "num_ancillas": self.num_ancillas,
            "num_parameters": self.num_parameters,
            "has_calibrations": bool(self.calibrations),
            "has_layout": bool(self.layout)
        }
        
        # Add first job results to analyzers
        for analyzer in self.analyzers:
            analyzer.add_results({
                "counts": sim_results["counts"],
                "shots": shots_per_job,
                "job_id": 0
            })
        
        # Run additional jobs if requested
        if num_jobs > 1:
            for job_id in range(1, num_jobs):
                job_result = self._simulate(shots=shots_per_job, show_histogram=False)
                # Add each job's results separately to analyzers
                for analyzer in self.analyzers:
                    analyzer.add_results({
                        "counts": job_result["counts"],
                        "shots": shots_per_job,
                        "job_id": job_id
                    })
                # Aggregate counts for final results
                sim_results["counts"] = {
                    k: sim_results["counts"].get(k, 0) + job_result["counts"].get(k, 0)
                    for k in set(sim_results["counts"]) | set(job_result["counts"])
                }
        
        return {
            "results_metrics": sim_results,
            "circuit_metrics": circuit_metrics
        }
    
    def run_on_ibm(self, channel: str = None, token: str = None):
        """
        Run the circuit on IBM Quantum hardware.
        
        Args:
            channel (str, optional): IBM Quantum channel
            token (str, optional): IBM Quantum token
            
        Returns:
            dict: Dictionary containing execution results and job information
        """
        try:
            # Use environment variables if no credentials are provided
            channel = channel or IBM_QUANTUM_CHANNEL
            token = token or IBM_QUANTUM_TOKEN
            
            if not token:
                raise ValueError("No IBM Quantum token provided. Please set IBM_QUANTUM_TOKEN in .env file or provide it directly.")

            QiskitRuntimeService.save_account(
                channel=channel, 
                token=token,
                overwrite=True
            )
            
            service = QiskitRuntimeService()
            backend = service.least_busy(simulator=False, operational=True)
            print(f"Using backend: {backend.configuration().backend_name}")
            print(f"Pending jobs: {backend.status().pending_jobs}")
            
            pm = generate_preset_pass_manager(backend=backend, optimization_level=0)
            sampler = Sampler(backend)
            isa_circuit = pm.run(self)
            job = sampler.run([isa_circuit])
            job_id = job.job_id()
            print(f">>> Job ID: {job_id}")
            print(f">>> Job Status: {job.status()}")

            import time
            start_time = time.time()
            while time.time() - start_time < 600:  # 10 minutes timeout
                status = job.status()
                print(f">>> Job Status: {status}")
                
                if status == 'DONE':
                    result = job.result()
                    counts = result[0].data.c.get_counts()
                    print(counts)
                    display(plot_histogram(counts))
                    
                    # Update analyzers with raw IBM results
                    for analyzer in self.analyzers:
                        analyzer.add_results({"counts": counts})
                    
                    return {
                        "status": "completed",
                        "job_id": job_id,
                        "counts": counts,
                        "backend": backend.configuration().backend_name
                    }
                elif status != 'RUNNING' and status != 'QUEUED':
                    print(f"Job ended with status: {status}")
                    return {
                        "status": "error",
                        "job_id": job_id,
                        "error": f"Job ended with status: {status}",
                        "backend": backend.configuration().backend_name
                    }
                
                time.sleep(5)

            print("Job timed out after 10 minutes")
            return {
                "status": "pending",
                "job_id": job_id,
                "backend": backend.configuration().backend_name
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def draw(self):
        """
        Draw the quantum circuit.
        
        Returns:
            matplotlib.figure.Figure: The circuit diagram
        """
        return super().draw(output='mpl') 