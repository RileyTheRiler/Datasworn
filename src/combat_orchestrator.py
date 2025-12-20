"""
Belgian AI Combat Orchestrator.
Manages group combat through attack grids and token systems.

Based on the "Belgian AI" from Kingdoms of Amalur: Reckoning.
Prevents "dogpiling" while maintaining combat pressure.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import random

from src.psych_profile import PsychologicalProfile
from src.npc_agent import create_combat_agent # Added integration



# ============================================================================
# Attack Grid System
# ============================================================================

@dataclass
class Combatant:
    """A combatant in the attack grid."""
    id: str
    name: str
    slot_cost: int = 4  # How many grid slots this combatant uses when attacking
    attack_range: float = 1.0  # Combat range (1.0 = melee, 2.0+ = ranged)
    threat_level: float = 1.0  # How dangerous
    is_attacking: bool = False
    last_attack_time: float = 0.0
    attack_cooldown: float = 2.0  # Seconds between attacks
    agent: Any = None  # NPCAgent instance


class EnemyType(Enum):
    """Standard enemy types with slot costs."""
    MINION = 2  # Weak, can have many
    SOLDIER = 4  # Standard
    ELITE = 6  # Dangerous
    BOSS = 12  # Only one can attack at a time


ENEMY_SLOT_COSTS = {
    EnemyType.MINION: 2,
    EnemyType.SOLDIER: 4,
    EnemyType.ELITE: 6,
    EnemyType.BOSS: 12,
}


@dataclass
class AttackGrid:
    """
    Manages how many enemies can attack simultaneously and their positions.
    Prevents unfair dogpiling while keeping pressure.
    """
    max_capacity: int = 12  # Total attack slots available
    current_usage: int = 0
    
    # Enhanced: Positional Slots
    # Maps slot_name -> combatant_id (or None)
    # Frontend Expects: ENGAGED_PRIMARY, FLANK_LEFT, FLANK_RIGHT, REAR_CENTER
    slots: dict[str, str | None] = field(default_factory=lambda: {
        "ENGAGED_PRIMARY": None,
        "FLANK_LEFT": None,
        "FLANK_RIGHT": None,
        "REAR_CENTER": None,
    })
    
    active_attackers: list[str] = field(default_factory=list)
    waiting_queue: list[str] = field(default_factory=list)
    
    def can_attack(self, combatant: Combatant) -> bool:
        """Check if a combatant can join the attack."""
        if combatant.id in self.active_attackers:
            return True  # Already attacking
        
        available = self.max_capacity - self.current_usage
        return combatant.slot_cost <= available
    
    def assign_best_slot(self, combatant: Combatant) -> str | None:
        """Find the best available slot for a combatant."""
        # Logic: 
        # 1. Primary if empty
        # 2. Flanks if Primary taken
        # 3. Rear if Flanks taken
        if self.slots["ENGAGED_PRIMARY"] is None:
            return "ENGAGED_PRIMARY"
        elif self.slots["FLANK_LEFT"] is None:
            return "FLANK_LEFT"
        elif self.slots["FLANK_RIGHT"] is None:
            return "FLANK_RIGHT"
        elif self.slots["REAR_CENTER"] is None:
            return "REAR_CENTER"
        return None  # No physical slot (maybe RANGED/OFF-GRID)
    
    def begin_attack(self, combatant: Combatant) -> bool:
        """Register a combatant as attacking."""
        if not self.can_attack(combatant):
            if combatant.id not in self.waiting_queue:
                self.waiting_queue.append(combatant.id)
            return False
        
        if combatant.id not in self.active_attackers:
            self.active_attackers.append(combatant.id)
            self.current_usage += combatant.slot_cost
            
            # Assign positional slot
            slot = self.assign_best_slot(combatant)
            if slot:
                self.slots[slot] = combatant.name # Store Name for frontend visibility
        
        combatant.is_attacking = True
        return True
    
    def end_attack(self, combatant: Combatant) -> None:
        """Release attack slot when combatant stops attacking."""
        if combatant.id in self.active_attackers:
            self.active_attackers.remove(combatant.id)
            self.current_usage = max(0, self.current_usage - combatant.slot_cost)
            
            # Clear slot
            for k, v in self.slots.items():
                if v == combatant.name:
                    self.slots[k] = None
                    break
        
        combatant.is_attacking = False
        combatant.last_attack_time = time.time()
    
    def get_next_attacker(self, combatants: dict[str, Combatant]) -> str | None:
        """Get the next waiting combatant who can attack."""
        for cid in self.waiting_queue:
            if cid in combatants and self.can_attack(combatants[cid]):
                self.waiting_queue.remove(cid)
                return cid
        return None
    
    def get_status(self) -> dict:
        """Get current grid status formatted for Frontend."""
        # Frontend expects:
        # active_attackers: dict
        # attack_grid: { slots: { ENGAGED: {primary}, FLANK: {left, right}, REAR: {center} } }
        
        return {
            "capacity": f"{self.current_usage}/{self.max_capacity}",
            "slots": {
                "ENGAGED": {"primary": self.slots["ENGAGED_PRIMARY"]},
                "FLANK": {
                    "left": self.slots["FLANK_LEFT"],
                    "right": self.slots["FLANK_RIGHT"]
                },
                "REAR": {"center": self.slots["REAR_CENTER"]}
            },
            "waiting": len(self.waiting_queue),
        }


# ============================================================================
# Attack Token System
# ============================================================================

@dataclass
class AttackToken:
    """A token granting permission to attack."""
    combatant_id: str
    issued_at: float
    delay: float  # Seconds before attack can land
    expires_at: float
    is_used: bool = False


class AttackTokenManager:
    """
    Manages attack timing to prevent damage spikes.
    Only one "relevant" attacker gets a token at a time.
    """
    
    def __init__(self):
        self.active_token: AttackToken | None = None
        self.base_delay: float = 0.5  # Minimum delay between attacks
        self.max_delay: float = 2.0  # Maximum delay
        self.last_damage_time: float = 0.0
    
    def calculate_delay(
        self,
        combatant: Combatant,
        player_health: float,
        distance: float,
        profile: PsychologicalProfile | None = None,
    ) -> float:
        """
        Calculate attack delay based on context.
        More dangerous situation = longer delays (mercy mechanic).
        """
        base = self.base_delay
        
        # Low player health = more delay (mercy)
        if player_health < 0.3:
            base += 0.5
        elif player_health < 0.5:
            base += 0.25
        
        # Distance affects delay
        if distance > 2.0:
            base += 0.3  # Ranged takes longer to aim
        
        # Threat level inversely affects delay (elite attacks faster)
        base -= (combatant.threat_level - 1.0) * 0.2
        
        # Psych Integration: Stress and Trauma
        if profile:
            # High stress adds hesitation/shaking (delay)
            if profile.stress_level > 0.6:
                base += 0.4
            
            # Trauma Modifiers
            # Assuming trauma_scars is a list of objects with 'name' attribute
            scars = [s.name for s in profile.trauma_scars]
            
            if "Survivor's Guilt" in scars:
                base += 0.3  # Hesitation
            
            if "Hyper-Vigilance" in scars:
                base -= 0.2  # Faster reaction, but maybe lower accuracy elsewhere
        
        return max(self.base_delay, min(self.max_delay, base))
    
    def issue_token(
        self,
        combatant: Combatant,

        player_health: float = 1.0,
        distance: float = 1.0,
        profile: PsychologicalProfile | None = None,
    ) -> AttackToken:
        """Issue an attack token to a combatant."""
        delay = self.calculate_delay(combatant, player_health, distance, profile)
        now = time.time()
        
        token = AttackToken(
            combatant_id=combatant.id,
            issued_at=now,
            delay=delay,
            expires_at=now + delay + 1.0,  # Token expires 1s after delay
        )
        
        self.active_token = token
        return token
    
    def can_attack_now(self) -> bool:
        """Check if the current token holder can attack."""
        if not self.active_token or self.active_token.is_used:
            return False
        
        now = time.time()
        if now >= self.active_token.issued_at + self.active_token.delay:
            return True
        return False
    
    def consume_token(self) -> str | None:
        """Consume the active token when attack lands."""
        if self.active_token and not self.active_token.is_used:
            self.active_token.is_used = True
            self.last_damage_time = time.time()
            return self.active_token.combatant_id
        return None
    
    def needs_new_token(self) -> bool:
        """Check if we need to issue a new token."""
        if self.active_token is None:
            return True
        if self.active_token.is_used:
            return True
        if time.time() > self.active_token.expires_at:
            return True
        return False


# ============================================================================
# Combat Orchestrator
# ============================================================================

class CombatOrchestrator:
    """
    Main combat management system.
    Coordinates attack grid and token systems.
    """
    
    def __init__(self, max_attackers: int = 12):
        self.grid = AttackGrid(max_capacity=max_attackers)
        self.token_manager = AttackTokenManager()
        self.combatants: dict[str, Combatant] = {}
        self.current_attacker: str | None = None
    
    def add_combatant(
        self,
        id: str,
        name: str,
        enemy_type: EnemyType = EnemyType.SOLDIER,
        threat_level: float = 1.0,
    ) -> Combatant:
        """Add a combatant to the orchestrator."""
        combatant = Combatant(
            id=id,
            name=name,
            slot_cost=ENEMY_SLOT_COSTS[enemy_type],
            threat_level=threat_level,
            agent=create_combat_agent(id, name) # Initialize GOAP brain
        )
        self.combatants[id] = combatant
        return combatant
    
    def remove_combatant(self, id: str) -> None:
        """Remove a combatant (killed or fled)."""
        if id in self.combatants:
            combatant = self.combatants[id]
            self.grid.end_attack(combatant)
            del self.combatants[id]
            
            # Cancel token if this was the attacker
            if self.token_manager.active_token and self.token_manager.active_token.combatant_id == id:
                self.token_manager.active_token = None
    
    def select_attacker(self, player_health: float = 1.0) -> Combatant | None:
        """
        Select the most "relevant" combatant to attack.
        Based on threat, distance, and time since last attack.
        """
        candidates = []
        now = time.time()
        
        for combatant in self.combatants.values():
            if combatant.is_attacking:
                continue  # Already attacking
            
            # Check cooldown
            if now - combatant.last_attack_time < combatant.attack_cooldown:
                continue
            
            # Check grid capacity
            if not self.grid.can_attack(combatant):
                continue
            
            # Score candidates
            score = combatant.threat_level
            score += (now - combatant.last_attack_time) * 0.1  # Favor those who waited
            
            candidates.append((combatant, score))
        
        if not candidates:
            return None
        
        # Select highest scoring
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    
    def check_panic(self, profile: PsychologicalProfile) -> bool:
        """
        Check if the player panics due to high stress, freezing or acting randomly.
        Returns True if panicked.
        """
        if profile.stress_level < 0.8:
            return False
        
        # Simple panic check: 20% chance per update if stressed
        # In a real game, this would be determined by a move roll or similar
        return random.random() < 0.2

    def update(self, player_health: float = 1.0, profile: PsychologicalProfile | None = None) -> dict | None:
        """
        Update the combat system.
        Returns attack info if an attack should occur.
        """
        # Psych Panic Check
        if profile and self.check_panic(profile):
            return {
                "action": "panic",
                "description": "You freeze in terror. Your hands shake uncontrollably.",
                "effect": "skip_turn"
            }

        # Check if current token is ready
        if self.token_manager.can_attack_now():
            attacker_id = self.token_manager.consume_token()
            if attacker_id and attacker_id in self.combatants:
                attacker = self.combatants[attacker_id]
                
                # Use GOAP to determine specific action
                action_info = None
                if attacker.agent:
                    # Update perception (e.g., target is in range if we issued a token)
                    attacker.agent.update_perception({"target_in_range": True})
                    action_info = attacker.agent.get_next_action()
                
                self.grid.end_attack(attacker)
                
                return {
                    "attacker": attacker.name,
                    "attacker_id": attacker_id,
                    "threat_level": attacker.threat_level,
                    "action": action_info["name"] if action_info else "attacks",
                    "description": action_info["description"] if action_info else f"{attacker.name} attacks you!",
                    "effect": action_info.get("effect") if action_info else {"target_damaged": True}
                }
        
        # Issue new token if needed
        if self.token_manager.needs_new_token():
            attacker = self.select_attacker(player_health)
            if attacker:
                self.grid.begin_attack(attacker)
                self.token_manager.issue_token(attacker, player_health, profile=profile)
                self.current_attacker = attacker.id
        
        return None
    
    def get_combat_context(self) -> str:
        """Generate context for narrator about combat state."""
        lines = ["[COMBAT ORCHESTRATION]"]
        
        grid_status = self.grid.get_status()
        lines.append(f"Attack Grid: {grid_status['capacity']} slots used")
        lines.append(f"Active attackers: {grid_status['active_attackers']}")
        lines.append(f"Waiting to attack: {grid_status['waiting']}")
        
        if self.token_manager.active_token and not self.token_manager.active_token.is_used:
            cid = self.token_manager.active_token.combatant_id
            if cid in self.combatants:
                lines.append(f"Next attacker: {self.combatants[cid].name}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "combatants": {
                cid: {
                    "name": c.name,
                    "slot_cost": c.slot_cost,
                    "threat_level": c.threat_level,
                    "is_attacking": c.is_attacking,
                }
                for cid, c in self.combatants.items()
            },
            "grid": {
                "max_capacity": self.grid.max_capacity,
                "current_usage": self.grid.current_usage,
                "active_attackers": self.grid.active_attackers,
            },
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CombatOrchestrator":
        orch = cls()
        # Basic hydration for now - in production would need full state restoration
        # Re-adding combatants
        for cid, cdata in data.get("combatants", {}).items():
            orch.add_combatant(
                id=cid,
                name=cdata["name"],
                threat_level=cdata["threat_level"]
            )
        return orch

    def get_debug_state(self) -> dict:
        """
        Get comprehensive debug state for the Combat Dashboard.
        Matches the structure expected by CombatDashboard.jsx.
        """
        now = time.time()
        
        # Build active tokens dict
        active_tokens = {}
        if self.token_manager.active_token and not self.token_manager.active_token.is_used:
            t = self.token_manager.active_token
            remaining = max(0, t.expires_at - now)
            active_tokens[t.combatant_id] = {"duration": round(remaining, 1)}
            
        # Build cooldowns dict
        cooldowns = {}
        for c in self.combatants.values():
            if not c.is_attacking:
                remaining = max(0, (c.last_attack_time + c.attack_cooldown) - now)
                if remaining > 0:
                    cooldowns[c.id] = round(remaining, 1)

        # Build NPC intelligence (Goal/Plan)
        npc_intelligence = {}
        for cid, c in self.combatants.items():
            if c.agent:
                npc_intelligence[cid] = {
                    "goal": c.agent.goals[0].name if c.agent.goals else "Idle",
                    "plan": [a.name for a in c.agent.current_plan]
                }
        
        return {
            "status": "Active",
            "token_manager": {
                "available_tokens": 1 if not self.token_manager.active_token else 0,
                "active_tokens": active_tokens,
                "cooldowns": cooldowns
            },
            "attack_grid": self.grid.get_status(),
            "npc_intelligence": npc_intelligence
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def create_combat_orchestrator(max_attackers: int = 12) -> CombatOrchestrator:
    """Create a new combat orchestrator."""
    return CombatOrchestrator(max_attackers=max_attackers)


def quick_combat_round(
    enemies: list[tuple[str, str]],  # List of (id, type) tuples
    player_health: float = 1.0,
) -> list[dict]:
    """
    Quick combat simulation.
    Returns list of attacks that should occur.
    """
    orch = CombatOrchestrator()
    
    for eid, etype in enemies:
        enemy_type = EnemyType[etype.upper()] if etype.upper() in EnemyType.__members__ else EnemyType.SOLDIER
        orch.add_combatant(eid, eid, enemy_type)
    
    attacks = []
    for _ in range(3):  # Simulate 3 update cycles
        result = orch.update(player_health)
        if result:
            attacks.append(result)
    
    return attacks
