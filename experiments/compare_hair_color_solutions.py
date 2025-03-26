#!/usr/bin/env python3
"""
Hair Color Enigma - Comparison Script

This script compares classical and quantum solutions to the hair color enigma problem.
It runs simulations using both approaches and produces comparative statistics and visualizations.
"""

import matplotlib.pyplot as plt
import numpy as np
import time
from typing import Dict, List, Tuple

# Import solutions
from experiments.hair_color_enigma import HairColorEnigma
from experiments.quantum_hair_color_enigma import QuantumHairColorEnigma


def run_classical_simulation(num_people: int, num_trials: int) -> Dict:
    """
    Run a classical simulation of the hair color enigma.
    
    Args:
        num_people: Number of people in the challenge
        num_trials: Number of trials to run
        
    Returns:
        Dictionary with statistics about the simulation
    """
    print(f"Running classical simulation with {num_people} people ({num_trials} trials)...")
    start_time = time.time()
    
    enigma = HairColorEnigma(num_people=num_people)
    stats = enigma.run_multiple_simulations(num_trials=num_trials)
    
    stats["execution_time"] = time.time() - start_time
    return stats


def run_quantum_simulation(num_people: int, shots_per_job: int = 1024, num_jobs: int = 10) -> Dict:
    """
    Run a quantum simulation of the hair color enigma using the Qward framework.
    
    Args:
        num_people: Number of people in the challenge
        shots_per_job: Number of shots per job in the quantum simulation
        num_jobs: Number of jobs to run
        
    Returns:
        Dictionary with statistics about the simulation
    """
    print(f"Running quantum simulation with {num_people} people ({shots_per_job} shots x {num_jobs} jobs)...")
    start_time = time.time()
    
    # Create the validator
    enigma = QuantumHairColorEnigma(num_people=num_people)
    
    # Run simulation
    results = enigma.analyze_hair_colors(num_jobs=num_jobs, shots_per_job=shots_per_job, show_histogram=False)
    
    # Format results for comparison
    quantum_stats = {
        "num_people": num_people,
        "num_trials": num_jobs * shots_per_job,
        "avg_correct": results["success_rate"] * num_people + (1 - results["success_rate"]) * (num_people - 1),
        "first_person_correct_pct": results["first_person_correct_pct"],
        "per_person_correct_pct": results["per_person_correct_pct"],
        "all_correct_pct": results["success_rate"],
        "theoretical_success_rate": results["theoretical_rate"],
        "execution_time": results["timing_info"]["execution_time"],
        "circuit_metrics": results["circuit_metrics"],
        "correct_distribution": results["correct_distribution"],
        "raw_results": results
    }
    
    return quantum_stats


