import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Try importing
try:
    from qward.validators.teleportation_validator import TeleportationValidator
    from qward.experiments.experiments import Experiments
    print("Imports successful!")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}") 