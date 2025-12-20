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
from src.narrative import (
    PayoffTracker, NPCMemoryBank, ConsequenceManager, ChoiceEchoSystem,
    OpeningHookSystem, NPCEmotionalStateMachine, MoralReputationSystem, DramaticIronyTracker,
    StoryBeatGenerator, PlotManager, BranchingNarrativeSystem, NPCGoalPursuitSystem,
    EndingPreparationSystem, ImpossibleChoiceGenerator, FlashbackSystem,
    EndingPreparationSystem, ImpossibleChoiceGenerator, FlashbackSystem,
    UnreliableNarratorSystem, MetaNarrativeSystem, NPCSkillSystem, NarrativeMultiplayerSystem
)
from src.environmental_storytelling import EnvironmentalStoryGenerator, CallbackManager, create_environmental_generator
from src.combat_orchestrator import CombatOrchestrator, create_combat_orchestrator
from src.utility_ai import evaluate_tactical_decision
from src.goap import plan_npc_action
from src.psychology import DreamSequenceEngine, PhobiaSystem, AddictionSystem, MoralInjurySystem, AttachmentSystem, TrustDynamicsSystem



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
    
    # Narrative Depth (New)
    callback_manager: CallbackManager = field(default_factory=CallbackManager)
    
    # Smart Event Detection (New)
    event_detector: Any = field(default=None)  # Lazy loaded to avoid circular imports? No, passed in.
    
    # Combat & AI (New)
    combat_system: CombatOrchestrator = field(default_factory=create_combat_orchestrator)
    
    # Phase 1 Systems
    payoff_tracker: PayoffTracker = field(default_factory=PayoffTracker)
    npc_memories: Dict[str, NPCMemoryBank] = field(default_factory=dict)
    consequence_manager: ConsequenceManager = field(default_factory=ConsequenceManager)
    echo_system: ChoiceEchoSystem = field(default_factory=ChoiceEchoSystem)
    
    # Phase 2 Systems
    opening_hooks: OpeningHookSystem = field(default_factory=OpeningHookSystem)
    npc_emotions: NPCEmotionalStateMachine = field(default_factory=NPCEmotionalStateMachine)
    reputation: MoralReputationSystem = field(default_factory=MoralReputationSystem)
    irony_tracker: DramaticIronyTracker = field(default_factory=DramaticIronyTracker)
    
    # Phase 3 Systems
    story_beats: StoryBeatGenerator = field(default_factory=StoryBeatGenerator)
    plot_manager: PlotManager = field(default_factory=PlotManager)
    branching_system: BranchingNarrativeSystem = field(default_factory=BranchingNarrativeSystem)
    npc_goals: NPCGoalPursuitSystem = field(default_factory=NPCGoalPursuitSystem)
    
    # Phase 4 Systems
    ending_system: EndingPreparationSystem = field(default_factory=EndingPreparationSystem)
    impossible_choices: ImpossibleChoiceGenerator = field(default_factory=ImpossibleChoiceGenerator)
    environmental_storyteller: EnvironmentalStoryGenerator = field(default_factory=create_environmental_generator)
    flashback_system: FlashbackSystem = field(default_factory=FlashbackSystem)
    
    # Phase 5 Systems
    unreliable_system: UnreliableNarratorSystem = field(default_factory=UnreliableNarratorSystem)
    meta_system: MetaNarrativeSystem = field(default_factory=MetaNarrativeSystem)
    npc_skills: NPCSkillSystem = field(default_factory=NPCSkillSystem)
    multiplayer_system: NarrativeMultiplayerSystem = field(default_factory=NarrativeMultiplayerSystem)
    
    # Psychological Systems
    dream_engine: DreamSequenceEngine = field(default_factory=DreamSequenceEngine)
    phobia_system: PhobiaSystem = field(default_factory=PhobiaSystem)
    
    # Psychological Systems - Phase 2
    addiction_system: AddictionSystem = field(default_factory=AddictionSystem)
    moral_injury_system: MoralInjurySystem = field(default_factory=MoralInjurySystem)
    
    # Psychological Systems - Phase 3
    attachment_system: AttachmentSystem = field(default_factory=AttachmentSystem)
    trust_dynamics: TrustDynamicsSystem = field(default_factory=TrustDynamicsSystem)
    
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
        
        # Advance Consequence Chains
        triggered_events = self.consequence_manager.check_progression(self.current_scene)
        self._pending_consequences = triggered_events
        
        # Advance Plots (Phase 3)
        if self.plot_manager.active_thread_id:
             self.plot_manager.advance_plot(self.plot_manager.active_thread_id, self.current_scene)
             
        # Simulate background NPC actions (Phase 3)
        self._pending_rumors = self.npc_goals.advance_npc_goals([]) # Pass active NPCs if we knew them ahead of time
    
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
        # 16. Unreliable Narrator (Phase 5)
        # Check if we need to distort perception
        distortion = self.unreliable_system.get_narrator_instruction()
        if distortion:
             sections.append(f"\\n{distortion}")

        if prose_guidance:
            sections.append(f"\\n{prose_guidance}")
            
        # 13. Flashback Context (Phase 4)
        fb_context = self.flashback_system.get_context_prefix()
        if fb_context:
            sections.insert(0, fb_context)
            
        # 17. Multiplayer Spotlight (Phase 5)
        spotlight = self.multiplayer_system.get_spotlight_guidance()
        if spotlight:
             sections.append(f"\\n{spotlight}")
             
        # 18. Panic Check (Psychology Phase 1)
        panic_status = self.phobia_system.get_panic_status()
        if panic_status:
             sections.append(f"\\n[WARNING: {panic_status} - Describe hyperventilation, terror, and irrational action.]")
             
        # 19. Addiction Withdrawal (Psychology Phase 2)
        withdrawal_effects = self.addiction_system.get_withdrawal_effects()
        if withdrawal_effects:
            for effect in withdrawal_effects:
                sections.append(f"\\n[{effect}]")
                
        # 20. Moral Guilt (Psychology Phase 2)
        guilt_context = self.moral_injury_system.get_guilt_context()
        if guilt_context:
            sections.append(f"\\n{guilt_context}")
            
        # 21. Attachment/Trust Context (Psychology Phase 3)
        for npc_id in active_npcs:
            attach_ctx = self.attachment_system.get_relationship_guidance(npc_id)
            if attach_ctx:
                sections.append(f"\\n{attach_ctx}")
            trust_ctx = self.trust_dynamics.get_trust_context(npc_id)
            if trust_ctx:
                sections.append(f"\\n{trust_ctx}")

        # 1. World & Environmental Context (Phase 4 Enhanced)
        # Use new Environmental Storyteller
        discovery = self.environmental_storyteller.generate_discovery(location_context=location)
        sections.append(f"\\n{discovery.get_narrator_context()}")
        
        # Add Show, Don't Tell Guidance (once per scene ideally, but here is fine)
        sections.append(f"\\n{self.environmental_storyteller.get_show_dont_tell_guidance()}")

        # 2. Narrative Callbacks (New)
        callback = self.callback_manager.get_callback_for_moment(
            current_scene=self.current_scene, 
            context=player_action,
            character=active_npcs[0] if active_npcs else None
        )
        if callback:
             sections.append(f"\\n{callback}")

        # 3. Combat Tactics (New)
        if self.combat_system.combatants:
             combat_ctx = self.combat_system.get_combat_context()
             sections.append(f"\\n{combat_ctx}")
            
        # 4. NPC Plans (GOAP) (New)
        # Use simple heuristic: if there's a leader or specific goal
        if active_npcs and not self.combat_system.combatants:
             # Example: create a plan for one NPC
             leader = active_npcs[0]
             # Demo goal: Gather resources
             plan = plan_npc_action(
                 goal_name="prepare_defenses",
                 goal_conditions={"has_wood": True, "has_iron": True},
                 current_state={"near_trees": True},
                 action_type="resource"
             )
             if plan:
                sections.append(f"\\n[NPC PLAN: {leader}]\\n" + "\\n".join([f"- {a['description']}" for a in plan]))
        
        # 6. Emotional Bonds (New)
        bond_context = self.bond_manager.get_all_bonds_context()
        if bond_context:
            sections.append(f"\\n<relationship_context>\\n{bond_context}\\n</relationship_context>")
            
        # Quiet Moment Check
        moment_data = self.bond_manager.quiet_tracker.get_quiet_moment(context=player_action)
        moment_type = moment_data.get("type")
        moment_prompt = moment_data.get("prompt")
        if moment_type:
            sections.append(f"\\n[PACING: A quiet moment is suggested ({moment_type}). {moment_prompt}]")

        # 7. World Coherence (New)
        coherence_context = self.world_coherence.get_coherence_context(location=location, active_npcs=active_npcs)
        if coherence_context:
            sections.append(f"\\n{coherence_context}")

        # 8. Narrative Payoffs (New)
        overdue_seeds = self.narrative_memory.get_pending_payoffs()
        if overdue_seeds:
            seed_list = "\\n".join([f"  - UNRESOLVED {s.plant_type.value}: {s.description}" for s in overdue_seeds])
            sections.append(f"\\n<payoff_alert>\\nPAYOFFS DUE SOON:\\n{seed_list}\\nConsider resolving one of these now.\\n</payoff_alert>")

        # 9. Consequence Triggers (New)
        # If we had pending consequences from advance_scene
        if getattr(self, "_pending_consequences", None):
            cons_list = "\\n".join([f"  - FROM {e['cause']}: {e['event']} (Severity: {e['severity']})" for e in self._pending_consequences])
            sections.append(f"\\n<consequence_trigger>\\nCONSEQUENCES MANIFESTING:\\n{cons_list}\\nIntegrate these events into the scene logic.\\n</consequence_trigger>")
            self._pending_consequences = []

        # 10. Echoes (New)
        # Simple check for active NPCs
        for npc in active_npcs:
            if npc in self.npc_memories:
                echo = self.npc_memories[npc].generate_callback(self.current_scene)
                if echo:
                    sections.append(f"\\n[CALLBACK SUGGESTION for {npc}: {echo}]")
            
            # Choice echoes
            choice_recall = self.echo_system.generate_echo(
                npc_id=npc, 
                current_scene=self.current_scene, 
                context=player_action
            )
            if choice_recall:
                 sections.append(f"\\n[CHOICE ECHO for {npc}: {choice_recall}]")

        # 11. NPC Depth Context (Phase 2)
        # Add basic reputation summary
        rep_summary = self.reputation.get_reputation_summary()
        sections.append(f"\\n<reputation_context>\\nYour Reputation: {rep_summary}\\n</reputation_context>")
        
        # Add NPC Emotions
        for npc in active_npcs:
            emo_state = self.npc_emotions.get_state(npc)
            if emo_state.intensity > 0.3:
                 sections.append(f"\\n[EMOTION: {npc} is {emo_state.current_state.value} (Intensity: {emo_state.intensity:.1f})]")
                 
        # Add Irony Opportunities
        irony_ops = self.irony_tracker.identify_irony_opportunities(active_npcs)
        if irony_ops:
            irony_text = "\\n".join([f"  - {op}" for op in irony_ops])
            sections.append(f"\\n<dramatic_irony>\\nOPPORTUNITIES:\\n{irony_text}\\n</dramatic_irony>")   

        # 12. Advanced Narrative (Phase 3)
        # Suggest Beat
        beat = self.story_beats.suggest_next_beat(tension=0.5) # Todo: hook up real tension
        sections.append(f"\\n[SUGGESTED BEAT: {beat.value}]")
        
        # Suggest Plot Thread
        next_thread = self.plot_manager.suggest_next_thread(self.current_scene)
        if next_thread:
             sections.append(f"\\n[PLOT FOCUS: {next_thread.title} ({next_thread.plot_type.value}) - {next_thread.description}]")
             
        # NPC Rumors
        if getattr(self, "_pending_rumors", None):
            rumor_text = "\\n".join([f"  - {r}" for r in self._pending_rumors])
            sections.append(f"\\n<world_rumors>\\nNEWS FROM AFAR:\\n{rumor_text}\\n</world_rumors>")
            self._pending_rumors = []
            
        # 14. Dilemma Check (Phase 4)
        if self.impossible_choices.active_dilemma and not self.impossible_choices.active_dilemma.resolved:
            d = self.impossible_choices.active_dilemma
            sections.append(f"\\n[ACTIVE DILEMMA: {d.description} | A: {d.option_a.description} | B: {d.option_b.description}]")

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
        try:
            from src.smart_event_detection import SmartEventDetector, EventType
            from src.narrative_memory import PlantType
            
            # Initialize detector if needed (it wasn't in __init__ properly, so lazy load or use field)
            if not self.event_detector:
                self.event_detector = SmartEventDetector(use_llm=True) # Assume LLM enabled for this high-level orchestrator
                
            detected_events = self.event_detector.detect_events(
                narrative=narrative_output,
                location=location,
                active_npcs=active_npcs,
                player_name="Player" # Todo: pass character name
            )
            
            # Map DetectedEvents to NarrativeMemory Plants
            for event in detected_events:
                plant_type = None
                
                # Mapping logic
                if event.event_type in [EventType.PROMISE, EventType.OATH]:
                    plant_type = PlantType.PROMISE
                elif event.event_type in [EventType.KILL, EventType.WOUND, EventType.THREAT, EventType.BETRAY]:
                    plant_type = PlantType.THREAT
                elif event.event_type in [EventType.DISCOVER, EventType.LEARN_SECRET, EventType.SOLVE_MYSTERY]:
                    plant_type = PlantType.MYSTERY
                elif event.event_type in [EventType.ACQUIRE, EventType.STEAL, EventType.LOSE]:
                    plant_type = PlantType.OBJECT
                elif event.event_type in [EventType.ALLY, EventType.ROMANCE, EventType.INSULT, EventType.HONOR]:
                    plant_type = PlantType.RELATIONSHIP
                    
                if plant_type:
                    self.narrative_memory.plant_element(
                        plant_type=plant_type,
                        description=f"{event.description} ({event.event_type.value})",
                        importance=event.severity,
                        involved_characters=event.entities,
                        related_themes=[event.location] if event.location else []
                    )
        except Exception as e:
            # Fallback to simple detection if LLM/Import fails
            print(f"Smart Event Detection failed: {e}")
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
            
        # 6. Update NPC Memories (New)
        for npc in active_npcs:
            if npc not in self.npc_memories:
                self.npc_memories[npc] = NPCMemoryBank(npc_id=npc)
            
            # Record that this interaction happened
            # We assume a general "interaction" topic for now unless parsed
            self.npc_memories[npc].record_interaction(
                scene_num=self.current_scene,
                topic="general_interaction",
                content=narrative_output[:100], # Store brief snippet
                emotion="NEUTRAL" # Todo: derive from sentiment analysis
            )
            
        # 7. Update Reputation (Phase 2)
        # Rough heuristic for now - real system would use LLM analysis of player_action
        if "kill" in player_input.lower() or "attack" in player_input.lower():
            self.reputation.record_choice("Violence used", mercy_delta=-5)
        elif "save" in player_input.lower() or "help" in player_input.lower():
            self.reputation.record_choice("Altruism shown", mercy_delta=5, selfless_delta=5)
            
        # 8. Update Emotions (Phase 2)
        # Decay old emotions first
        for npc in self.npc_emotions.states:
             self.npc_emotions.decay_emotion(npc)
        
        # Trigger reactions based on keywords
        # Hardcoded for demo - better to use LLM event detection
        if "threat" in player_input.lower():
            for npc in active_npcs:
                self.npc_emotions.process_event(npc, "THREATENED")
                
        # 9. Store Narrative Callback (New)
        self.callback_manager.store_moment(
            scene=self.current_scene,
            description=narrative_output[:200], # Capture snippet
            characters=active_npcs,
            emotional_weight=0.5, # Base weight
            ideal_context=location
        )
        
        # 10. Update Combat State (New)
        # 10. Update Combat State (New)
        # Simple heuristic: if action implies violence, update combat
        if any(w in player_input.lower() for w in ["attack", "shoot", "hit", "fire", "fight"]):
             self.combat_system.update(player_health=1.0) # Placeholder health
                
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
            # Phase 1 Persistence
            "payoff_tracker": self.payoff_tracker.to_dict(),
            "npc_memories": {nid: mem.to_dict() for nid, mem in self.npc_memories.items()},
            "consequence_manager": self.consequence_manager.to_dict(),
            "echo_system": self.echo_system.to_dict(),
            # Phase 2 Persistence
            "npc_emotions": self.npc_emotions.to_dict(),
            "reputation": self.reputation.to_dict(),
            "irony_tracker": self.irony_tracker.to_dict(),
            # Phase 3 Persistence
            "story_beats": self.story_beats.to_dict(),
            "plot_manager": self.plot_manager.to_dict(),
            "branching_system": self.branching_system.to_dict(),
            "npc_goals": self.npc_goals.to_dict(),
            # Phase 4 Persistence
            "ending_system": self.ending_system.to_dict(),
            "impossible_choices": self.impossible_choices.to_dict(),
            "environmental_storyteller": self.environmental_storyteller.to_dict(),
            "flashback_system": self.flashback_system.to_dict(),
            # Phase 5 Persistence
            "unreliable_system": self.unreliable_system.to_dict(),
            "meta_system": self.meta_system.to_dict(),
            "npc_skills": self.npc_skills.to_dict(),
            "multiplayer_system": self.multiplayer_system.to_dict(),
            # Psychology Persistence
            "dream_engine": self.dream_engine.to_dict(),
            "phobia_system": self.phobia_system.to_dict(),
            # Psychology Phase 2 Persistence
            "addiction_system": self.addiction_system.to_dict(),
            "moral_injury_system": self.moral_injury_system.to_dict(),
            # Psychology Phase 3 Persistence
            "attachment_system": self.attachment_system.to_dict(),
            "attachment_system": self.attachment_system.to_dict(),
            "attachment_system": self.attachment_system.to_dict(),
            "trust_dynamics": self.trust_dynamics.to_dict(),
            "callback_manager": self.callback_manager.to_dict(),
            "combat_system": self.combat_system.to_dict(),
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
            
        # Phase 1 Rehydration
        if "payoff_tracker" in data:
            orchestrator.payoff_tracker = PayoffTracker.from_dict(data["payoff_tracker"])
            
        if "npc_memories" in data:
            orchestrator.npc_memories = {
                nid: NPCMemoryBank.from_dict(mem_data) 
                for nid, mem_data in data["npc_memories"].items()
            }
            
        if "consequence_manager" in data:
            orchestrator.consequence_manager = ConsequenceManager.from_dict(data["consequence_manager"])
            
        if "echo_system" in data:
            orchestrator.echo_system = ChoiceEchoSystem.from_dict(data["echo_system"])
            
        # Phase 2 Rehydration
        if "npc_emotions" in data:
            orchestrator.npc_emotions = NPCEmotionalStateMachine.from_dict(data["npc_emotions"])
            
        if "reputation" in data:
            orchestrator.reputation = MoralReputationSystem.from_dict(data["reputation"])
            
        if "irony_tracker" in data:
            orchestrator.irony_tracker = DramaticIronyTracker.from_dict(data["irony_tracker"])
            
        # Phase 3 Rehydration
        if "story_beats" in data:
            orchestrator.story_beats = StoryBeatGenerator.from_dict(data["story_beats"])
            
        if "plot_manager" in data:
            orchestrator.plot_manager = PlotManager.from_dict(data["plot_manager"])
            
        if "branching_system" in data:
            orchestrator.branching_system = BranchingNarrativeSystem.from_dict(data["branching_system"])
            
        if "npc_goals" in data:
            orchestrator.npc_goals = NPCGoalPursuitSystem.from_dict(data["npc_goals"])
            
        # Phase 4 Rehydration
        if "ending_system" in data:
            orchestrator.ending_system = EndingPreparationSystem.from_dict(data["ending_system"])
            
        if "dilemma_generator" in data: # Handle legacy/old dilemma generator if needed
             pass

        if "impossible_choices" in data:
            orchestrator.impossible_choices = ImpossibleChoiceGenerator.from_dict(data["impossible_choices"])
            
        if "environmental_storyteller" in data:
            orchestrator.environmental_storyteller = EnvironmentalStoryteller.from_dict(data["environmental_storyteller"])
            
        if "flashback_system" in data:
            orchestrator.flashback_system = FlashbackSystem.from_dict(data["flashback_system"])
            
        # Phase 5 Rehydration
        if "unreliable_system" in data:
            orchestrator.unreliable_system = UnreliableNarratorSystem.from_dict(data["unreliable_system"])
            
        if "meta_system" in data:
            orchestrator.meta_system = MetaNarrativeSystem.from_dict(data["meta_system"])
            
        if "npc_skills" in data:
            orchestrator.npc_skills = NPCSkillSystem.from_dict(data["npc_skills"])
            
        if "multiplayer_system" in data:
            orchestrator.multiplayer_system = NarrativeMultiplayerSystem.from_dict(data["multiplayer_system"])
            
        # Psychology Rehydration
        if "dream_engine" in data:
            orchestrator.dream_engine = DreamSequenceEngine.from_dict(data["dream_engine"])
            
        if "phobia_system" in data:
            orchestrator.phobia_system = PhobiaSystem.from_dict(data["phobia_system"])
            
        # Psychology Phase 2 Rehydration
        if "addiction_system" in data:
            orchestrator.addiction_system = AddictionSystem.from_dict(data["addiction_system"])
            
        if "moral_injury_system" in data:
            orchestrator.moral_injury_system = MoralInjurySystem.from_dict(data["moral_injury_system"])
            
        # Psychology Phase 3 Rehydration
        if "attachment_system" in data:
            orchestrator.attachment_system = AttachmentSystem.from_dict(data["attachment_system"])
            
        if "trust_dynamics" in data:
            orchestrator.trust_dynamics = TrustDynamicsSystem.from_dict(data["trust_dynamics"])
            
        if "callback_manager" in data:
            orchestrator.callback_manager = CallbackManager.from_dict(data["callback_manager"])
            
        if "combat_system" in data:
            orchestrator.combat_system = CombatOrchestrator.from_dict(data["combat_system"])
        
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