def compare_results(classical_stats: Dict, quantum_stats: Dict, num_people: int):
    """
    Compare results from classical and quantum simulations.
    
    Args:
        classical_stats: Statistics from classical simulation
        quantum_stats: Statistics from quantum simulation
        num_people: Number of people in the challenge
    """
    print("\n" + "=" * 80)
    print(f"COMPARISON OF CLASSICAL AND QUANTUM APPROACHES ({num_people} people)")
    print("=" * 80)
    
    # Theoretical calculations
    theoretical_max_success = 1 / (2 ** (num_people - 1))
    print("\nTheoretical Analysis:")
    print(f"  Maximum possible success rate (all correct): {theoretical_max_success:.4%}")
    print(f"  This is the mathematical limit for any strategy with this problem.")
    
    # Average correct answers
    classical_avg = classical_stats["avg_correct"]
    quantum_avg = quantum_stats["avg_correct"]
    max_possible_avg = theoretical_max_success * num_people + (1 - theoretical_max_success) * (num_people - 1)
    
    print(f"\nAverage correct answers:")
    print(f"  Classical: {classical_avg:.4f} / {num_people} ({classical_avg/num_people:.2%} accuracy)")
    print(f"  Quantum:   {quantum_avg:.4f} / {num_people} ({quantum_avg/num_people:.2%} accuracy)")
    print(f"  Theoretical maximum: {max_possible_avg:.4f} / {num_people} ({max_possible_avg/num_people:.2%} accuracy)")
    
    # Success rate (all correct)
    classical_all = classical_stats["correct_distribution"].get(num_people, 0)
    quantum_all = quantum_stats["all_correct_pct"]
    quantum_success_ratio = quantum_all / theoretical_max_success if theoretical_max_success > 0 else 0
    classical_success_ratio = classical_all / theoretical_max_success if theoretical_max_success > 0 else 0
    
    print(f"\nAll correct rate (success rate):")
    print(f"  Classical: {classical_all:.4%} ({classical_success_ratio:.2f}x theoretical maximum)")
    print(f"  Quantum:   {quantum_all:.4%} ({quantum_success_ratio:.2f}x theoretical maximum)")
    print(f"  Theoretical maximum: {theoretical_max_success:.4%}")
    
    # Check quantum implementation performance
    if abs(quantum_all - theoretical_max_success) < 0.02:  # Within 2% of theoretical
        print("  ✓ Quantum implementation is achieving near-optimal performance")
    elif quantum_all < theoretical_max_success * 0.9:  # Less than 90% of theoretical
        print("  ✗ Quantum implementation is underperforming relative to theoretical maximum")
    elif quantum_all > theoretical_max_success * 2:  # More than 2x theoretical maximum
        print("  ⚠️ Warning: Quantum implementation is reporting a success rate significantly above theoretical maximum")
        print("     This suggests a potential issue with the implementation or success criteria")
    
    # Check classical implementation performance
    if classical_all > theoretical_max_success * 2:  # More than 2x theoretical maximum
        print("  ⚠️ Warning: Classical implementation is reporting a success rate significantly above theoretical maximum")
        print("     This suggests a potential issue with the implementation or success criteria")
    elif abs(classical_all - theoretical_max_success) < 0.02:  # Within 2% of theoretical
        print("  ✓ Classical implementation is achieving near-optimal performance")
    
    # Per-person correct rates
    print("\nPer-person correct rates:")
    
    # First person correct
    classical_first = classical_stats["first_person_correct_pct"]
    quantum_first = quantum_stats["first_person_correct_pct"]
    print(f"  First person (theoretical ideal: 50%):")
    print(f"    Classical: {classical_first:.2%}")
    print(f"    Quantum:   {quantum_first:.2%}")
    
    # Other people
    if "per_person_correct_pct" in quantum_stats:
        quantum_per_person = quantum_stats["per_person_correct_pct"]
        print(f"  Individual success rates:")
        print("    Person | Classical (Expected) | Quantum (Measured)")
        print("    " + "-" * 50)
        for i in range(num_people):
            person_name = chr(65 + i)  # A, B, C, D, ...
            if i == 0:
                classical_expected = "50%"
            else:
                classical_expected = "100%"
            print(f"      {person_name}    | {classical_expected:^19} | {quantum_per_person[i]:^16.2%}")
        
        # Check if other people are close to 100% as expected
        other_people_avg = sum(quantum_per_person[1:]) / (num_people - 1) if num_people > 1 else 0
        print(f"  Other people average success rate: {other_people_avg:.2%} (Expected: 100%)")
        
        if other_people_avg < 0.9 and num_people > 1:  # Less than 90%
            print("  ⚠️ The quantum implementation's success rate for people 2-N is lower than expected")
            print("     This suggests the quantum circuit may not be implementing the ideal strategy")
    
    # Distribution of correct answers
    print("\nDistribution of correct answers:")
    print("  Number Correct | Classical | Quantum  | Theoretical Maximum")
    print("  " + "-" * 60)
    
    # Theoretical distribution
    theoretical_dist = {
        num_people: theoretical_max_success,
        num_people - 1: 1 - theoretical_max_success
    }
    
    for i in range(num_people + 1):
        classical_prob = classical_stats["correct_distribution"].get(i, 0)
        quantum_prob = quantum_stats["correct_distribution"].get(i, 0)
        theoretical_prob = theoretical_dist.get(i, 0)
        print(f"       {i:2d}       | {classical_prob:8.2%} | {quantum_prob:8.2%} | {theoretical_prob:8.2%}")
    
    # Execution time
    classical_time = classical_stats["execution_time"]
    quantum_time = quantum_stats["execution_time"]
    print(f"\nExecution time:")
    print(f"  Classical: {classical_time:.3f} seconds")
    print(f"  Quantum:   {quantum_time:.3f} seconds")
    
    # Interpretation
    print("\nInterpretation:")
    if num_people <= 2:
        print("  For 1-2 people, both classical and quantum approaches perform similarly.")
    else:
        print(f"  For {num_people} people:")
        
        if classical_all > quantum_all:
            diff_pct = (classical_all - quantum_all) / quantum_all * 100
            print(f"  - Classical solution achieves {diff_pct:.1f}% higher success rate than the quantum")
        elif quantum_all > classical_all:
            diff_pct = (quantum_all - classical_all) / classical_all * 100
            print(f"  - Quantum solution achieves {diff_pct:.1f}% higher success rate than the classical")
        else:
            print("  - Both solutions achieve identical success rates")
            
        if abs(quantum_first - 0.5) > 0.05:  # More than 5% from 50%
            print(f"  - First person's success rate in quantum ({quantum_first:.1%}) deviates from theoretical 50%")
        
        if "per_person_correct_pct" in quantum_stats:
            low_performers = [i+1 for i, rate in enumerate(quantum_stats["per_person_correct_pct"][1:], 1) if rate < 0.9]
            if low_performers:
                people_str = ", ".join([chr(65 + i - 1) for i in low_performers])
                print(f"  - People {people_str} have unexpectedly low success rates in the quantum implementation")
        
        print("\n  Key takeaways:")
        print("  - Both approaches demonstrate the same theoretical limit of correct guesses")
        print(f"  - The optimal strategy has a {theoretical_max_success:.4%} chance of all {num_people} people guessing correctly")
        print("  - When not all guesses are correct, the optimal strategy ensures only the first person is wrong")
        
        if abs(quantum_per_person[0] - 0.5) <= 0.05 and other_people_avg >= 0.9:
            print("  - The quantum implementation is correctly modeling the optimal strategy")
        else:
            print("  - The quantum implementation may need adjustment to fully match the optimal strategy")
    
    # Circuit metrics for quantum
    print("\nQuantum Circuit Metrics:")
    for metric, value in quantum_stats["circuit_metrics"].items():
        if isinstance(value, dict):
            print(f"  {metric}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {metric}: {value}")


