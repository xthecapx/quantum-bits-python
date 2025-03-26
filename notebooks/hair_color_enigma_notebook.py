#!/usr/bin/env python3
"""
Hair Color Enigma Challenge - Notebook Content

This file contains code cells that can be copied into a Jupyter notebook
to explore both classical and quantum solutions to the Hair Color Enigma challenge.
"""

# %% [markdown]
# # The Hair Color Enigma Challenge
# 
# This notebook explores the "Four Hair Colors" enigma challenge from the Quantum Enigmas series. We'll implement and compare both classical and quantum solutions using the parity strategy.
# 
# ## Problem Statement
# 
# Four people (Alice, Bob, Charlie, and Dahlia) are lined up, with each person seeing only those in front of them. Each person's hair is randomly colored either orange or indigo. They must each guess their own hair color by speaking only one word ("orange" or "indigo").
# 
# The challenge: Develop a strategy that maximizes the number of correct guesses.

# %% [markdown]
# ## The Parity Strategy
# 
# The key insight is to use parity information (whether the number of indigo hairs is odd or even) rather than directly naming colors.
# 
# - **First person**: Counts the number of indigo hairs they see. Says "orange" if even, "indigo" if odd.
# - **Second person**: Based on what they see and what the first person said, deduces their own hair color.
# - **Third person**: Based on what they see and what the previous people said, deduces their own hair color.
# - **Fourth person**: Based on what they see and what the previous people said, deduces their own hair color.
# 
# This strategy guarantees that all but the first person will guess correctly. The first person has a 50% chance of being correct.

# %%
# Import dependencies
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

# Add parent directory to path so we can import our modules
sys.path.append(os.path.abspath('..'))

# %% [markdown]
# ## Classical Solution
# 
# First, let's import and use our classical implementation:

# %%
from experiments.hair_color_enigma import HairColorEnigma

# Create a new enigma with 4 people
enigma = HairColorEnigma(num_people=4)

# Run a single simulation with explicit hair colors for explanation
# 0 = orange, 1 = indigo
enigma.set_hair_colors([0, 0, 1, 0])  # Alice (orange), Bob (orange), Charlie (indigo), Dahlia (orange)
guesses, results = enigma.simulate_parity_strategy()
enigma.print_simulation_results()

# %% [markdown]
# ### Step-by-step Walkthrough
# 
# Let's walk through how the parity strategy works in detail:

# %%
def explain_strategy(hair_colors: List[int]):
    """Explain the parity strategy step by step for a given hair color configuration."""
    color_names = {0: "orange", 1: "indigo"}
    person_names = ["Alice", "Bob", "Charlie", "Dahlia"]
    
    print(f"Hair colors: {[color_names[c] for c in hair_colors]}")
    print("-" * 50)
    
    # Step 1: What Alice sees
    print(f"Step 1: {person_names[0]} sees {person_names[1]}, {person_names[2]}, and {person_names[3]}")
    visible_colors = hair_colors[1:]
    indigo_count = sum(visible_colors)
    parity = indigo_count % 2
    print(f"  {person_names[0]} sees {indigo_count} indigo hairs, which is {'odd' if parity == 1 else 'even'}")
    print(f"  {person_names[0]} says: '{color_names[parity]}'")
    print(f"  (This is {'correct' if parity == hair_colors[0] else 'incorrect'} for her own hair)")
    print()
    
    # Step 2: What Bob deduces
    print(f"Step 2: {person_names[1]} sees {person_names[2]} and {person_names[3]}")
    visible_colors = hair_colors[2:]
    indigo_count = sum(visible_colors)
    print(f"  {person_names[1]} sees {indigo_count} indigo hairs, which is {'odd' if indigo_count % 2 == 1 else 'even'}")
    print(f"  {person_names[1]} knows {person_names[0]} said '{color_names[parity]}'")
    
    # Bob's deduction
    if parity == indigo_count % 2:
        # If what Alice saw has the same parity as what Bob sees, 
        # Bob must have orange hair (0)
        bob_guess = 0
    else:
        # If what Alice saw has different parity from what Bob sees,
        # Bob must have indigo hair (1)
        bob_guess = 1
        
    print(f"  {person_names[1]} deduces his hair is '{color_names[bob_guess]}'")
    print(f"  (This is {'correct' if bob_guess == hair_colors[1] else 'incorrect'} for his own hair)")
    print()
    
    # Step 3: What Charlie deduces
    print(f"Step 3: {person_names[2]} sees {person_names[3]}")
    visible_colors = [hair_colors[3]]
    indigo_count = sum(visible_colors)
    print(f"  {person_names[2]} sees {indigo_count} indigo hairs, which is {'odd' if indigo_count % 2 == 1 else 'even'}")
    print(f"  {person_names[2]} knows {person_names[0]} said '{color_names[parity]}'")
    print(f"  {person_names[2]} knows {person_names[1]} has '{color_names[bob_guess]}' hair")
    
    # Charlie's deduction (XOR of all known parities)
    charlie_guess = parity ^ bob_guess ^ (indigo_count % 2)
    
    print(f"  {person_names[2]} deduces his hair is '{color_names[charlie_guess]}'")
    print(f"  (This is {'correct' if charlie_guess == hair_colors[2] else 'incorrect'} for his own hair)")
    print()
    
    # Step 4: What Dahlia deduces
    print(f"Step 4: {person_names[3]} sees no one")
    print(f"  {person_names[3]} knows {person_names[0]} said '{color_names[parity]}'")
    print(f"  {person_names[3]} knows {person_names[1]} has '{color_names[bob_guess]}' hair")
    print(f"  {person_names[3]} knows {person_names[2]} has '{color_names[charlie_guess]}' hair")
    
    # Dahlia's deduction (XOR of all known parities)
    dahlia_guess = parity ^ bob_guess ^ charlie_guess
    
    print(f"  {person_names[3]} deduces her hair is '{color_names[dahlia_guess]}'")
    print(f"  (This is {'correct' if dahlia_guess == hair_colors[3] else 'incorrect'} for her own hair)")
    print()
    
    # Summary
    correct_count = sum([
        parity == hair_colors[0],
        bob_guess == hair_colors[1],
        charlie_guess == hair_colors[2],
        dahlia_guess == hair_colors[3]
    ])
    
    print(f"Summary: {correct_count}/4 people guessed correctly")

