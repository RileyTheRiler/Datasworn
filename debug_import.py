import sys
import os
from pathlib import Path

# Simulate server.py environment
sys.path.insert(0, str(Path(os.getcwd()) / "src"))
sys.path.insert(0, os.getcwd())

print(f"Sys Path: {sys.path[:3]}")

try:
    import src.npc.schemas as schemas
    print(f"Module: {schemas}")
    print(f"File: {schemas.__file__}")
    
    if hasattr(schemas, 'PsychologicalProfile'):
        print("PsychologicalProfile FOUND in module.")
    else:
        print("PsychologicalProfile NOT FOUND in module.")
        print(f"Available names: {dir(schemas)}")
        
    from src.npc.schemas import PsychologicalProfile
    print("Direct import of PsychologicalProfile successful.")
    
except ImportError as e:
    print(f"ImportError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