def plot_comparison(classical_stats: Dict, quantum_stats: Dict, num_people: int):
    """
    Create comparative plots for classical and quantum simulations.
    
    Args:
        classical_stats: Statistics from classical simulation
        quantum_stats: Statistics from quantum simulation
        num_people: Number of people in the challenge
    """
    # Prepare data for plotting
    correct_values = list(range(num_people + 1))
    
    classical_probs = [classical_stats["correct_distribution"].get(i, 0) for i in correct_values]
    quantum_probs = [quantum_stats["correct_distribution"].get(i, 0) for i in correct_values]
    
    # Calculate theoretical distribution
    theoretical_max_success = 1 / (2 ** (num_people - 1))
    theoretical_probs = [0] * (num_people + 1)
    theoretical_probs[num_people] = theoretical_max_success
    theoretical_probs[num_people - 1] = 1 - theoretical_max_success
    
    # Create the plot
    plt.figure(figsize=(12, 7))
    
    bar_width = 0.25
    index = np.arange(len(correct_values))
    
    plt.bar(index - bar_width, classical_probs, bar_width, label="Classical", color="blue", alpha=0.7)
    plt.bar(index, quantum_probs, bar_width, label="Quantum", color="green", alpha=0.7)
    plt.bar(index + bar_width, theoretical_probs, bar_width, label="Theoretical Maximum", color="red", alpha=0.5)
    
    plt.xlabel("Number of Correct Guesses")
    plt.ylabel("Probability")
    plt.title(f"Distribution of Correct Guesses: Classical vs. Quantum ({num_people} people)")
    plt.xticks(index, correct_values)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    # Add a text box with key insights
    classical_all = classical_stats["correct_distribution"].get(num_people, 0)
    quantum_all = quantum_stats["all_correct_pct"]
    
    # Calculate success ratios
    quantum_success_ratio = quantum_all / theoretical_max_success if theoretical_max_success > 0 else 0
    classical_success_ratio = classical_all / theoretical_max_success if theoretical_max_success > 0 else 0
    
    textstr = f"Key Metrics:\n"
    textstr += f"All Correct (Classical): {classical_all:.2%}\n"
    textstr += f"All Correct (Quantum): {quantum_all:.2%}\n"
    textstr += f"Theoretical Maximum: {theoretical_max_success:.2%}\n"
    if quantum_all > theoretical_max_success * 1.1:
        textstr += f"⚠️ Quantum rate exceeds theoretical maximum by {quantum_success_ratio:.2f}x\n"
    if classical_all > theoretical_max_success * 1.1:
        textstr += f"⚠️ Classical rate exceeds theoretical maximum by {classical_success_ratio:.2f}x\n"
    textstr += f"Average Correct (Classical): {classical_stats['avg_correct']:.2f}/{num_people}\n"
    textstr += f"Average Correct (Quantum): {quantum_stats['avg_correct']:.2f}/{num_people}"
    
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    plt.figtext(0.15, 0.15, textstr, fontsize=10, verticalalignment="bottom", bbox=props)
    
    plt.tight_layout()
    plt.savefig(f"hair_color_comparison_{num_people}_people.png")
    plt.show()
    
    # Create a second plot showing how close each approach is to theoretical maximum
    plt.figure(figsize=(10, 6))
    
    # Normalize against theoretical maximum
    norm_classical = [min(c/t if t > 0 else 0, 1.0) for c, t in zip(classical_probs, theoretical_probs)]
    norm_quantum = [min(q/t if t > 0 else 0, 1.0) for q, t in zip(quantum_probs, theoretical_probs)]
    
    # Replace NaN or inf with 0
    norm_classical = [0 if not np.isfinite(x) else x for x in norm_classical]
    norm_quantum = [0 if not np.isfinite(x) else x for x in norm_quantum]
    
    plt.bar(index - bar_width/2, norm_classical, bar_width, label="Classical", color="blue", alpha=0.7)
    plt.bar(index + bar_width/2, norm_quantum, bar_width, label="Quantum", color="green", alpha=0.7)
    
    plt.axhline(y=1.0, color='r', linestyle='-', alpha=0.5, label="Theoretical Maximum")
    
    plt.xlabel("Number of Correct Guesses")
    plt.ylabel("Relative to Theoretical Maximum")
    plt.title(f"Efficiency Comparison: Classical vs. Quantum ({num_people} people)")
    plt.xticks(index, correct_values)
    plt.ylim(0, 1.1)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(f"hair_color_efficiency_{num_people}_people.png")
    plt.show()
    
    # Create a third plot showing per-person success rates
    if "per_person_correct_pct" in quantum_stats:
        plt.figure(figsize=(10, 6))
        
        # Per-person data
        people_labels = [chr(65 + i) for i in range(num_people)]  # A, B, C, D, ...
        quantum_rates = quantum_stats["per_person_correct_pct"]
        
        # Expected classical rates
        classical_expected = [0.5] + [1.0] * (num_people - 1)
        
        # Plot
        bar_width = 0.4
        index = np.arange(num_people)
        
        plt.bar(index - bar_width/2, classical_expected, bar_width, label="Classical (Expected)", color="blue", alpha=0.7)
        plt.bar(index + bar_width/2, quantum_rates, bar_width, label="Quantum (Measured)", color="green", alpha=0.7)
        
        plt.xlabel("Person")
        plt.ylabel("Success Rate")
        plt.title(f"Per-Person Success Rates: Classical vs. Quantum ({num_people} people)")
        plt.xticks(index, people_labels)
        plt.ylim(0, 1.1)
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(f"hair_color_per_person_{num_people}_people.png")
        plt.show()


