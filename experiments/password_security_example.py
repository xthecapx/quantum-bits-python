import hashlib
import bcrypt
import time
import math
from typing import Tuple

def demonstrate_sha256(password: str) -> str:
    """Demonstrates how SHA-256 works (NOT recommended for password storage)"""
    return hashlib.sha256(password.encode()).hexdigest()

def proper_password_storage(password: str) -> Tuple[str, str]:
    """Shows proper password storage using bcrypt"""
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return salt.decode(), hashed.decode()

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a password against its stored hash"""
    return bcrypt.checkpw(password.encode(), stored_hash.encode())

def simulate_quantum_cracking(password: str, hashed_password: str):
    """Simulates theoretical quantum password cracking using Grover's algorithm principles"""
    print("\nSimulating quantum password cracking (theoretical):")
    
    # In a real quantum computer, Grover's algorithm would search in O(sqrt(N)) time
    # where N is the number of possible combinations
    # For demonstration, we'll simulate this by reducing the search space
    start_time = time.time()
    attempts = 0
    max_attempts = 100  # Reduced for quantum simulation
    
    # Simulate quantum parallel search
    for i in range(max_attempts):
        attempts += 1
        # Simulate checking multiple passwords simultaneously (quantum superposition)
        test_passwords = [f"test{j:03d}" for j in range(i*10, (i+1)*10)]
        for test_password in test_passwords:
            if verify_password(test_password, hashed_password):
                end_time = time.time()
                print(f"Found password after {attempts} quantum attempts!")
                print(f"Time taken: {end_time - start_time:.2f} seconds")
                return
    
    end_time = time.time()
    print(f"Time taken for {attempts} quantum attempts: {end_time - start_time:.2f} seconds")
    print("Note: This is a simplified simulation. Real quantum computers would be much faster")

def demonstrate_cracking_difficulty(password: str, hashed_password: str):
    """Demonstrates why password cracking is difficult"""
    print("\nDemonstrating classical password cracking difficulty:")
    
    start_time = time.time()
    attempts = 0
    max_attempts = 1000  # Limiting for demonstration
    
    for i in range(max_attempts):
        attempts += 1
        test_password = f"test{i:03d}"
        if verify_password(test_password, hashed_password):
            print(f"Found password after {attempts} attempts!")
            break
    
    end_time = time.time()
    print(f"Time taken for {attempts} attempts: {end_time - start_time:.2f} seconds")
    print("Note: This is just a demonstration. Real password cracking would take much longer")
    print("and would need to try many more combinations!")

def main():
    # Example password
    password = "MySecurePassword123!"
    
    # 1. Demonstrating SHA-256 (NOT for password storage)
    sha256_hash = demonstrate_sha256(password)
    print(f"Original password: {password}")
    print(f"SHA-256 hash: {sha256_hash}")
    print(f"SHA-256 hash length: {len(sha256_hash)} characters")
    
    # 2. Proper password storage with bcrypt
    salt, hashed_password = proper_password_storage(password)
    print(f"\nProper password storage:")
    print(f"Salt: {salt}")
    print(f"Hashed password: {hashed_password}")
    
    # 3. Password verification
    is_valid = verify_password(password, hashed_password)
    print(f"\nPassword verification:")
    print(f"Is password valid? {is_valid}")
    
    # 4. Try with wrong password
    wrong_password = "WrongPassword123!"
    is_valid = verify_password(wrong_password, hashed_password)
    print(f"Is wrong password valid? {is_valid}")
    
    # 5. Demonstrate classical cracking difficulty
    demonstrate_cracking_difficulty(password, hashed_password)
    
    # 6. Simulate quantum cracking
    simulate_quantum_cracking(password, hashed_password)
    
    # 7. Theoretical comparison
    print("\nTheoretical Comparison:")
    print("Classical computer: O(N) time complexity")
    print("Quantum computer: O(sqrt(N)) time complexity with Grover's algorithm")
    print("For a 12-character password with 95 possible characters:")
    print(f"Classical: Would need to try ~{95**12:,} combinations")
    print(f"Quantum: Would need to try ~{math.sqrt(95**12):,.0f} combinations")
    print("\nNote: This is a simplified simulation. Real quantum computers would face additional")
    print("challenges with noise, decoherence, and the physical limitations of quantum hardware.")

if __name__ == "__main__":
    main() 