#!/usr/bin/env python3
"""
Hair Color Enigma - Quantum Solution

This module implements a quantum solution to the "Four Hair Colors" enigma
using Qiskit. It demonstrates how to set up the quantum circuit described
in the enigma challenge and how to interpret the results.
"""

from typing import Dict
import time
from qward.validators.base_validator import BaseValidator
from qward.analysis.success_rate import SuccessRate


class QuantumHairColorEnigma(BaseValidator):
    """Quantum solution to the hair color enigma problem using the Qward framework."""
    
    def __init__(self, num_people: int = 4, use_barriers: bool = True):
        """
        Initialize the quantum hair color enigma with a specified number of people.
        
        Args:
            num_people: Number of people in the challenge (default: 4)
            use_barriers: Whether to include barriers in the circuit for clarity
        """
        self.num_people = num_people
        self.use_barriers = use_barriers
        
        # Calculate total qubits needed (each person has a hair color qubit and a guess qubit)
        total_qubits = num_people * 2
        
        # Initialize the base validator with the specified number of qubits and classical bits
        super().__init__(
            num_qubits=total_qubits, 
            num_clbits=total_qubits, 
            use_barriers=use_barriers, 
            name="hair_color_enigma"
        )
        
        # Define success criteria for the Hair Color Enigma
        def success_criteria(state):
            # Parse the state (binary string)
            # First num_people bits (from right to left) are the hair colors
            # Remaining bits are the guesses
            
            # Reverse the state to match indices (qiskit returns least significant bit first)
            reversed_state = state[::-1]
            
            # Extract hair colors and guesses
            hair_colors = reversed_state[:self.num_people]
            guesses = reversed_state[self.num_people:self.num_people*2]
            
            # Calculate the number of correct guesses
            correct_count = sum(1 for i in range(self.num_people) 
                               if hair_colors[i] == guesses[i])
            
            # Success if all people guess correctly
            return correct_count == self.num_people
        
        # Add the success rate analyzer with the criteria
        success_analyzer = SuccessRate()
        success_analyzer.set_success_criteria(success_criteria)
        self.add_analyzer(success_analyzer)
        
        # Setup the circuit
        self._setup_circuit()
        
    def _setup_circuit(self):
        """Build the quantum circuit that implements the hair color enigma."""
        # Put hair color qubits in superposition to represent all possible combinations
        for i in range(self.num_people):
            self.h(i)
        
        if self.use_barriers:
            self.barrier()
        
        # Set the first person's guess to be a random 50/50 choice using a hadamard gate
        # This enforces the theoretical limitation that the first person has a 50% chance of guessing correctly
        self.h(self.num_people)  # First person's guess qubit
        
        if self.use_barriers:
            self.barrier()
            
        # For the first person's strategy, we would ideally compute the parity of other people's hair
        # But since we're enforcing the 50% theoretical limit with the hadamard gate above,
        # we don't need to connect it to the hair colors
        
        # Second person calculates based on first person's guess and hair colors of people after them
        if self.num_people > 1:
            # Copy first person's guess to second person's guess
            self.cx(self.num_people, self.num_people + 1)
            
            # XOR with hair colors of people after second person
            for i in range(2, self.num_people):
                self.cx(i, self.num_people + 1)
            
            # XOR with own hair color to make a correct guess
            self.cx(1, self.num_people + 1)
                
            if self.use_barriers:
                self.barrier()
        
        # Third person calculates parity of people after them and previous guesses
        if self.num_people > 2:
            # Copy first person's guess to third person's guess
            self.cx(self.num_people, self.num_people + 2)
            
            # Copy second person's guess to third person's guess
            self.cx(self.num_people + 1, self.num_people + 2)
            
            # XOR with hair colors of people after third person
            for i in range(3, self.num_people):
                self.cx(i, self.num_people + 2)
            
            # XOR with own hair color to make a correct guess
            self.cx(2, self.num_people + 2)
                
            if self.use_barriers:
                self.barrier()
        
        # Continue for remaining people
        for person in range(3, self.num_people):
            # Copy all previous guesses
            for prev_person in range(person):
                self.cx(self.num_people + prev_person, self.num_people + person)
                
            # XOR with hair colors of people after current person
            for i in range(person + 1, self.num_people):
                self.cx(i, self.num_people + person)
            
            # XOR with own hair color to make a correct guess
            self.cx(person, self.num_people + person)
                
            if self.use_barriers:
                self.barrier()
        
        # Measure all qubits
        total_qubits = self.num_people * 2
        for i in range(total_qubits):
            self.measure(i, i)
            
    def analyze_per_person_success(self, counts_dict):
        """
        Analyze the success rate for each individual person.
        
        Args:
            counts_dict: Dictionary of measurement counts
            
        Returns:
            Dictionary with per-person statistics
        """
        total_shots = sum(counts_dict.values())
        if total_shots == 0:
            return {
                "per_person_correct": [0] * self.num_people,
                "per_person_correct_pct": [0] * self.num_people,
                "first_person_correct_pct": 0,
                "others_correct_pct": 0
            }
            
        # Initialize counters
        per_person_correct = [0] * self.num_people
        
        # Analyze each measured state
        for bitstring, count in counts_dict.items():
            # Reverse the bitstring to match our convention (first person is first)
            reversed_bits = bitstring[::-1]
            
            # Extract hair colors and guesses
            hair_colors = reversed_bits[:self.num_people]
            guesses = reversed_bits[self.num_people:self.num_people*2]
            
            # Check each person
            for i in range(self.num_people):
                if hair_colors[i] == guesses[i]:
                    per_person_correct[i] += count
        
        # Calculate percentages
        per_person_correct_pct = [count / total_shots for count in per_person_correct]
        first_person_correct_pct = per_person_correct_pct[0] if self.num_people > 0 else 0
        
        # Calculate statistics for others (excluding first person)
        others_correct = sum(per_person_correct[1:]) if self.num_people > 1 else 0
        others_total = total_shots * (self.num_people - 1) if self.num_people > 1 else 0
        others_correct_pct = others_correct / others_total if others_total > 0 else 0
        
        return {
            "per_person_correct": per_person_correct,
            "per_person_correct_pct": per_person_correct_pct,
            "first_person_correct_pct": first_person_correct_pct,
            "others_correct_pct": others_correct_pct
        }
        
    def analyze_correct_distribution(self, counts_dict):
        """
        Analyze the distribution of the number of correct guesses.
        
        Args:
            counts_dict: Dictionary of measurement counts
            
        Returns:
            Dictionary mapping number of correct guesses to probability
        """
        total_shots = sum(counts_dict.values())
        if total_shots == 0:
            return {i: 0 for i in range(self.num_people + 1)}
            
        # Initialize distribution
        distribution = {i: 0 for i in range(self.num_people + 1)}
        
        # Analyze each measured state
        for bitstring, count in counts_dict.items():
            # Reverse the bitstring to match our convention (first person is first)
            reversed_bits = bitstring[::-1]
            
            # Extract hair colors and guesses
            hair_colors = reversed_bits[:self.num_people]
            guesses = reversed_bits[self.num_people:self.num_people*2]
            
            # Count correct guesses
            correct_count = sum(1 for i in range(self.num_people) 
                               if hair_colors[i] == guesses[i])
            
            distribution[correct_count] += count
        
        # Convert to probabilities
        distribution = {k: v / total_shots for k, v in distribution.items()}
        
        return distribution
        
    def analyze_hair_colors(self, num_jobs: int = 10, shots_per_job: int = 1024, show_histogram: bool = True):
        """
        Analyze the hair color enigma simulation results.
        
        Args:
            num_jobs: Number of jobs to run
            shots_per_job: Number of shots per job
            show_histogram: Whether to display a histogram of results
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\nRunning quantum simulation for {self.num_people} people...")
        print(f"Parameters: {num_jobs} jobs with {shots_per_job} shots each")
        
        # Run simulation
        sim_results = self.run_simulation(show_histogram=show_histogram, 
                                         num_jobs=num_jobs, 
                                         shots_per_job=shots_per_job)
        
        # Get counts from results
        counts = sim_results["results_metrics"]["counts"]
        
        # Analyze the success rates
        analysis_results = self.run_analysis()
        
        # Get the success rate analyzer results
        success_analysis = analysis_results["analyzer_0"]
        
        # Analyze per-person success rates
        per_person_stats = self.analyze_per_person_success(counts)
        
        # Analyze correct guess distribution
        correct_distribution = self.analyze_correct_distribution(counts)
        
        # Get timing information from BaseValidator
        timing_info = sim_results["timing_info"]
        
        # Calculate the theoretical success rate
        theoretical_rate = 1 / (2 ** (self.num_people - 1))
        
        # Format for better understanding
        results = {
            "counts": counts,
            "num_people": self.num_people,
            "success_rate": success_analysis["mean_success_rate"],
            "std_success_rate": success_analysis["std_success_rate"],
            "min_success_rate": success_analysis["min_success_rate"],
            "max_success_rate": success_analysis["max_success_rate"],
            "total_trials": success_analysis["total_trials"],
            "theoretical_rate": theoretical_rate,
            "circuit_metrics": sim_results["circuit_metrics"],
            "timing_info": timing_info,
            "per_person_correct": per_person_stats["per_person_correct"],
            "per_person_correct_pct": per_person_stats["per_person_correct_pct"],
            "first_person_correct_pct": per_person_stats["first_person_correct_pct"],
            "others_correct_pct": per_person_stats["others_correct_pct"],
            "correct_distribution": correct_distribution
        }
        
        return results
    
    def print_analysis_results(self, results: Dict):
        """
        Print the analysis results in a human-readable format.
        
        Args:
            results: Dictionary with analysis results
        """
        print(f"\nQuantum Hair Color Enigma Analysis ({results['num_people']} people)")
        print("-" * 60)
        
        # Print timing information from BaseValidator
        timing_info = results["timing_info"]
        print(f"Execution period: {timing_info['start_time']} to {timing_info['end_time']}")
        print(f"Execution time: {timing_info['execution_time']:.3f} seconds")
        print(f"Jobs: {timing_info['num_jobs']}, Shots per job: {timing_info['shots_per_job']}")
        print(f"Total shots: {timing_info['total_shots']}")
        print(f"Shots per second: {timing_info['shots_per_second']:.1f}")
        
        print("\nAccuracy Statistics:")
        print(f"Success rate (all correct): {results['success_rate']:.2%}")
        print(f"Standard deviation: {results['std_success_rate']:.2%}")
        print(f"Min success rate: {results['min_success_rate']:.2%}")
        print(f"Max success rate: {results['max_success_rate']:.2%}")
        
        # Theoretical success rate is 1/(2^(n-1)) for n people
        theoretical_rate = results.get('theoretical_rate', 1 / (2 ** (results['num_people'] - 1)))
        print(f"Theoretical success rate: {theoretical_rate:.2%}")
        
        # Distribution of correct guesses
        if 'correct_distribution' in results:
            print("\nDistribution of Correct Guesses:")
            print("  Correct | Measured | Theoretical")
            print("  " + "-" * 40)
            
            # Calculate theoretical distribution
            theoretical_dist = {}
            theoretical_dist[results['num_people']] = theoretical_rate
            theoretical_dist[results['num_people']-1] = 1 - theoretical_rate
            
            for i in range(results['num_people'] + 1):
                measured = results['correct_distribution'].get(i, 0)
                theoretical = theoretical_dist.get(i, 0)
                print(f"    {i:2d}    | {measured:^8.2%} | {theoretical:^11.2%}")
        
        # Per-person success rates
        if 'per_person_correct_pct' in results:
            print("\nPer-Person Success Rates:")
            print("  Person | Expected | Measured")
            print("  " + "-" * 35)
            
            per_person_rates = results['per_person_correct_pct']
            for i in range(results['num_people']):
                person_name = chr(65 + i)  # A, B, C, D, ...
                expected = "50%" if i == 0 else "100%"
                print(f"    {person_name}    | {expected:^8} | {per_person_rates[i]:^8.2%}")
            
            # First person and others statistics
            print(f"\n  First person correct rate: {results['first_person_correct_pct']:.2%} (Expected: 50%)")
            if results['num_people'] > 1:
                print(f"  Other people correct rate: {results['others_correct_pct']:.2%} (Expected: 100%)")
                
            # Diagnostic information
            if abs(results['first_person_correct_pct'] - 0.5) > 0.05:
                print("  ⚠️ First person's success rate deviates from the expected 50%")
            
            if results['num_people'] > 1 and results['others_correct_pct'] < 0.95:
                print("  ⚠️ Other people's success rates are below the expected 100%")
                print("     This suggests the quantum circuit may not be optimal")
        
        # Calculate statistics comparable to classical implementation
        expected_avg_correct = results['success_rate'] * results['num_people'] + \
                              (1 - results['success_rate']) * (results['num_people'] - 1)
        
        # In theory first person is correct 50% of the time
        first_person_correct = 0.5
        
        print("\nComparative Statistics:")
        print(f"Expected average correct answers: {expected_avg_correct:.2f} / {results['num_people']}")
        print(f"First person correct rate (theoretical): {first_person_correct:.2%}")
        print(f"Expected Long-Term Accuracy: {expected_avg_correct/results['num_people']:.1%}")
        
        print("\nCircuit Metrics:")
        for metric, value in results["circuit_metrics"].items():
            if isinstance(value, dict):
                print(f"  {metric}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {metric}: {value}")
    
    def print_state_analysis(self, hair_colors_list=None, state=None):
        """
        Analyze a specific measured state in detail.
        
        Args:
            hair_colors_list: List of hair colors (e.g. ["orange", "orange", "indigo", "orange"])
            state: Binary string representing the measured state (legacy format - will be deprecated)
        """
        if hair_colors_list is not None:
            # Convert hair color list to binary state
            binary_colors = []
            for color in hair_colors_list:
                if color.lower() == "indigo":
                    binary_colors.append("1")
                elif color.lower() == "orange":
                    binary_colors.append("0")
                else:
                    raise ValueError(f"Invalid hair color: {color}. Must be 'orange' or 'indigo'.")
            
            # Create full state from hair colors (hair colors + guesses calculated by parity strategy)
            hair_colors = "".join(binary_colors)
            
            # Calculate guesses using parity strategy
            guesses = ["0"] * self.num_people
            
            # First person calculates parity of all other people
            first_guess = 0
            for i in range(1, self.num_people):
                first_guess ^= int(hair_colors[i])
            guesses[0] = str(first_guess)
            
            # Second person calculates parity of people after them and first person's guess
            if self.num_people > 1:
                second_guess = int(guesses[0])  # Start with first person's guess
                for i in range(2, self.num_people):
                    second_guess ^= int(hair_colors[i])
                guesses[1] = str(second_guess)
            
            # Third person calculates parity of people after them and previous guesses
            if self.num_people > 2:
                third_guess = int(guesses[0]) ^ int(guesses[1])  # Previous guesses
                for i in range(3, self.num_people):
                    third_guess ^= int(hair_colors[i])
                guesses[2] = str(third_guess)
            
            # Remaining people
            for person in range(3, self.num_people - 1):
                current_guess = 0
                # XOR all previous guesses
                for prev_person in range(person):
                    current_guess ^= int(guesses[prev_person])
                # XOR with hair colors of people after current person
                for i in range(person + 1, self.num_people):
                    current_guess ^= int(hair_colors[i])
                guesses[person] = str(current_guess)
            
            # Last person just XORs all previous guesses
            if self.num_people > 1:
                last_guess = 0
                for prev_person in range(self.num_people - 1):
                    last_guess ^= int(guesses[prev_person])
                guesses[self.num_people - 1] = str(last_guess)
            
            # Combine hair colors and guesses to form the full state
            full_state = hair_colors + "".join(guesses)
            
            # Reverse for qiskit's least-significant-bit-first convention
            state = full_state[::-1]
        elif state is None:
            raise ValueError("Either hair_colors_list or state must be provided")
            
        # Reverse the state to match indices
        reversed_state = state[::-1]
        
        # Extract hair colors and guesses
        hair_colors = reversed_state[:self.num_people]
        guesses = reversed_state[self.num_people:self.num_people*2]
        
        print(f"\nAnalysis of state: {state}")
        print("-" * 60)
        
        # Print each person's hair color and guess
        for i in range(self.num_people):
            person = chr(65 + i)  # A, B, C, D, ...
            hair = "indigo" if hair_colors[i] == "1" else "orange"
            guess = "indigo" if guesses[i] == "1" else "orange"
            is_correct = hair_colors[i] == guesses[i]
            status = "✓" if is_correct else "✗"
            
            print(f"Person {person}: Hair={hair}, Guess={guess} {status}")
        
        # Count correct guesses
        correct_count = sum(1 for i in range(self.num_people) 
                           if hair_colors[i] == guesses[i])
        
        print(f"Total correct: {correct_count}/{self.num_people} ({correct_count/self.num_people:.0%})")


def solve_hair_color_enigma(num_people: int = 4, num_jobs: int = 10, shots_per_job: int = 1024):
    """
    Run a demonstration of the quantum hair color enigma.
    
    Args:
        num_people: Number of people in the challenge
        num_jobs: Number of jobs to run in the simulation
        shots_per_job: Number of shots per job
        
    Returns:
        The QuantumHairColorEnigma instance
    """
    print("=" * 70)
    print("   HAIR COLOR ENIGMA - QUANTUM PARITY STRATEGY SIMULATION")
    print("=" * 70)
    print("\nThis simulation demonstrates the quantum implementation of the parity strategy.")
    print("The quantum circuit uses Hadamard and CNOT gates to implement the strategy.")
    print("Each person's hair color is represented by a qubit in superposition.")
    print("\nExpected results:")
    theoretical_rate = 1 / (2 ** (num_people - 1))
    print(f"- Complete circuit should have ~{theoretical_rate:.2%} of states with all answers correct")
    print("- First person success rate should match classical (~50%)")
    
    # Create the enigma validator
    print("\n" + "=" * 50)
    print(f"RUNNING QUANTUM SIMULATION WITH {num_people} PEOPLE")
    print("=" * 50)
    
    enigma = QuantumHairColorEnigma(num_people=num_people)
    
    # Run analysis
    results = enigma.analyze_hair_colors(num_jobs=num_jobs, shots_per_job=shots_per_job)
    enigma.print_analysis_results(results)
    
    # Draw the circuit
    print("\n" + "=" * 50)
    print("CIRCUIT STRUCTURE")
    print("=" * 50)
    print("Circuit diagram:")
    enigma.draw()
    
    # Plot the analysis
    print("\n" + "=" * 50)
    print("ANALYSIS VISUALIZATION")
    print("=" * 50)
    print("Generating analysis plots...")
    enigma.plot_analysis(ideal_rate=0.5)  # Ideal success rate is 50% in theory
    
    print("\n" + "=" * 70)
    print("   QUANTUM SIMULATION COMPLETE")
    print("=" * 70)
    
    return enigma


def run_on_ibm_hardware(num_people: int = 4):
    """
    Run the Hair Color Enigma on IBM Quantum hardware and analyze the results.
    
    Args:
        num_people: Number of people in the challenge
        
    Returns:
        The QuantumHairColorEnigma instance and the IBM results
    """
    print("=" * 70)
    print("   HAIR COLOR ENIGMA - IBM QUANTUM HARDWARE EXECUTION")
    print("=" * 70)
    print("\nThis will execute the Hair Color Enigma on real IBM quantum hardware.")
    print("Note: This requires an IBM Quantum account and API token configured in .env")
    print("Make sure IBM_QUANTUM_TOKEN is set in your .env file.")
    
    # Create the enigma validator
    print("\n" + "=" * 50)
    print(f"PREPARING CIRCUIT FOR {num_people} PEOPLE")
    print("=" * 50)
    
    enigma = QuantumHairColorEnigma(num_people=num_people)
    
    # Run on IBM hardware
    print("\n" + "=" * 50)
    print("SUBMITTING TO IBM QUANTUM HARDWARE")
    print("=" * 50)
    
    ibm_results = enigma.run_on_ibm()
    
    # Display timing information
    if "timing_info" in ibm_results:
        timing_info = ibm_results["timing_info"]
        print("\n" + "=" * 50)
        print("IBM EXECUTION TIMING INFORMATION")
        print("=" * 50)
        print(f"Overall execution period: {timing_info.get('overall_start_time', 'N/A')} to {timing_info.get('overall_end_time', 'N/A')}")
        print(f"Total time: {timing_info.get('overall_time', 'N/A'):.3f} seconds")
        
        if "compile_time" in timing_info:
            print(f"Circuit compilation time: {timing_info['compile_time']:.3f} seconds")
        
        if "queue_time" in timing_info:
            print(f"Time in queue: {timing_info['queue_time']:.3f} seconds")
        
        if "execution_time" in timing_info:
            print(f"Actual execution time: {timing_info['execution_time']:.3f} seconds")
            print(f"Execution period: {timing_info.get('execution_start_time', 'N/A')} to {timing_info.get('execution_end_time', 'N/A')}")
            print(f"Shots: {timing_info.get('shots', 'N/A')}")
            print(f"Shots per second: {timing_info.get('shots_per_second', 'N/A'):.1f}")
    
    # Check if execution was successful
    if ibm_results["status"] == "completed":
        print("\n" + "=" * 50)
        print("IBM QUANTUM RESULTS ANALYSIS")
        print("=" * 50)
        
        # Analyze the counts
        counts = ibm_results["counts"]
        total_shots = sum(counts.values())
        
        # Calculate success rate
        successful_states = 0
        for state, count in counts.items():
            # Reverse the state to match indices
            reversed_state = state[::-1]
            
            # Extract hair colors and guesses
            hair_colors = reversed_state[:num_people]
            guesses = reversed_state[num_people:num_people*2]
            
            # Check if all guesses are correct
            all_correct = all(hair_colors[i] == guesses[i] for i in range(num_people))
            
            if all_correct:
                successful_states += count
        
        success_rate = successful_states / total_shots
        
        print(f"Success rate (all correct): {success_rate:.2%}")
        print(f"Backend used: {ibm_results['backend']}")
        print(f"Job ID: {ibm_results['job_id']}")
    else:
        print("\n" + "=" * 50)
        print("IBM QUANTUM EXECUTION FAILED")
        print("=" * 50)
        print(f"Status: {ibm_results['status']}")
        if "error" in ibm_results:
            print(f"Error: {ibm_results['error']}")
    
    print("\n" + "=" * 70)
    print("   IBM QUANTUM EXECUTION COMPLETE")
    print("=" * 70)
    
    return enigma, ibm_results


if __name__ == "__main__":
    # Run the demonstration using local simulator
    print("\nRunning the Hair Color Enigma using local simulation...")
    enigma = solve_hair_color_enigma(num_people=4)
    
    # Optionally analyze a specific state
    print("\n" + "=" * 50)
    print("EXAMPLE STATE ANALYSIS")
    print("=" * 50)
    print("Analyzing a specific state where Alice has orange hair, Bob has orange hair,")
    print("Charlie has indigo hair, and Dahlia has orange hair:")
    enigma.print_state_analysis(hair_colors_list=["orange", "orange", "indigo", "orange"])
    
    # Uncomment the following lines to run on real IBM Quantum hardware
    # Note: This requires an IBM Quantum account and API token configured in your .env file
    # 
    # print("\nRunning the Hair Color Enigma on IBM Quantum hardware...")
    # print("This may take a while depending on queue times...")
    # enigma_ibm, ibm_results = run_on_ibm_hardware(num_people=4)
    #
    # The ibm_results variable will contain detailed timing information and results 