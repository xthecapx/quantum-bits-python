from qward.validators.base_validator import BaseValidator
from qward.analysis.success_rate import SuccessRate

class QuantumEnigmaValidator(BaseValidator):
    def __init__(self):        
        # Initialize with named registers
        super().__init__(num_qubits=3, num_clbits=3, name="quantum_enigma")
        
        # Define success criteria: both guardians point to the same door
        # and that door is the one NOT to open (the door without the treasure)
        def success_criteria(state):
            # print(f"Analyzing state: {state}")  # Debug print
            lie_qubit = int(state[0])       # Which guardian is lying (0=q0, 1=q1)
            q1_guardian = int(state[1])     # q1 guardian's answer (0=right door, 1=left door)
            q0_guardian = int(state[2])     # q0 guardian's answer (0=right door, 1=left door)
            
            # Both guardians should point to the same door
            if q0_guardian != q1_guardian:
                print(f"  Failed: Guardians point to different doors")
                return False

            result = q1_guardian == q0_guardian
            return result
        
        # Add the success rate analysis with the criteria
        success_analyzer = SuccessRate()
        success_analyzer.set_success_criteria(success_criteria)
        self.add_analyzer(success_analyzer)
        
        # Setup the circuit
        self._setup_circuit()
    
    def _setup_circuit(self):
        # Place treasure randomly using Hadamard gate on q0
        self.h(0)  # q0: Right guardian's knowledge
        
        # Ensure both guardians know the same thing using CNOT
        self.cx(0, 1)  # q1: Left guardian's knowledge
        
        if self.use_barriers:
            self.barrier()
        
        # Add lie qubit in superposition
        self.h(2)  # q2: Which guardian is lying (0=right, 1=left)
        
        # First liar detection step
        self.cx(2, 1)  # If q2 is 1, left guardian lies
        self.x(2)      # Flip the lie qubit
        self.cx(2, 0)  # If q2 is 0, right guardian lies
        self.x(2)      # Flip the lie qubit back
        
        if self.use_barriers:
            self.barrier()
        
        # Which door would the other guardian tell me not to open?
        # Apply the "what would the other guardian say" logic
        # First, swap the guardians' knowledge
        self.swap(0, 1)  # Swap right and left guardian knowledge
        
        # Apply NOT gates to represent "not to open"
        self.x(0)  # NOT on right guardian's answer
        self.x(1)  # NOT on left guardian's answer
        
        if self.use_barriers:
            self.barrier()
        
        # Second liar detection step
        self.cx(2, 1)  # If q2 is 1, left guardian lies
        self.x(2)      # Flip the lie qubit
        self.cx(2, 0)  # If q2 is 0, right guardian lies
        self.x(2)      # Flip the lie qubit back
        
        # Measure all qubits
        self.measure([0, 1, 2], [0, 1, 2])

def solve_quantum_enigma():
    # Create and run the quantum enigma validator
    validator = QuantumEnigmaValidator()
    
    # Run simulation with histogram
    results = validator.run_simulation(show_histogram=True, num_jobs=1000, shots_per_job=1000)
    
    # Print the results
    print("\nQuantum Enigma Results:")
    print("------------------------")
    for state, count in results["results_metrics"]["counts"].items():
        # state format: [lie_qubit, q1_guardian, q0_guardian]
        lie_qubit = state[0]      # Which guardian is lying (0=q0, 1=q1)
        q1_guardian = state[1]    # q1 guardian's answer (0=right door, 1=left door)
        q0_guardian = state[2]    # q0 guardian's answer (0=right door, 1=left door)
        
        # Determine where the treasure is
        # If both guardians point to the same door, that's the door NOT to open
        # So the treasure is behind the opposite door
        if q0_guardian == q1_guardian:
            # If they both point to right door (0), treasure is behind left door (1)
            # If they both point to left door (1), treasure is behind right door (0)
            treasure_door = '1' if q0_guardian == '0' else '0'
        else:
            treasure_door = 'unknown'  # This shouldn't happen in our circuit
        
        print(f"State {state}: {count} times")
        print(f"  Guardian lying: {'q1' if lie_qubit == '1' else 'q0'}")
        print(f"  q1 guardian points to: {'Right' if q1_guardian == '0' else 'Left'} door")
        print(f"  q0 guardian points to: {'Right' if q0_guardian == '0' else 'Left'} door")
        print(f"  Treasure is behind: {'Right' if treasure_door == '0' else 'Left'} door")
        print("  ---")
    
    # Print circuit metrics
    print("\nCircuit Metrics:")
    print("---------------")
    for metric, value in results["circuit_metrics"].items():
        print(f"{metric}: {value}")
    
    # Print success analysis
    print("\nSuccess Analysis:")
    print("----------------")
    analysis_results = validator.run_analysis()
    analysis = analysis_results["analyzer_0"]  # Get the first analyzer's results
    print(f"Mean success rate: {analysis['mean_success_rate']:.2%}")
    print(f"Standard deviation: {analysis['std_success_rate']:.2%}")
    print(f"Min success rate: {analysis['min_success_rate']:.2%}")
    print(f"Max success rate: {analysis['max_success_rate']:.2%}")
    print(f"Total trials: {analysis['total_trials']}")
    
    # Plot analysis results
    print("\nGenerating analysis plots...")
    validator.plot_analysis(ideal_rate=1.0)
    
    return validator

if __name__ == "__main__":
    validator = solve_quantum_enigma()
    print("\nCircuit:")
    validator.draw()  # This will use the matplotlib output 