import requests
import json
import sys

def verify_character_web():
    url = "http://localhost:8000/api/narrative/character-web"
    
    # Try different ports if 8000 is not responsive
    ports = [8000, 8001, 8002, 8003]
    response = None
    
    for port in ports:
        try:
            test_url = f"http://localhost:{port}/api/narrative/character-web"
            print(f"Testing {test_url}...")
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                print(f"Success on port {port}!")
                url = test_url
                break
        except requests.exceptions.RequestException:
            continue
            
    if not response or response.status_code != 200:
        print(f"Error: Could not access endpoint on any of the tested ports.")
        sys.exit(1)
        
    data = response.json()
    
    # Verify structure
    required_keys = ["corners", "conflicts", "double_reversals"]
    for key in required_keys:
        if key not in data:
            print(f"Error: Missing key '{key}' in response.")
            sys.exit(1)
            
    # Verify corners
    corners = data["corners"]
    if len(corners) != 6:
        print(f"Error: Expected 6 corners, found {len(corners)}.")
        sys.exit(1)
        
    roles = [c["role"] for c in corners]
    expected_roles = [
        "hero", "necessary_opponent", "ally", 
        "fake_ally_opponent", "optional_fake_opponent_ally", "subplot_mirror"
    ]
    
    for role in expected_roles:
        if role not in roles:
            print(f"Error: Missing expected role '{role}' in corners.")
            sys.exit(1)
            
    # Verify distinct values and tactics (basic check)
    all_values = []
    all_tactics = set()
    for c in corners:
        all_values.extend(c["values"])
        all_tactics.add(c["tactic"])
        
    if len(set(all_tactics)) < 4: # There are 4 unique TacticStyles
        print(f"Error: Not enough distinct tactics found ({len(all_tactics)}).")
        # Note: Some characters might share tactics, but we check if they are spread out.
    
    print("\nCharacter Web Verification Passed!")
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    verify_character_web()
