"""
Contextual Dialogue Selector

Evaluates player and NPC state to select appropriate dialogue based on conditions.
Loads dialogue contexts from YAML and applies weighted selection.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
import random


@dataclass
class DialogueContext:
    """Current context for dialogue selection"""
    # Player state
    player_has_weapon_drawn: bool = False
    player_intoxication: float = 0.0
    player_is_sneaking: bool = False
    player_honor: float = 0.5
    player_crime_timer: int = 999999  # Seconds since last crime
    player_wearing_mask: bool = False
    player_on_mount: bool = False
    player_has_item: Optional[str] = None
    
    # NPC state
    npc_mood: str = "neutral"
    npc_schedule_phase: Optional[str] = None
    npc_fatigue: float = 0.0
    npc_memory_has: List[str] = field(default_factory=list)
    npc_trait_required: Optional[str] = None
    npc_archetype: Optional[str] = None
    npc_relationship: float = 0.5
    npc_state: Optional[str] = None
    
    # Environmental
    weather: str = "clear"
    time_of_day: str = "day"
    location_type: Optional[str] = None
    location_density: float = 0.3
    location_danger_level: float = 0.0
    nearby_npcs: int = 5
    
    # Memory
    memory_age: int = 999999  # Seconds
    memory_required: Optional[str] = None


@dataclass
class DialogueLine:
    """A single dialogue line with conditions and weight"""
    text: str
    weight: float = 1.0
    conditions: Dict[str, Any] = field(default_factory=dict)
    npc_mood: Optional[str] = None
    animation: Optional[str] = None
    sound_effect: Optional[str] = None
    visual_effect: Optional[str] = None
    triggers: Optional[str] = None
    behavior: Optional[str] = None
    reputation_change: float = 0.0
    relationship_change: float = 0.0
    
    def matches_context(self, context: DialogueContext) -> bool:
        """Check if this line matches the current context"""
        # Check player conditions
        if "player_has_weapon_drawn" in self.conditions:
            if context.player_has_weapon_drawn != self.conditions["player_has_weapon_drawn"]:
                return False
        
        if "player_intoxication" in self.conditions:
            condition = self.conditions["player_intoxication"]
            if isinstance(condition, str) and condition.startswith(">="):
                threshold = float(condition[2:].strip())
                if context.player_intoxication < threshold:
                    return False
        
        if "player_is_sneaking" in self.conditions:
            if context.player_is_sneaking != self.conditions["player_is_sneaking"]:
                return False
        
        if "player_honor" in self.conditions:
            condition = self.conditions["player_honor"]
            if isinstance(condition, str):
                if condition.startswith("<"):
                    threshold = float(condition[1:].strip())
                    if context.player_honor >= threshold:
                        return False
                elif condition.startswith(">="):
                    threshold = float(condition[2:].strip())
                    if context.player_honor < threshold:
                        return False
        
        if "player_crime_timer" in self.conditions:
            condition = self.conditions["player_crime_timer"]
            if isinstance(condition, str) and condition.startswith("<"):
                threshold = int(condition[1:].strip())
                if context.player_crime_timer >= threshold:
                    return False
        
        # Check NPC conditions
        if self.npc_mood and context.npc_mood != self.npc_mood:
            return False
        
        if self.npc_trait_required and self.npc_trait_required not in context.npc_memory_has:
            # This is a simplification - in real use, check NPC traits
            pass
        
        if "npc_memory_has" in self.conditions:
            required_memory = self.conditions["npc_memory_has"]
            if required_memory not in context.npc_memory_has:
                return False
        
        if "memory_age" in self.conditions:
            condition = self.conditions["memory_age"]
            if isinstance(condition, str) and condition.startswith("<"):
                threshold = int(condition[1:].strip())
                if context.memory_age >= threshold:
                    return False
        
        # Check environmental conditions
        if "weather" in self.conditions:
            if context.weather != self.conditions["weather"]:
                return False
        
        if "time_of_day" in self.conditions:
            if context.time_of_day != self.conditions["time_of_day"]:
                return False
        
        if "location_type" in self.conditions:
            if context.location_type != self.conditions["location_type"]:
                return False
        
        return True


class DialogueSelector:
    """
    Selects appropriate dialogue based on context.
    
    Features:
    - Load dialogue from YAML files
    - Evaluate player state (weapon, intoxication, honor, etc.)
    - Evaluate NPC state (mood, schedule, fatigue, memories)
    - Evaluate environment (weather, time, location)
    - Weighted random selection from matching lines
    - Separate walk-by barks from directed interactions
    """
    
    def __init__(self, dialogue_dir: str = "data/dialogue/contexts"):
        self.dialogue_dir = Path(dialogue_dir)
        self.contexts: Dict[str, Dict] = {}  # context_name -> data
        self.load_contexts()
    
    def load_contexts(self) -> None:
        """Load all dialogue context files from YAML"""
        if not self.dialogue_dir.exists():
            print(f"Warning: Dialogue directory not found: {self.dialogue_dir}")
            return
        
        for yaml_file in self.dialogue_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    context_name = yaml_file.stem
                    self.contexts[context_name] = data
                    print(f"Loaded dialogue context: {context_name}")
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
    
    def select_dialogue(
        self,
        npc_id: str,
        interaction_type: str,  # "greeting", "walk_by_bark", etc.
        context: DialogueContext
    ) -> Optional[DialogueLine]:
        """
        Select the best dialogue line for the current context.
        
        Args:
            npc_id: NPC identifier
            interaction_type: Type of interaction
            context: Current dialogue context
        
        Returns:
            Selected DialogueLine or None
        """
        candidates = []
        
        # Check all loaded contexts
        for context_name, context_data in self.contexts.items():
            if "contexts" not in context_data:
                continue
            
            for condition_key, condition_block in context_data["contexts"].items():
                # Check if conditions match
                if "conditions" in condition_block:
                    if not self._evaluate_conditions(condition_block["conditions"], context):
                        continue
                
                # Get dialogue lines for interaction type
                if interaction_type in condition_block:
                    lines_data = condition_block[interaction_type]
                    for line_data in lines_data:
                        line = self._parse_dialogue_line(line_data)
                        if line.matches_context(context):
                            candidates.append(line)
                
                # Check panic levels for crime witness
                if "panic_levels" in condition_block:
                    # Determine panic level based on NPC state
                    panic_level = self._get_panic_level(context)
                    if panic_level in condition_block["panic_levels"]:
                        level_data = condition_block["panic_levels"][panic_level]
                        if interaction_type in level_data:
                            lines_data = level_data[interaction_type]
                            for line_data in lines_data:
                                line = self._parse_dialogue_line(line_data)
                                if line.matches_context(context):
                                    candidates.append(line)
        
        # Check neutral fallbacks
        for context_data in self.contexts.values():
            if "neutral" in context_data and interaction_type in context_data["neutral"]:
                lines_data = context_data["neutral"][interaction_type]
                for line_data in lines_data:
                    line = self._parse_dialogue_line(line_data)
                    candidates.append(line)
        
        if not candidates:
            return None
        
        # Weighted random selection
        total_weight = sum(line.weight for line in candidates)
        if total_weight == 0:
            return random.choice(candidates)
        
        rand = random.uniform(0, total_weight)
        cumulative = 0
        for line in candidates:
            cumulative += line.weight
            if rand <= cumulative:
                return line
        
        return candidates[-1]  # Fallback
    
    def get_walk_by_bark(
        self,
        npc_id: str,
        context: DialogueContext
    ) -> Optional[DialogueLine]:
        """Get an ambient walk-by bark"""
        return self.select_dialogue(npc_id, "walk_by_barks", context)
    
    def get_greeting(
        self,
        npc_id: str,
        context: DialogueContext
    ) -> Optional[DialogueLine]:
        """Get a greeting dialogue"""
        return self.select_dialogue(npc_id, "greetings", context)
    
    def _evaluate_conditions(
        self,
        conditions: List[Dict[str, Any]],
        context: DialogueContext
    ) -> bool:
        """Evaluate a list of conditions against context"""
        for condition in conditions:
            for key, value in condition.items():
                if key == "player_has_weapon_drawn":
                    if context.player_has_weapon_drawn != value:
                        return False
                elif key == "player_intoxication":
                    if isinstance(value, str) and value.startswith(">="):
                        threshold = float(value[2:].strip())
                        if context.player_intoxication < threshold:
                            return False
                elif key == "player_honor":
                    if isinstance(value, str):
                        if value.startswith("<"):
                            threshold = float(value[1:].strip())
                            if context.player_honor >= threshold:
                                return False
                        elif value.startswith(">="):
                            threshold = float(value[2:].strip())
                            if context.player_honor < threshold:
                                return False
                elif key == "weather":
                    if context.weather != value:
                        return False
                elif key == "time_of_day":
                    if context.time_of_day != value:
                        return False
                elif key == "npc_memory_has":
                    if value not in context.npc_memory_has:
                        return False
        
        return True
    
    def _get_panic_level(self, context: DialogueContext) -> str:
        """Determine panic level based on context"""
        # Simplified panic calculation
        if "witnessed_murder" in context.npc_memory_has:
            if context.memory_age < 60:  # Very recent
                return "extreme"
            elif context.memory_age < 300:
                return "high"
            else:
                return "medium"
        elif "witnessed_theft" in context.npc_memory_has:
            if context.memory_age < 60:
                return "high"
            else:
                return "medium"
        
        return "low"
    
    def _parse_dialogue_line(self, line_data: Dict[str, Any]) -> DialogueLine:
        """Parse a dialogue line from YAML data"""
        return DialogueLine(
            text=line_data.get("text", "..."),
            weight=line_data.get("weight", 1.0),
            conditions=line_data.get("conditions", {}),
            npc_mood=line_data.get("npc_mood"),
            animation=line_data.get("animation"),
            sound_effect=line_data.get("sound_effect"),
            visual_effect=line_data.get("visual_effect"),
            triggers=line_data.get("triggers"),
            behavior=line_data.get("behavior"),
            reputation_change=line_data.get("reputation_change", 0.0),
            relationship_change=line_data.get("relationship_change", 0.0),
        )
