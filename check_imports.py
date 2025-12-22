import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd()))

try:
    print("Attempting to import src.quest_api...")
    from src import quest_api
    print("Successfully imported src.quest_api")
except Exception as e:
    print(f"FAILED to import src.quest_api: {e}")
    import traceback
    traceback.print_exc()
