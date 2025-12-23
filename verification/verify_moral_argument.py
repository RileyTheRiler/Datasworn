import requests
import json
import sys

def verify_moral_argument():
    """Verify the moral argument endpoint returns correct structure and data."""
    
    # Try different ports
    ports = [8000, 8001, 8002, 8003]
    response = None
    
    for port in ports:
        try:
            test_url = f"http://localhost:{port}/api/narrative/moral-argument"
            print(f"Testing {test_url}...")
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                print(f"✓ Success on port {port}!")
                break
        except requests.exceptions.RequestException:
            continue
            
    if not response or response.status_code != 200:
        print("✗ Error: Could not access endpoint on any tested ports.")
        sys.exit(1)
        
    data = response.json()
    
    # Verify structure
    required_keys = [
        "moral_weakness", 
        "first_immoral_act", 
        "immoral_choices", 
        "ally_criticisms",
        "competing_values",
        "thematic_insight",
        "current_escalation_level"
    ]
    
    for key in required_keys:
        if key not in data:
            print(f"✗ Error: Missing key '{key}' in response.")
            sys.exit(1)
    
    print("✓ All required keys present")
    
    # Verify moral weakness
    weakness = data["moral_weakness"]
    if not all(k in weakness for k in ["type", "description", "root_fear", "manifestation"]):
        print("✗ Error: Moral weakness missing required fields.")
        sys.exit(1)
    print(f"✓ Moral weakness defined: {weakness['type']}")
    
    # Verify first immoral act is scripted
    first_act = data["first_immoral_act"]
    if not all(k in first_act for k in ["choice_id", "scene", "description", "justification", "harm"]):
        print("✗ Error: First immoral act missing required fields.")
        sys.exit(1)
    if first_act["escalation_level"] != 1:
        print("✗ Error: First immoral act should be escalation level 1.")
        sys.exit(1)
    print(f"✓ First immoral act scripted at scene {first_act['scene']}")
    
    # Verify escalating choices (should have 2-3 total)
    choices = data["immoral_choices"]
    if len(choices) < 2:
        print(f"⚠ Warning: Only {len(choices)} immoral choices defined (expected 2-3).")
    else:
        print(f"✓ {len(choices)} escalating immoral choices defined")
    
    # Verify escalation levels increase
    escalation_levels = [c["escalation_level"] for c in choices]
    if escalation_levels != sorted(escalation_levels):
        print("✗ Error: Escalation levels should increase.")
        sys.exit(1)
    print(f"✓ Escalation levels: {escalation_levels}")
    
    # Verify ally criticism
    criticisms = data["ally_criticisms"]
    if len(criticisms) < 1:
        print("⚠ Warning: No ally criticisms defined.")
    else:
        print(f"✓ {len(criticisms)} ally criticism(s) defined")
        for crit in criticisms:
            if not all(k in crit for k in ["ally", "value", "criticism", "why_it_stings"]):
                print("✗ Error: Ally criticism missing required fields.")
                sys.exit(1)
    
    # Verify thematic insight is a single line
    insight = data["thematic_insight"]
    if not insight:
        print("⚠ Warning: Thematic insight is empty.")
    elif len(insight.split('\n')) > 1:
        print("✗ Error: Thematic insight should be a single line.")
        sys.exit(1)
    else:
        print(f"✓ Thematic insight: \"{insight}\"")
    
    # Verify competing values
    values = data["competing_values"]
    if len(values) < 2:
        print("⚠ Warning: Should have at least 2 competing values.")
    else:
        print(f"✓ Competing values: {', '.join(values)}")
    
    print("\n" + "="*60)
    print("MORAL ARGUMENT VERIFICATION PASSED!")
    print("="*60)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    verify_moral_argument()