def run_comparison(num_people=4, num_trials=10000, shots_per_job=1024, num_jobs=10):
    """
    Run the comparison between classical and quantum solutions with specified parameters.
    
    Args:
        num_people: Number of people in the challenge
        num_trials: Number of trials for classical simulation
        shots_per_job: Number of shots per job for quantum simulation
        num_jobs: Number of jobs for quantum simulation
        
    Returns:
        Tuple of (classical_stats, quantum_stats)
    """
    print("=" * 80)
    print(f"HAIR COLOR ENIGMA: CLASSICAL VS. QUANTUM COMPARISON")
    print("=" * 80)
    print(f"\nComparison parameters:")
    print(f"- Number of people: {num_people}")
    print(f"- Classical trials: {num_trials}")
    print(f"- Quantum shots: {shots_per_job} per job × {num_jobs} jobs = {shots_per_job * num_jobs} total")
    
    # Run classical simulation
    classical_stats = run_classical_simulation(num_people, num_trials)
    
    # Run quantum simulation
    quantum_stats = run_quantum_simulation(num_people, shots_per_job, num_jobs)
    
    # Compare and visualize results
    compare_results(classical_stats, quantum_stats, num_people)
    plot_comparison(classical_stats, quantum_stats, num_people)
    
    print(f"\nComparison complete. Plots saved as:")
    print(f"- 'hair_color_comparison_{num_people}_people.png'")
    print(f"- 'hair_color_efficiency_{num_people}_people.png'")
    print(f"- 'hair_color_per_person_{num_people}_people.png'")
    
    return classical_stats, quantum_stats