# Example from the video
explain_strategy([0, 0, 1, 0])  # Alice (orange), Bob (orange), Charlie (indigo), Dahlia (orange)

# %% [markdown]
# ### Statistical Analysis with Classical Solution
# 
# Let's run multiple simulations to see the distribution of outcomes:

# %%
# Run 10,000 trials
stats = enigma.run_multiple_simulations(num_trials=10000)
enigma.print_statistics(stats)

# Visualization of results
correct_counts = list(stats["correct_distribution"].keys())
probabilities = list(stats["correct_distribution"].values())

plt.figure(figsize=(10, 6))
plt.bar(correct_counts, probabilities, color='blue', alpha=0.7)
plt.xlabel('Number of Correct Guesses')
plt.ylabel('Probability')
plt.title('Distribution of Correct Guesses in Hair Color Enigma (Classical Solution)')
plt.xticks(range(5))
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# %% [markdown]
# ### Testing with Different Numbers of People
# 
# The parity strategy can be generalized to any number of people. Let's see how it performs with different group sizes:

# %%
# Test with different numbers of people
people_counts = [2, 3, 4, 6, 8, 10]
avg_correct = []
success_rates = []

for count in people_counts:
    enigma = HairColorEnigma(num_people=count)
    stats = enigma.run_multiple_simulations(num_trials=5000)
    avg_correct.append(stats["avg_correct"])
    success_rates.append(stats["avg_correct"] / count)
    print(f"\nWith {count} people:")
    print(f"Average correct: {stats['avg_correct']:.2f}/{count} ({stats['avg_correct']/count:.2%})")
    print(f"All correct: {stats['correct_distribution'].get(count, 0):.2%}")

# Plot results
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(people_counts, avg_correct, 'bo-', linewidth=2)
plt.xlabel('Number of People')
plt.ylabel('Average Correct Guesses')
plt.title('Scaling of Correct Guesses')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(people_counts, success_rates, 'ro-', linewidth=2)
plt.xlabel('Number of People')
plt.ylabel('Success Rate')
plt.title('Success Rate vs. Group Size')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [markdown]
# ## Quantum Solution
# 
# Now let's implement and analyze the quantum solution:

# %%
from experiments.quantum_hair_color_enigma import QuantumHairColorEnigma, solve_hair_color_enigma

# Run the quantum solution with 4 people
enigma = solve_hair_color_enigma(num_people=4)

# %% [markdown]
# ### Examining the Quantum Circuit
# 
# Let's take a closer look at the quantum circuit for this problem:

# %%
# Display the quantum circuit with text representation
print("Circuit diagram (text representation):")
print(enigma.draw(output='text'))

# %% [markdown]
# ### Analyzing a Specific State
# 
# Let's analyze a specific state to understand how the quantum solution works:

# %%
# Let's analyze the state where:
# - The hair colors are: [orange, orange, indigo, orange] (0010)
# - The guesses are: [indigo, orange, indigo, orange] (1010)
# This corresponds to the example we worked through classically
enigma.print_state_analysis("10100010")

# %% [markdown]
# ## Comparing Classical and Quantum Approaches
# 
# Let's directly compare the classical and quantum solutions:

# %%
from experiments.compare_hair_color_solutions import run_classical_simulation, run_quantum_simulation, compare_results, plot_comparison

# Compare with 4 people
num_people = 4

# Run simulations
classical_stats = run_classical_simulation(num_people, num_trials=10000)
quantum_stats = run_quantum_simulation(num_people, shots_per_job=1024, num_jobs=10)

# Compare results
compare_results(classical_stats, quantum_stats, num_people)

# Plot comparison
plot_comparison(classical_stats, quantum_stats, num_people)

# %% [markdown]
# ## Conclusion
# 
# ### Key Findings
# 
# 1. **Parity Strategy Effectiveness**: The parity strategy guarantees that at least N-1 people (all except the first person) will guess correctly, and there's a 50% chance that all N people will guess correctly.
# 
# 2. **Quantum vs. Classical**: In both approaches we see similar results, as expected for this problem. The quantum approach demonstrates the same parity logic but implemented through quantum gates.
# 
# 3. **Scaling with Group Size**: As the number of people increases, the success rate approaches 1.0 as the impact of the first person's uncertainty becomes proportionally smaller.
# 
# ### Potential for Quantum Advantage
# 
# For this specific problem, the quantum solution doesn't provide a significant advantage over the classical approach in terms of success rate. However, the quantum implementation is interesting from an educational perspective as it demonstrates:
# 
# - How quantum gates can implement logical operations
# - The use of entanglement to represent information flow between people
# - How quantum superposition allows exploration of all possible hair color configurations simultaneously
# 
# With more advanced quantum algorithms (like Grover's algorithm), it might be possible to improve the first person's success rate beyond 50%, but that would require a different quantum circuit design. 