"""
Psychological Profiling System for Starforged AI Game Master.
Analyzes player behavior to build a psychological profile and generate narrative subversions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json
import ollama

# ============================================================================
# Psychological Profile
# ============================================================================

@dataclass
class PsychProfile:
    """
    Tracks the player's psychological state and gameplay patterns.
    Traits are rated 0.0 (low) to 1.0 (high).
    """
    # Core Traits
    aggression: float = 0.5   # Violence vs. Diplomacy
    caution: float = 0.5      # Planning vs. Impulse
    curiosity: float = 0.5    # Exploration vs. Mission-focus
    empathy: float = 0.5      # Altruism vs. Self-interest
    trust: float = 0.5        # Gullibility vs. Paranoia
    discipline: float = 0.5   # Impulse Control
    deception: float = 0.5    # Manipulative vs. Honest
    materialism: float = 0.5  # Greed vs. Asceticism
    dogmatism: float = 0.5    # Rigid vs. Flexible beliefs

    # Cognitive Biases (Confidence: 0.0 to 1.0)
    sunk_cost_fallacy: float = 0.0
    risk_aversion: float = 0.0
    confirmation_bias: float = 0.0
    authority_bias: float = 0.0

    # Values & Narrative Data
    fear_triggers: list[str] = field(default_factory=list)  # Discovered phobias/weaknesses
    paranoia_targets: list[str] = field(default_factory=list) # NPCs/Factions the player mistrusts
    core_values: list[str] = field(default_factory=list)  # e.g., "Justice", "Survival"
    taboos: list[str] = field(default_factory=list)       # Lines they won't cross
    
    # History
    decision_log: list[dict] = field(default_factory=list) # Significant choices

    def update_trait(self, trait: str, change: float):
        """Update a specific trait, clamping between 0.0 and 1.0."""
        if hasattr(self, trait) and isinstance(getattr(self, trait), float):
            current = getattr(self, trait)
            new_val = max(0.0, min(1.0, current + change))
            setattr(self, trait, new_val)

    def log_decision(self, event: str, analysis: str):
        """Log a significant decision."""
        entry = {"event": event, "analysis": analysis}
        self.decision_log.append(entry)
        if len(self.decision_log) > 50:
            self.decision_log.pop(0)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    @classmethod
    def from_dict(cls, data: dict) -> "PsychProfile":
        # Filter out unknown keys to match the new schema
        valid_keys = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_keys)


# ============================================================================
# PsychoAnalyst Agent
# ============================================================================

SYSTEM_PROMPT = """You are the PsychoAnalyst. You analyze player behavior in a TTRPG to build an EXHAUSTIVE psychological profile.

YOUR GOAL:
Deconstruct the player's psyche based on their choices. Look for patterns, contradictions, and deep-seated motivations.

INPUT:
- Player Action
- Narrative Context
- Current Profile (Core Traits, Biases, Values)

ANALYSIS TARGETS:
1. **Core Traits** (Delta +/-): Aggression, Caution, Curiosity, Empathy, Trust, Discipline, Deception, Materialism, Dogmatism.
2. **Cognitive Biases** (Delta +/-): Does the player show Sunk Cost Fallacy? Risk Aversion? Confirmation Bias?
3. **Values**: What do they value? (e.g., Justice, Power, Survival). What are their Taboos?
4. **Fears & Paranoia**: What scares them? Who do they mistrust?

OUTPUT (JSON):
{
  "trait_updates": {"trait_name": float_delta}, 
  "bias_updates": {"bias_name": float_delta},
  "new_values": ["string"],
  "new_taboos": ["string"],
  "new_fear_triggers": ["string"],
  "new_paranoia_targets": ["string"],
  "decision_analysis": "Concise psychological breakdown of this specific choice."
}
"""

SUBVERSION_PROMPT = """You are the Subversion Engine. Your goal is to generate a 'Subversion' - a narrative twist or psychological challenge designed specifically to target the player's current profile.

INPUT:
- Current Psych Profile (Exhaustive)
- Recent Context

STRATEGIES:
- **Exploit Biases**: If high Sunk Cost, present a failing cause they've invested in. If high Confirmation Bias, feed them false evidence they want to believe.
- **Challenge Values**: If they value Justice, present a situation where Justice creates a monstrosity.
- **Target Traits**: 
    - High Discipline? Create chaos where rules fail. 
    - High Deception? Have them be the victim of a simpler, more honest lie.
- **Leverage Fears**: Use their Fear Triggers creatively.

OUTPUT (JSON):
{
  "type": "subversion",
  "target_vector": "Specific trait/bias/value targeted (e.g., 'Sunk Cost Fallacy')",
  "suggestion": "Specific narrative twist/challenge to insert into the next scene."
}
"""

@dataclass
class PsychoAnalyst:
    """
    Analyzes player actions and generates psychological subversions.
    """
    model: str = "llama3.1"
    profile: PsychProfile = field(default_factory=PsychProfile)
    _client: ollama.Client = field(default_factory=ollama.Client, repr=False)

    def analyze_turn(self, player_action: str, context: str) -> None:
        """
        Analyze a single turn and update the psychological profile.
        """
        prompt = f"""
        PLAYER ACTION: {player_action}
        CONTEXT: {context}
        CURRENT PROFILE: {json.dumps(self.profile.to_dict(), default=str)}
        """

        try:
            response = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.5, "format": "json"},
            )
            
            content = response.get("message", {}).get("content", "")
            data = json.loads(content)

            # Apply updates
            updates = data.get("trait_updates", {})
            for trait, change in updates.items():
                self.profile.update_trait(trait, change)
            
            # Apply bias updates
            bias_updates = data.get("bias_updates", {})
            for bias, change in bias_updates.items():
                self.profile.update_trait(bias, change)
            
            # Lists
            for val in data.get("new_values", []):
                if val not in self.profile.core_values:
                    self.profile.core_values.append(val)
            
            for taboo in data.get("new_taboos", []):
                if taboo not in self.profile.taboos:
                    self.profile.taboos.append(taboo)

            for trigger in data.get("new_fear_triggers", []):
                if trigger not in self.profile.fear_triggers:
                    self.profile.fear_triggers.append(trigger)
                    
            for target in data.get("new_paranoia_targets", []):
                if target not in self.profile.paranoia_targets:
                    self.profile.paranoia_targets.append(target)
            
            # Log decision
            if data.get("decision_analysis"):
                self.profile.log_decision(player_action[:50] + "...", data["decision_analysis"])

        except Exception as e:
            print(f"PsychoAnalyst Analysis Error: {e}")

    def propose_subversion(self, context: str) -> str | None:
        """
        Generate a narrative subversion based on the current profile.
        Returns a string suggestion for the Director/Narrator, or None.
        """
        # Trigger less frequently to avoid noise, or always return one and let Director decide?
        # For now, we'll try to generate one.
        
        prompt = f"""
        CONTEXT: {context}
        CURRENT PROFILE: {json.dumps(self.profile.to_dict(), default=str)}
        """

        try:
            response = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SUBVERSION_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.8, "format": "json"},
            )
            
            content = response.get("message", {}).get("content", "")
            data = json.loads(content)
            
            suggestion = data.get("suggestion")
            target = data.get("target_vector", "General")
            
            if suggestion:
                return f"[{target}] {suggestion}"
            return None

        except Exception as e:
            print(f"PsychoAnalyst Subversion Error: {e}")
            return None
