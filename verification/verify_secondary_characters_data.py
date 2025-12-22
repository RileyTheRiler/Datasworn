
import sys
import os
import json

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.narrative.secondary_characters import get_character_data, check_micro_revelation, SECONDARY_CHARACTERS
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

def verify_character(name, expectations):
    print(f"\n--- Verifying {name.upper()} DATA ---")
    data = get_character_data(name)
    if not data:
        print(f"FAILED: get_character_data('{name}') returned None")
        return False
        
    for field in ["id", "name", "role", "central_problem_answer", "psychological_wound", "backstory"]:
        if field not in data:
            print(f"FAILED: Missing field '{field}'")
            return False
            
    for key, value_fragment in expectations.items():
        actual_value = str(data.get(key, ""))
        if value_fragment.lower() not in actual_value.lower():
            print(f"FAILED: Expected '{value_fragment}' in '{key}' but got: {actual_value[:50]}...")
            return False
            
    # Reveal check
    for rev in data['micro_revelations']:
        if not rev['text']:
            print("FAILED: Empty revelation text")
            return False
            
    print(f"SUCCESS: {name} data verified.")
    return True

def verify_logic():
    print("\n--- Verifying REVELATION LOGIC ---")
    # Test Torres trigger
    # Trigger: "torres_brother" on "military"
    rev = check_micro_revelation("torres", {"topic": "military service"})
    if rev and rev.id == "torres_brother":
        print("SUCCESS: Torres brother revelation triggered correctly.")
    else:
        print(f"FAILED: Torres trigger. Got {rev}")
        return False
        
    # Test Negative
    rev = check_micro_revelation("torres", {"topic": "cooking"})
    if rev is None:
        print("SUCCESS: Negative trigger verified.")
    else:
        print(f"FAILED: Negative trigger returned {rev}")
        return False
        
    return True

def main():
    print("Starting Data-Only Verification...")
    
    # 1. TORRES
    torres_expectations = {
        "name": "Elena Torres",
        "psychological_wound": "court-martialed",
        "secret_knowledge": "Yuki coming from the captain's quarters"
    }
    
    # 2. KAI
    kai_expectations = {
        "name": "Kai Nakamura",
        "backstory": "Helix Dynamics",
        "secret_knowledge": "manual override lockout"
    }
    
    # 3. OKONKWO
    okonkwo_expectations = {
        "name": "Sofia Okonkwo",
        "psychological_wound": "impossible choice",
        "secret_knowledge": "terminally ill"
    }
    
    # 4. VASQUEZ
    vasquez_expectations = {
        "name": "Miguel Vasquez",
        "role": "Cargo Master",
        "secret_knowledge": "addiction treatment"
    }
    
    # 5. EMBER
    ember_expectations = {
        "name": "Ember Quinn",
        "role": "Apprentice",
        "secret_knowledge": "arguing the night before the murder"
    }
    
    results = [
        verify_character("torres", torres_expectations),
        verify_character("kai", kai_expectations),
        verify_character("okonkwo", okonkwo_expectations),
        verify_character("vasquez", vasquez_expectations),
        verify_character("ember", ember_expectations),
        verify_logic()
    ]
    
    if all(results):
        print("\nALL DATA VERIFIED SUCCESSFULLY.")
    else:
        print("\nSOME CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
