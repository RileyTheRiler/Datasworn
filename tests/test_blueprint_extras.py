
import pytest
from src.blueprint_generator import calculate_movement_range, calculate_vision_cone

def test_calculate_movement_range():
    # 30ft speed, 5ft per square, 40px grid
    # (30 / 5) * 40 = 6 * 40 = 240
    assert calculate_movement_range(30, 40) == 240
    
    # 60ft speed
    assert calculate_movement_range(60, 40) == 480
    
    # Custom grid size
    assert calculate_movement_range(30, 50) == 300

def test_calculate_vision_cone():
    pos = (100, 100)
    facing = 0 # Right
    fov = 90
    max_range = 100
    
    points = calculate_vision_cone(pos, facing, fov, max_range)
    
    # Should be a list of points
    assert isinstance(points, list)
    assert len(points) > 3 # At least start, arc points, end
    
    # First and last point should be origin
    assert points[0] == pos
    assert points[-1] == pos
    
    # Check a point in the cone
    # For facing 0 (right), points should have x > 100
    some_arc_point = points[10]
    assert some_arc_point[0] > 100

def test_image_gen_integration():
    """Test that image_gen functions accept new parameters without error."""
    try:
        from src.image_gen import generate_tactical_blueprint
        
        # Mock game state
        fake_state = {
            "current_location": "Test Zone",
            "location_type": "bar",
            "npcs": []
        }
        
        # Call with new parameters
        result = generate_tactical_blueprint(
            fake_state,
            show_movement=True,
            show_vision=True
        )
        
        assert "image_base64" in result
        assert result["image_base64"].startswith("iVBOR") # Base64 PNG signature
        
    except ImportError:
        pytest.skip("PIL not installed or import error")
    except Exception as e:
        pytest.fail(f"generate_tactical_blueprint failed: {e}")
