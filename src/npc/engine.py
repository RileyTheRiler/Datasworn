"""
Cognitive Engine Brain (LangGraph Node).
Orchestrates Perception, Memory, and Action.
"""

from __future__ import annotations
from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from src.npc.schemas import CognitiveState, MemoryObject
from src.npc.memory_stream import NPCMemoryStream
from src.npc.planning import NPCAgency
from src.narrator import get_llm_client, NarratorConfig
import json

class NPCEngineInput(TypedDict):
    npc_state: CognitiveState
    player_input: str
    context_location: str
    time: str

class NPCOutput(TypedDict):
    narrative: str
    state_updates: Dict[str, Any]

class NPCCognitiveEngine:
    """
    The 'Brain' that runs the loop.
    Currently implemented as a class that manages the workflow manually or via internal graph.
    """
    def __init__(self):
        self.memory = None # Set per NPC run
        self.agency = NPCAgency()
        self.llm = get_llm_client(NarratorConfig(max_tokens=1000, temperature=0.7))

    def process_turn(self, state: CognitiveState, player_input: str, location: str, time: str) -> NPCOutput:
        """
        Main cognitive loop:
        Perception -> Retrieval -> Planning -> Action
        """
        self.memory = NPCMemoryStream(state.npc_id)
        
        # 1. Perception & Retrieval
        relevant_memories = self.memory.retrieve(state, player_input, k=3)
        memory_context = "\n".join([m.to_text_context() for m in relevant_memories])
        
        # 2. Planning Check (Reaction)
        current_activity = self.agency.update_plan(state, f"Player says: {player_input}", self.llm)
        
        # 3. Action Generation (JSON Enforced)
        system_prompt = self._build_system_prompt(state, memory_context, current_activity, location, time)
        
        try:
            # We force a JSON schema instruction
            json_response = self.llm.generate_sync(
                prompt=f"Player Input: {player_input}\nRespond in JSON.",
                system=system_prompt,
                config=NarratorConfig(max_tokens=1000, temperature=0.8)
            )
            
            # Clean and parse JSON
            cleaned_json = self._clean_json(json_response)
            parsed = json.loads(cleaned_json)
            
            # 4. State Commit
            # Add new memory of this interaction
            # Note: add_memory now writes to DB
            self.memory.add_memory(
                state=state, 
                content=f"Player: {player_input} | Me: {parsed.get('narrative', '')}", 
                importance=5, 
                m_type="dialogue",
                timestamp=time
            )
            
            # Process internal updates if any (e.g. mood)
            if "state_updates" in parsed and "mood" in parsed["state_updates"]:
                 state.profile.current_mood = parsed["state_updates"]["mood"]
            
            return {
                "narrative": parsed.get("narrative", "..."),
                "state_updates": parsed.get("state_updates", {})
            }
            
        except Exception as e:
            print(f"[Engine Error] {e}")
            return {
                "narrative": f"{state.profile.name} looks confused. (System Error: {e})",
                "state_updates": {}
            }

    def _build_system_prompt(self, state: CognitiveState, memories: str, activity: str, location: str, time: str) -> str:
        return f"""
        You are {state.profile.name}, a {state.profile.role} in {location}.
        Time: {time}. Current Activity: {activity}.
        
        CORE IDENTITY:
        {state.profile.narrative_seed}
        Traits: {state.profile.traits}
        Mood: {state.profile.current_mood}
        
        RELEVANT MEMORIES:
        {memories}
        
        RELATIONSHIPS:
        {json.dumps({k: v.get_semantic_descriptor() for k,v in state.relationships.items()})}
        
        TASK:
        Respond to the player. You must output a valid JSON object.
        
        JSON SCHEMA:
        {{
            "narrative": "string (your dialogue and action)",
            "state_updates": {{
                "mood": "string (new mood)",
                "trust_change": float (delta for player trust, optional)
            }}
        }}
        """

    def _clean_json(self, text: str) -> str:
        """Heuristic to strip markdown code blocks."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
