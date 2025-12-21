"""
Photo Album Backend Verification Script
Tests all photo album functionality before frontend integration.
"""

import sys
import requests
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_URL = "http://localhost:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}[TEST]{Colors.END} {name}")

def print_pass(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_fail(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ{Colors.END} {msg}")

def test_imports():
    """Test that all imports work correctly."""
    print_test("Testing imports")
    
    try:
        from src.game_state import PhotoEntry, PhotoAlbumState
        print_pass("PhotoEntry and PhotoAlbumState imported")
    except ImportError as e:
        print_fail(f"Failed to import state models: {e}")
        return False
    
    try:
        from src.photo_album import PhotoAlbumManager
        print_pass("PhotoAlbumManager imported")
    except ImportError as e:
        print_fail(f"Failed to import PhotoAlbumManager: {e}")
        return False
    
    return True

def test_state_creation():
    """Test that PhotoAlbumState can be created."""
    print_test("Testing state creation")
    
    from src.game_state import PhotoAlbumState, PhotoEntry
    
    # Create empty state
    state = PhotoAlbumState()
    assert len(state.photos) == 0, "New state should have no photos"
    print_pass("Empty PhotoAlbumState created")
    
    # Create photo entry
    entry = PhotoEntry(
        id="test-123",
        image_url="/test.png",
        caption="Test Photo",
        timestamp="2024-01-01T00:00:00",
        tags=["Test"],
        scene_id="Test Zone"
    )
    print_pass("PhotoEntry created")
    
    # Add to state
    state.photos.append(entry)
    assert len(state.photos) == 1, "State should have 1 photo"
    print_pass("Photo added to state")
    
    return True

def test_manager_operations():
    """Test PhotoAlbumManager operations."""
    print_test("Testing PhotoAlbumManager")
    
    from src.game_state import PhotoAlbumState
    from src.photo_album import PhotoAlbumManager
    
    state = PhotoAlbumState()
    manager = PhotoAlbumManager(state)
    
    # Test capture_moment
    entry = manager.capture_moment(
        image_url="/test_image.png",
        caption="Test Capture",
        tags=["Test", "Verification"],
        scene_id="Test Location"
    )
    
    assert entry.id is not None, "Entry should have ID"
    assert entry.image_url == "/test_image.png", "Image URL should match"
    assert len(entry.tags) == 2, "Should have 2 tags"
    print_pass("capture_moment() works")
    
    # Test get_photos
    photos = manager.get_photos()
    assert len(photos) == 1, "Should have 1 photo"
    print_pass("get_photos() works")
    
    # Test tag filtering
    filtered = manager.get_photos(tag_filter="Test")
    assert len(filtered) == 1, "Should find 1 photo with 'Test' tag"
    print_pass("Tag filtering works")
    
    # Test get_latest_photo
    latest = manager.get_latest_photo()
    assert latest.caption == "Test Capture", "Latest photo should match"
    print_pass("get_latest_photo() works")
    
    return True

def test_api_endpoints():
    """Test API endpoints (requires server running)."""
    print_test("Testing API endpoints")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_URL.replace('/api', '')}/")
        if response.status_code != 200:
            print_fail("Server not responding")
            return False
        print_pass("Server is running")
    except requests.ConnectionError:
        print_fail("Server not running. Start with: python -m uvicorn src.server:app --reload")
        return False
    
    # Test 1: Start a session
    print_info("Starting new session...")
    response = requests.post(f"{API_URL}/session/start", json={
        "character_name": "Test Character"
    })
    
    if response.status_code != 200:
        print_fail(f"Failed to start session: {response.status_code}")
        print_info(response.text)
        return False
    
    data = response.json()
    session_id = data.get("session_id", "default")
    print_pass(f"Session started: {session_id}")
    
    # Test 2: Get empty album
    print_info("Fetching empty album...")
    response = requests.get(f"{API_URL}/album/{session_id}")
    
    if response.status_code != 200:
        print_fail(f"Failed to get album: {response.status_code}")
        print_info(response.text)
        return False
    
    album_data = response.json()
    photos = album_data.get("photos", [])
    
    if len(photos) != 0:
        print_fail(f"Expected 0 photos, got {len(photos)}")
        return False
    
    print_pass("Empty album retrieved")
    
    # Test 3: Manually capture a photo
    print_info("Capturing test photo...")
    response = requests.post(f"{API_URL}/album/capture", json={
        "session_id": session_id,
        "image_url": "/assets/test_capture.png",
        "caption": "API Test Capture",
        "tags": ["API", "Test", "Verification"],
        "scene_id": "Test Zone"
    })
    
    if response.status_code != 200:
        print_fail(f"Failed to capture photo: {response.status_code}")
        print_info(response.text)
        return False
    
    capture_result = response.json()
    if not capture_result.get("success"):
        print_fail("Capture returned success=False")
        return False
    
    print_pass("Photo captured via API")
    
    # Test 4: Retrieve album with photo
    print_info("Fetching album with photo...")
    response = requests.get(f"{API_URL}/album/{session_id}")
    
    if response.status_code != 200:
        print_fail(f"Failed to get album: {response.status_code}")
        return False
    
    album_data = response.json()
    photos = album_data.get("photos", [])
    
    if len(photos) != 1:
        print_fail(f"Expected 1 photo, got {len(photos)}")
        return False
    
    photo = photos[0]
    if photo["caption"] != "API Test Capture":
        print_fail(f"Caption mismatch: {photo['caption']}")
        return False
    
    if len(photo["tags"]) != 3:
        print_fail(f"Expected 3 tags, got {len(photo['tags'])}")
        return False
    
    print_pass("Photo retrieved from album")
    print_info(f"  Caption: {photo['caption']}")
    print_info(f"  Tags: {', '.join(photo['tags'])}")
    print_info(f"  ID: {photo['id']}")
    
    return True

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Photo Album Backend Verification{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    tests = [
        ("Imports", test_imports),
        ("State Creation", test_state_creation),
        ("Manager Operations", test_manager_operations),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"Exception in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Summary{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{name}: {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✓ All tests passed! Backend is ready.{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}✗ Some tests failed. Fix issues before frontend testing.{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
