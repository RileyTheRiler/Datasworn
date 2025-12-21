import os
import sys
import json
import logging
import sqlite3
from datetime import datetime
from unittest.mock import MagicMock

# Ensure strict python path
sys.path.append(os.getcwd())

from src.database import get_db, DatabaseManager
from src.npc.schemas import CognitiveState, PersonalityProfile, RelationshipState
from src.npc.memory_stream import NPCMemoryStream
from src.npc.engine import NPCCognitiveEngine

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("Verifier")

def setup_test_db():
    logger.info("Initializing Database...")
    try:
        if os.path.exists("world.db"):
            os.remove("world.db") # Start fresh
    except Exception as e:
        logger.warning(f"Could not remove old DB: {e}")
        
    db = get_db()
    
    # Check tables
    tables = db.query("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [t['name'] for t in tables]
    logger.info(f"Tables created: {table_names}")
    
    required = ['entities', 'events', 'npc_knowledge']
    for r in required:
        if r not in table_names:
            logger.error(f"Missing table: {r}")
            return False
            
    return True

def test_memory_system():
    logger.info("\n--- Testing Memory System ---")
    npc_id = "janus_01"
    
    # 1. Init Stream (should create NPC entity)
    stream = NPCMemoryStream(npc_id)
    
    # Check Entity
    db = get_db()
    npc_rec = db.query("SELECT * FROM entities WHERE entity_id = ?", (npc_id,))
    if not npc_rec:
        logger.error("NPC Entity creation failed.")
        return False
    logger.info("NPC Entity created successfully.")
    
    # 2. Add Memory
    state = CognitiveState(
        npc_id=npc_id,
        profile=PersonalityProfile(name="Janus", role="Tester", traits=["Analytical"]),
    )
    
    logger.info("Adding memory: 'I saw the player open the airlock.'")
    mem = stream.add_memory(state, "I saw the player open the airlock.", importance=8, m_type="observation")
    
    if not mem or not mem.event_id:
        logger.error("Memory creation failed.")
        return False
    logger.info(f"Memory stored. Event ID: {mem.event_id}")
    
    # 3. Retrieve
    logger.info("Retrieving memory for query 'airlock'...")
    results = stream.retrieve(state, "What happened at the airlock?", k=1)
    
    if not results:
        logger.error("Retrieval failed (No results).")
        return False
        
    logger.info(f"Retrieved: {results[0].content} (Score: {results[0].importance_score})")
    if "airlock" not in results[0].content:
        logger.error("Retrieval mismatch.")
        return False
        
    return True

def test_cognitive_engine():
    logger.info("\n--- Testing Cognitive Engine ---")
    
    # Mock LLM
    mock_llm = MagicMock()
    # Mock Response for process_turn
    mock_llm.generate_sync.return_value = json.dumps({
        "narrative": "I am watching you closely.",
        "state_updates": {
            "mood": "Suspicious",
            "trust_change": -0.1
        }
    })
    
    engine = NPCCognitiveEngine()
    engine.llm = mock_llm # Inject Mock
    
    state = CognitiveState(
        npc_id="janus_01",
        profile=PersonalityProfile(
            name="Janus", 
            role="Security Officer", 
            traits=["Paranoid", "Vigilant"],
            current_mood="Neutral"
        )
    )
    
    logger.info("Processing Turn 1...")
    output = engine.process_turn(state, "Hello there.", "Bridge", "08:00")
    
    logger.info(f"Output Narrative: {output['narrative']}")
    logger.info(f"State Updates: {output['state_updates']}")
    
    # Verify Updates applied to State object
    if state.profile.current_mood != "Suspicious":
        logger.error(f"Mood update failed. Expected 'Suspicious', got '{state.profile.current_mood}'")
        return False
        
    # Verify Memory of interaction added
    stream = NPCMemoryStream("janus_01")
    memories = stream.retrieve(state, "Hello", k=5)
    
    found_interaction = False
    for m in memories:
        if "Me: I am watching you closely" in m.content:
            found_interaction = True
            logger.info(f"Found interaction memory: {m.content}")
            break
            
    if not found_interaction:
        logger.error("Interaction not committed to memory.")
        return False
        
    return True

if __name__ == "__main__":
    if not setup_test_db():
        sys.exit(1)
        
    if not test_memory_system():
        sys.exit(1)
        
    if not test_cognitive_engine():
        sys.exit(1)
        
    logger.info("\n✅ ALL TESTS PASSED")
