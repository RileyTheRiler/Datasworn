import requests
import json
import base64

API_URL = "http://localhost:8000/api"

def test_ship_blueprints():
    print("1. Initializing session...")
    init_data = {
        "character_name": "Riley",
        "background_vow": "Explore the Forge"
    }
    res = requests.post(f"{API_URL}/session/start", json=init_data)
    print(f"Init Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Error: {res.text}")
        return

    print("\n2. Fetching ship blueprint...")
    # Using session_id="default" as per server.py
    res = requests.get(f"{API_URL}/ship/blueprint?session_id=default")
    print(f"Blueprint Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"Blueprint received! Image length: {len(data.get('image_base64', ''))}")
        print(f"Ship Class: {data.get('metadata', {}).get('class_type')}")
        print(f"Hull Integrity: {data.get('metadata', {}).get('hull_integrity')}")
    else:
        print(f"Error: {res.text}")
        return

    print("\n3. Inflicting ship damage...")
    update_data = {
        "session_id": "default",
        "hull_integrity": 2,
        "active_alerts": ["HULL BREACH - DECK 4", "FIRE IN ENGINEERING"]
    }
    res = requests.post(f"{API_URL}/ship/update", json=update_data)
    print(f"Update Status: {res.status_code}")

    print("\n4. Fetching updated blueprint...")
    res = requests.get(f"{API_URL}/ship/blueprint?session_id=default")
    print(f"Updated Blueprint Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"Updated Damage Level: {data.get('metadata', {}).get('damage_level')}")
        print(f"Active Alerts: {data.get('metadata', {}).get('alerts')}")

if __name__ == "__main__":
    test_ship_blueprints()
