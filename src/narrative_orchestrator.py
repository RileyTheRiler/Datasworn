"""
Narrative Orchestrator - Master Integration System

Coordinates all narrative structure systems to provide comprehensive
guidance to the narrator for high-quality storytelling.

Integrates:
- Story Arc & Tension (story_graph.py)
- Callbacks & Foreshadowing (narrative_memory.py)
- Thematic Consistency (theme_engine.py)
- Narrative Variety (narrative_variety.py)
- Pacing Intelligence (prose_enhancement.py)
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List

from src.story_graph import StoryDAG, TensionCurve
from src.narrative_memory import NarrativeMemory
from src.theme_engine import ThemeEngine, create_starforged_themes
from src.narrative_variety import NarrativeVariety
from src.prose_enhancement import ProseEnhancementEngine

from src.emotional_storytelling import BondManager, BondEvent
from src.world_coherence import WorldStateCoherence, WorldFactType
from src.moral_dilemma import DilemmaGenerator, DilemmaType


@dataclass
class NarrativeOrchestrator:
    """Master coordinator for all narrative systems."""
    
    # Core systems
    story_graph: StoryDAG = field(default_factory=StoryDAG)
    narrative_memory: NarrativeMemory = field(default_factory=NarrativeMemory)
    theme_engine: ThemeEngine = field(default_factory=create_starforged_themes)
    narrative_variety: NarrativeVariety = field(default_factory=NarrativeVariety)
    prose_engine: ProseEnhancementEngine = field(default_factory=ProseEnhancementEngine)
    
    # New Backend Systems
    bond_manager: BondManager = field(default_factory=BondManager)
    world_coherence: WorldStateCoherence = field(default_factory=WorldStateCoherence)
    dilemma_generator: DilemmaGenerator = field(default_factory=DilemmaGenerator)
    
    # State
    current_scene: int = 0
    
    def advance_scene(self):
        """Advance all systems to next scene."""
        self.current_scene += 1
        self.narrative_memory.advance_scene()
        self.theme_engine.advance_scene()
        self.narrative_variety.advance_scene()
        self.prose_engine.sensory_tracker.advance_scene()
        self.world_coherence.advance_scene()
    
    def get_comprehensive_guidance(
        self,
        location: str = "",
        active_npcs: list[str] = None,
        player_action: str = "",
    ) -> str:
        """
        Generate comprehensive narrative guidance from all systems.
        
        This is the main entry point for narrator prompt enhancement.
        """
        sections = []
        active_npcs = active_npcs or []
        
        # 1. Story Position & Tension
        if self.story_graph.current_node:
            story_context = self.story_graph.get_narrative_context()
            if story_context:
                sections.append(story_context)
            
            # Tension guidance
            pacing_guidance = self.story_graph.tension_curve.get_pacing_guidance(self.current_scene)
            if pacing_guidance:
                sections.append(f"\\n<pacing>\\n{pacing_guidance}\\n</pacing>")
        
        # 2. Callbacks & Foreshadowing
        memory_guidance = self.narrative_memory.get_narrator_guidance()
        if memory_guidance:
            sections.append(f"\\n{memory_guidance}")
        
        # 3. Thematic Consistency
        theme_guidance = self.theme_engine.get_narrator_guidance()
        if theme_guidance:
            sections.append(f"\\n{theme_guidance}")
        
        # 4. Narrative Variety
        variety_guidance = self.narrative_variety.get_narrator_guidance()
        if variety_guidance:
            sections.append(f"\\n{variety_guidance}")
        
        # 5. Prose Enhancement
        prose_guidance = self.prose_engine.get_comprehensive_guidance(
            location=location,
            active_npcs=active_npcs,
        )
        if prose_guidance:
            sections.append(f"\\n{prose_guidance}")
            
        # 6. Emotional Bonds (New)
        bond_context = self.bond_manager.get_all_bonds_context()
        if bond_context:
            sections.append(f"\\n<relationship_context>\\n{bond_context}\\n</relationship_context>")
            
        # Quiet Moment Check
        moment_type, moment_prompt = self.bond_manager.quiet_tracker.get_quiet_moment(context=player_action)
        if moment_type:
            sections.append(f"\\n[PACING: A quiet moment is suggested ({moment_type}). {moment_prompt}]")

        # 7. World Coherence (New)
        coherence_context = self.world_coherence.get_coherence_context(location=location, active_npcs=active_npcs)
        if coherence_context:
            sections.append(f"\\n{coherence_context}")

        return "\\n".join(sections)
    
    def process_interaction(
        self,
        player_input: str,
        narrative_output: str,
        location: str,
        active_npcs: list[str] = None,
        roll_outcome: str = None
    ):
        """
        Process a complete interaction to update all tracking systems.
        
        Args:
            player_input: The user's action/dialogue
            narrative_output: The definition of what happened (AI response)
            location: Current location
            active_npcs: List of NPC names involved
            roll_outcome: Result of action roll if any
        """
        active_npcs = active_npcs or []
        
        # 1. Update Prose Engine
        self.prose_engine.process_narrative(
            narrative_output, 
            location, 
            active_npcs
        )
        
        # 2. Auto-detect & record narrative plants
        from src.narrative_memory import auto_detect_plants
        detected_plants = auto_detect_plants(narrative_output, self.current_scene)
        for plant_type, description, importance in detected_plants:
            self.narrative_memory.plant_element(plant_type, description, importance)
            
        # 3. Update Bonds
        # Simple heuristic: if player talks to NPC, record interaction
        # In a real system, we'd use an LLM classifier here
        for npc in active_npcs:
            # Check if interaction was positive or negative based on roll/keywords
            # For now, just presence is a small bond boost
            self.bond_manager.record_bond_event(
                npc_name=npc,
                description=f"Interacted in scene {self.current_scene}",
                bond_change=1,
                scene=self.current_scene
            )
            
        # 4. Track World Facts / Coherence
        # Again, simple heuristic or future LLM extraction
        # For now, we update location usage
        self.world_coherence.record_fact(
            WorldFactType.LOCATION_STATE, 
            location, 
            f"Visited in scene {self.current_scene}"
        )
        
        # 5. Check for Dilemmas
        # Only check periodically
        if (self.current_scene % 5 == 0) or (roll_outcome == "miss"):
            # This would trigger a future dilemma setup
            pass    
            
    def to_dict(self) -> dict:
        """Serialize all systems."""
        return {
            "story_graph": self.story_graph.to_dict(),
            "narrative_memory": self.narrative_memory.to_dict(),
            "theme_engine": self.theme_engine.to_dict(),
            "narrative_variety": self.narrative_variety.to_dict(),
            "prose_engine": self.prose_engine.to_dict(),
            "bond_manager": self.bond_manager.to_dict(),
            "world_coherence": self.world_coherence.to_dict(),
            "dilemma_generator": {}, # Stateless generator
            "current_scene": self.current_scene,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeOrchestrator":
        """Deserialize all systems."""
        orchestrator = cls()
        orchestrator.current_scene = data.get("current_scene", 0)
        
        if "story_graph" in data:
            orchestrator.story_graph = StoryDAG.from_dict(data["story_graph"])
        
        if "narrative_memory" in data:
            orchestrator.narrative_memory = NarrativeMemory.from_dict(data["narrative_memory"])
        
        if "theme_engine" in data:
            orchestrator.theme_engine = ThemeEngine.from_dict(data["theme_engine"])
        
        if "narrative_variety" in data:
            orchestrator.narrative_variety = NarrativeVariety.from_dict(data["narrative_variety"])
        
        if "prose_engine" in data:
            orchestrator.prose_engine = ProseEnhancementEngine.from_dict(data["prose_engine"])
            
        if "bond_manager" in data:
            orchestrator.bond_manager = BondManager.from_dict(data["bond_manager"])
            
        if "world_coherence" in data:
            orchestrator.world_coherence = WorldStateCoherence.from_dict(data["world_coherence"])
        
        return orchestrator


# =============================================================================
# Story Phase Detection
# =============================================================================

class StoryPhase:
    """Detect current story phase for director integration."""
    
    @staticmethod
    def detect_phase(story_graph: StoryDAG) -> str:
        """
        Detect current story phase based on act and tension.
        
        Returns: "setup", "escalation", "climax", or "resolution"
        """
        if not story_graph.current_node:
            return "setup"
        
        current_act = story_graph.get_current_act()
        tension_avg = story_graph.tension_curve.get_recent_average()
        
        # Act-based detection
        if current_act.value == 1:
            return "setup"
        elif current_act.value == 2:
            if tension_avg > 0.7:
                return "escalation"
            else:
                return "setup"
        elif current_act.value == 3:
            if tension_avg > 0.8:
                return "climax"
            else:
                return "resolution"
        
        return "escalation"
    
    @staticmethod
    def get_phase_guidance(phase: str) -> str:
        """Get narrative guidance for current phase."""
        guidance = {
            "setup": "Establish characters, relationships, and stakes. Build the world. Plant seeds for later.",
            "escalation": "Raise stakes. Complicate situations. Test characters. Increase tension.",
            "climax": "Peak tension. Major confrontations. Decisive moments. High emotional impact.",
            "resolution": "Resolve conflicts. Show consequences. Provide closure. Hint at future.",
        }
        return guidance.get(phase, "")