def main():
    """Run the comparison between classical and quantum solutions with default values."""
    # Hardcoded values for easy use in notebooks
    num_people = 4       # Number of people in the challenge
    num_trials = 10000   # Number of trials for classical simulation
    shots_per_job = 1024 # Number of shots per job for quantum simulation
    num_jobs = 10        # Number of jobs for quantum simulation
    
    # Run the comparison with hardcoded values
    run_comparison(num_people, num_trials, shots_per_job, num_jobs)


if __name__ == "__main__":
    main()

# Example of how to use this in a Jupyter notebook:
"""
# Hair Color Enigma: Classical vs Quantum Comparison

from experiments.compare_hair_color_solutions import run_comparison

# Run with default parameters (4 people)
classical_stats, quantum_stats = run_comparison()

# Run with 3 people and fewer trials for faster execution
classical_stats_3, quantum_stats_3 = run_comparison(
    num_people=3, 
    num_trials=5000,  # Fewer trials for classical
    shots_per_job=512,  # Fewer shots for quantum
    num_jobs=5  # Fewer jobs for quantum
)

# Extract and compare specific metrics
print(f"First person correct rate (Classical): {classical_stats['first_person_correct_pct']:.2%}")
print(f"First person correct rate (Quantum): {quantum_stats['first_person_correct_pct']:.2%}")

# Extract per-person success rates for quantum
quantum_per_person = quantum_stats['per_person_correct_pct']
for i, rate in enumerate(quantum_per_person):
    person = chr(65 + i)  # A, B, C, D, ...
    print(f"Person {person} success rate: {rate:.2%}")
""" 