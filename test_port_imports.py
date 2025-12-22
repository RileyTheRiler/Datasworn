"""Quick test to verify imports work"""
import sys
sys.path.insert(0, 'c:/Users/riley/Desktop/Datasworn')

try:
    from src.narrative.port_arrival import get_approach_scene, get_docking_scene
    print("✓ port_arrival imports successful")
    
    from src.narrative.port_arrival_orchestrator import PortArrivalOrchestrator
    print("✓ port_arrival_orchestrator imports successful")
    
    # Test basic functionality
    scene = get_approach_scene()
    print(f"✓ get_approach_scene() works: {len(scene)} keys")
    
    orchestrator = PortArrivalOrchestrator()
    print("✓ PortArrivalOrchestrator() instantiation works")
    
    status = orchestrator.get_status()
    print(f"✓ get_status() works: {status['current_stage']}")
    
    print("\n🎉 All imports and basic functionality verified!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
