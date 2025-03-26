from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import numpy as np
import time
import hashlib
from typing import Tuple, Dict, List

def simple_hash(value: int, bits: int) -> int:
    """
    A simplified hash function for demonstration purposes.
    In reality, we would use a cryptographic hash like SHA-256.
    
    Args:
        value (int): The value to hash
        bits (int): Number of bits in the output hash
        
    Returns:
        int: A simplified hash value
    """
    # Convert to bytes and hash with SHA-256 (for demonstration)
    hash_obj = hashlib.sha256(str(value).encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    
    # Take only the specified number of bits
    mask = (1 << bits) - 1
    return hash_int & mask

class RealisticPasswordCracker(QuantumCircuit):
    """
    A more realistic approach to quantum password cracking.
    In a real scenario, we only know the hash, not the original password.
    """
    def __init__(self, num_bits: int, hash_value: int, name: str = None):
        """
        Initialize the quantum password cracker.
        
        Args:
            num_bits (int): Number of bits in the password
            hash_value (int): The hash value we're trying to crack
            name (str, optional): Name of the circuit
        """
        # For a realistic implementation, we would need:
        # 1. Qubits for the password
        # 2. Qubits for the hash function computation
        # 3. Ancilla qubits for temporary calculations
        
        # For simplicity, we'll use a limited number of qubits
        password_qubits = num_bits
        hash_qubits = num_bits  # In reality, this would be much larger
        ancilla_qubits = 1  # In reality, this would be much larger
        
        total_qubits = password_qubits + hash_qubits + ancilla_qubits
        
        # Create quantum and classical registers
        self.password_register = QuantumRegister(password_qubits, "password")
        self.hash_register = QuantumRegister(hash_qubits, "hash")
        self.ancilla_register = QuantumRegister(ancilla_qubits, "ancilla")
        self.cr = ClassicalRegister(password_qubits, "measurement")
        
        # Initialize the quantum circuit
        super().__init__(
            self.password_register,
            self.hash_register,
            self.ancilla_register,
            self.cr,
            name=name
        )
        
        self.num_bits = num_bits
        self.hash_value = hash_value
        self.search_space_size = 2 ** num_bits
        
    def oracle_for_hash(self) -> None:
        """
        Oracle that marks states whose hash equals the target hash.
        
        This is a simplified implementation. In reality, implementing
        a cryptographic hash function like SHA-256 would require thousands
        of qubits and a very deep circuit, which is beyond current quantum
        hardware capabilities.
        """
        print("NOTE: In a real implementation, this oracle would implement")
        print("the actual hash function (like SHA-256) as a quantum circuit.")
        print("However, this is extremely complex and beyond current capabilities.")
        print("For demonstration purposes, we're using a simplified approach.")
        
        # For demonstration, we'll simulate the oracle by directly marking
        # the states that would match our target hash
        
        # In a real implementation, we would:
        # 1. Apply the hash function to the password register
        # 2. Compare the result with the target hash
        # 3. Mark the states that match
        
        # For simplicity, we'll pre-compute which inputs hash to our target
        # and directly mark them
        
        targets = []
        for i in range(self.search_space_size):
            if simple_hash(i, self.num_bits) == self.hash_value:
                targets.append(i)
                
        print(f"Found {len(targets)} password(s) that hash to {self.hash_value}:")
        for t in targets:
            print(f"  {t} ({format(t, f'0{self.num_bits}b')})")
        
        # Mark each target state
        for target in targets:
            # Apply X gates to create the target state pattern
            target_binary = format(target, f'0{self.num_bits}b')
            for i, bit in enumerate(target_binary):
                if bit == '0':
                    self.x(self.password_register[i])
            
            # Multi-controlled Z gate (phase flip on target state)
            self.h(self.ancilla_register[0])
            self.mct(
                list(self.password_register), 
                self.ancilla_register[0]
            )
            self.h(self.ancilla_register[0])
            
            # Undo the X gates
            for i, bit in enumerate(target_binary):
                if bit == '0':
                    self.x(self.password_register[i])
        
    def diffusion_operator(self) -> None:
        """
        Grover diffusion operator.
        """
        # Apply H gates
        for i in range(self.num_bits):
            self.h(self.password_register[i])
        
        # Apply phase flip about zero
        for i in range(self.num_bits):
            self.x(self.password_register[i])
            
        # Apply controlled-Z
        self.h(self.password_register[self.num_bits - 1])
        self.mct(
            [self.password_register[i] for i in range(self.num_bits - 1)],
            self.password_register[self.num_bits - 1]
        )
        self.h(self.password_register[self.num_bits - 1])
        
        # Undo X gates
        for i in range(self.num_bits):
            self.x(self.password_register[i])
        
        # Apply H gates again
        for i in range(self.num_bits):
            self.h(self.password_register[i])
    
    def create_grover_circuit(self) -> None:
        """
        Create a quantum circuit implementing Grover's algorithm.
        """
        # Initialize password register in superposition
        for i in range(self.num_bits):
            self.h(self.password_register[i])
        
        # Calculate optimal number of iterations
        iterations = int(np.pi/4 * np.sqrt(self.search_space_size))
        print(f"Using {iterations} Grover iterations")
        
        # Apply Grover iterations
        for _ in range(max(1, iterations)):
            self.oracle_for_hash()
            self.diffusion_operator()
        
        # Measure password register
        self.measure(self.password_register, self.cr)
    
    def find_password(self, shots: int = 1000) -> Dict[str, int]:
        """
        Try to find passwords that hash to the target hash value.
        
        Args:
            shots (int): Number of shots for the simulation
            
        Returns:
            Dict[str, int]: Measurement counts
        """
        # Create the circuit
        self.create_grover_circuit()
        
        # Use the Aer simulator
        simulator = AerSimulator()
        
        start_time = time.time()
        
        # Execute the circuit
        result = simulator.run(self, shots=shots).result()
        counts = result.get_counts()
        
        end_time = time.time()
        print(f"Quantum simulation took {end_time - start_time:.6f} seconds")
        
        return counts

def demonstrate_realistic_scenario():
    """
    Demonstrate a more realistic password cracking scenario.
    """
    # For demonstration purposes, we'll use a small number of bits
    num_bits = 2
    
    print(f"Demonstrating with {num_bits}-bit password")
    print(f"Search space size: {2**num_bits}")
    
    # Choose a random password
    original_password = np.random.randint(0, 2**num_bits)
    print(f"Original password: {original_password} ({format(original_password, f'0{num_bits}b')})")
    
    # Calculate its hash (in reality, this is all we would know)
    hash_value = simple_hash(original_password, num_bits)
    print(f"Hash value: {hash_value} ({format(hash_value, f'0{num_bits}b')})")
    
    # Create the password cracker
    print("\nCreating quantum circuit for password cracking...")
    cracker = RealisticPasswordCracker(num_bits, hash_value)
    
    # Try to crack the password
    print("\nRunning quantum password cracking simulation...")
    counts = cracker.find_password(shots=1000)
    
    # Analyze results
    print("\nMeasurement results:")
    for bitstring, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        password = int(bitstring, 2)
        is_correct = (simple_hash(password, num_bits) == hash_value)
        print(f"Password: {password} ({bitstring}), Count: {count}, Matches hash: {is_correct}")
    
    # Classical verification
    print("\nClassically verifying all possible passwords:")
    for i in range(2**num_bits):
        h = simple_hash(i, num_bits)
        if h == hash_value:
            print(f"Password {i} ({format(i, f'0{num_bits}b')}) hashes to {h}")

if __name__ == "__main__":
    demonstrate_realistic_scenario() 