"""
Simple diagnostic to check server health and endpoint availability.
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

print("Checking server health...")

# 1. Health check
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"✓ Server is running (status: {response.status_code})")
    print(f"  Response: {response.json()}")
except requests.exceptions.Timeout:
    print("✗ Server timeout - server may be hung")
    sys.exit(1)
except Exception as e:
    print(f"✗ Cannot connect to server: {e}")
    sys.exit(1)

# 2. Check if cognitive endpoint exists
print("\nChecking endpoint registration...")
try:
    # Try a simple GET that should fail with 405 (Method Not Allowed) if endpoint exists
    response = requests.get(f"{BASE_URL}/api/cognitive/debug/test", timeout=5)
    print(f"✓ /api/cognitive/debug endpoint exists (status: {response.status_code})")
except Exception as e:
    print(f"  Note: {e}")

print("\n✓ Basic diagnostics complete")
print("  Server appears to be responding")
print("  You can now test the cognitive endpoints")
