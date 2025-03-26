from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import numpy as np
import time
from typing import Tuple, Dict

class QuantumPasswordFinder(QuantumCircuit):
    """
    Implements Grover's algorithm for password searching.
    We use Grover's instead of Shor's algorithm because:
    1. Password searching is an unstructured search problem
    2. We're looking for a specific value in a large space
    3. Grover's algorithm provides optimal O(sqrt(N)) search time
    4. It works with any type of password (not just numbers)
    """
    def __init__(self, num_bits: int, name: str = None):
        """
        Initialize the quantum password finder.
        
        Args:
            num_bits (int): Number of bits in the password
            name (str, optional): Name of the circuit
        """
        # Create quantum and classical registers
        qr = QuantumRegister(num_bits, "q")
        cr = ClassicalRegister(num_bits, "c")
        
        # Initialize the quantum circuit
        super().__init__(qr, cr, name=name)
        
        self.num_bits = num_bits
        self.search_space_size = 2 ** num_bits
        self.target_password = None
        
    def create_grover_circuit(self, target: int) -> None:
        """
        Create a quantum circuit implementing Grover's algorithm.
        This is more suitable than Shor's algorithm because:
        1. We don't need to factor numbers
        2. We just need to find a specific value
        3. The circuit is simpler and requires fewer qubits
        """
        self.target_password = target
        
        # Initialize all qubits in superposition
        # This creates equal probability for all possible passwords
        for i in range(self.num_bits):
            self.h(i)
        
        # Oracle for marking the target state
        # This is simpler than Shor's phase estimation
        target_binary = format(target, f'0{self.num_bits}b')
        for i, bit in enumerate(target_binary):
            if bit == '1':
                self.x(i)
        
        # Diffusion operator
        # This amplifies the marked state
        # Much simpler than Shor's quantum Fourier transform
        for i in range(self.num_bits):
            self.h(i)
        
        # Apply phase flip about zero
        for i in range(self.num_bits):
            self.x(i)
        self.h(self.num_bits - 1)
        self.mct(list(range(self.num_bits - 1)), self.num_bits - 1)
        self.h(self.num_bits - 1)
        for i in range(self.num_bits):
            self.x(i)
        
        # Apply H gates again
        for i in range(self.num_bits):
            self.h(i)
        
        # Measure
        self.measure_all()
    
    def find_password(self, target: int, shots: int = 1000) -> Tuple[int, float, Dict[str, int]]:
        """
        Find the target password using Grover's algorithm.
        This is more efficient than Shor's algorithm for password searching because:
        1. We don't need to perform phase estimation
        2. We don't need to factor numbers
        3. The circuit depth is smaller
        4. We need fewer qubits
        """
        # Create the circuit
        self.create_grover_circuit(target)
        
        # Use the Aer simulator
        simulator = AerSimulator()
        
        start_time = time.time()
        
        # Execute the circuit
        result = simulator.run(self, shots=shots).result()
        counts = result.get_counts()
        
        # Find the most common result
        max_count = max(counts.values())
        for bitstring, count in counts.items():
            if count == max_count:
                result = int(bitstring, 2)
                break
        
        end_time = time.time()
        
        return result, end_time - start_time, counts

def simulate_classical_search(num_bits: int, target: int) -> Tuple[int, float]:
    """Simulate classical search for comparison"""
    search_space_size = 2 ** num_bits
    start_time = time.time()
    
    # Classical search
    for i in range(search_space_size):
        if i == target:
            end_time = time.time()
            return i, end_time - start_time
    
    end_time = time.time()
    return -1, end_time - start_time

def main():
    # Test with different password lengths (in bits)
    for num_bits in [1, 2]:
        print(f"\nTesting with {num_bits}-bit password:")
        search_space_size = 2 ** num_bits
        print(f"Search space size: {search_space_size}")
        
        # Create quantum simulator
        finder = QuantumPasswordFinder(num_bits)
        
        # Test with a random target password
        target = np.random.randint(0, search_space_size)
        print(f"Target password (decimal): {target}")
        print(f"Target password (binary): {format(target, f'0{num_bits}b')}")
        
        # Quantum search
        quantum_result, quantum_time, counts = finder.find_password(target)
        print(f"\nQuantum search:")
        print(f"Found password (decimal): {quantum_result}")
        print(f"Found password (binary): {format(quantum_result, f'0{num_bits}b')}")
        print(f"Time taken: {quantum_time:.6f} seconds")
        print(f"Measurement counts: {counts}")
        
        # Classical search
        classical_result, classical_time = simulate_classical_search(num_bits, target)
        print(f"\nClassical search:")
        print(f"Found password (decimal): {classical_result}")
        print(f"Found password (binary): {format(classical_result, f'0{num_bits}b')}")
        print(f"Time taken: {classical_time:.6f} seconds")
        
        # Compare speeds
        speedup = classical_time / quantum_time if quantum_time > 0 else float('inf')
        print(f"\nQuantum speedup: {speedup:.2f}x")
        
        # Theoretical comparison
        print(f"\nTheoretical comparison:")
        print(f"Classical complexity: O({search_space_size})")
        print(f"Quantum complexity: O(sqrt({search_space_size}))")
        print(f"Theoretical speedup: {np.sqrt(search_space_size):.2f}x")

if __name__ == "__main__":
    main() 