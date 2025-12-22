"""
Quick verification test for ending endpoints
"""
import requests

BASE_URL = "http://localhost:8001"

print("Testing server connection...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"✓ Server is online: {response.status_code}")
except Exception as e:
    print(f"✗ Server connection failed: {e}")
    exit(1)

print("\nTesting /api/narrative/ending/sequence...")
try:
    response = requests.get(f"{BASE_URL}/api/narrative/ending/sequence?session_id=default", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Archetype: {data.get('archetype', 'N/A')}")
        print(f"✓ Moral Question: {data.get('moral_question', 'N/A')[:50]}...")
        print(f"✓ Hero path stages: {list(data.get('hero_path', {}).keys())}")
        print(f"✓ Tragedy path stages: {list(data.get('tragedy_path', {}).keys())}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Request failed: {e}")

print("\n✓ Quick verification complete!")
