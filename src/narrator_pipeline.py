"""
Narrator Pipeline - Composable system injections for narrative generation.
Breaks down the monolithic narrator_node into modular, testable functions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from src.logging_config import get_logger
from src.config import config

logger = get_logger("narrator")


@dataclass
class NarrativeContext:
    """Context accumulated through the pipeline."""
    # Core game state
    player_input: str = ""
    character_name: str = "Traveler"
    location: str = "the void"

    # Roll information
    roll_result: str = ""
    roll_outcome: str = ""

    # Director guidance
    pacing: str = "standard"
    tone: str = "mysterious"
    director_notes: str = ""
    active_beats: list[str] = field(default_factory=list)
    tension_level: float = 0.5

    # Memory context
    memory_context: str = ""

    # Voice context
    voice_context: str = ""
    npc_behavior_context: str = ""

    # Few-shot examples
    few_shot_context: str = ""

    # System prompt injections (accumulated)
    system_injections: list[str] = field(default_factory=list)

    # State references (for systems that need full state)
    state: dict[str, Any] = field(default_factory=dict)

    def add_injection(self, section_name: str, content: str) -> None:
        """Add a labeled injection to the system prompt."""
        if content and content.strip():
            self.system_injections.append(f"<{section_name}>\n{content.strip()}\n</{section_name}>")

    def get_combined_injections(self) -> str:
        """Get all injections as a single string."""
        return "\n\n".join(self.system_injections)


# Type for pipeline stage functions
PipelineStage = Callable[[NarrativeContext], NarrativeContext]


def stage_memory_context(ctx: NarrativeContext) -> NarrativeContext:
    """Inject memory context (recent events, relationships, campaign history)."""
    try:
        memory_state = ctx.state.get("memory")
        if not memory_state:
            return ctx

        context_parts = []

        # Recent scene summaries
        if hasattr(memory_state, 'scene_summaries') and memory_state.scene_summaries:
            recent = memory_state.scene_summaries[-config.narrative.max_recent_scene_summaries:]
            context_parts.append("[Recent Events]\n" + "\n".join(f"- {s}" for s in recent))

        # Key relationships from campaign
        if hasattr(memory_state, 'key_relationships') and memory_state.key_relationships:
            rels = [f"{npc}: {rel}" for npc, rel in list(memory_state.key_relationships.items())[:config.narrative.max_key_relationships]]
            context_parts.append("[Key Relationships]\n" + "\n".join(f"- {r}" for r in rels))

        # Major story beats
        if hasattr(memory_state, 'major_beats') and memory_state.major_beats:
            context_parts.append("[Campaign History]\n" + "\n".join(f"- {b}" for b in memory_state.major_beats[-config.narrative.max_major_beats:]))

        if context_parts:
            ctx.memory_context = "\n\n".join(context_parts)
            ctx.add_injection("memory_context", ctx.memory_context)

    except Exception as e:
        logger.debug(f"Memory context injection fallback: {e}")

    return ctx


def stage_voice_profiles(ctx: NarrativeContext) -> NarrativeContext:
    """Inject character voice profiles for NPCs in the scene."""
    try:
        voice_state = ctx.state.get("voices")
        if not voice_state or not hasattr(voice_state, 'active_characters'):
            return ctx

        voice_parts = []
        for char_name in voice_state.active_characters[:config.narrative.max_npcs_in_scene]:
            profile = voice_state.profiles.get(char_name.lower(), {})
            if profile:
                lines = [f"[CHARACTER VOICE: {profile.get('name', char_name)}]"]
                if profile.get('speech_patterns'):
                    lines.append(f"Speech: {'; '.join(profile['speech_patterns'][:2])}")
                if profile.get('relationship_to_player'):
                    lines.append(f"Relationship: {profile['relationship_to_player']}")
                voice_parts.append("\n".join(lines))

        if voice_parts:
            ctx.voice_context = "\n\n".join(voice_parts)
            ctx.add_injection("character_voices", ctx.voice_context)

    except Exception as e:
        logger.debug(f"Voice profile injection fallback: {e}")

    return ctx


def stage_npc_behavior(ctx: NarrativeContext) -> NarrativeContext:
    """Inject NPC behavior tree evaluations."""
    try:
        memory_state = ctx.state.get("memory")
        voice_state = ctx.state.get("voices")

        if not memory_state or not hasattr(memory_state, 'active_npcs'):
            return ctx

        from src.behavior_tree import evaluate_npc_behavior

        bt_parts = []
        for npc_name in memory_state.active_npcs[:config.narrative.max_npcs_in_scene]:
            # Get archetype from voice profiles or default
            archetype = "civilian"
            if voice_state and hasattr(voice_state, 'profiles'):
                profile = voice_state.profiles.get(npc_name.lower(), {})
                archetype = profile.get("archetype", "civilian")

            # Evaluate behavior tree
            bt_context = evaluate_npc_behavior(
                npc_name=npc_name,
                archetype=archetype,
                player_name=ctx.character_name,
                player_reputation=0.5,
                in_combat=False,
                has_quest=False,
            )

            if bt_context.action and bt_context.dialogue_intent:
                bt_parts.append(
                    f"[NPC BEHAVIOR: {npc_name}]\n"
                    f"Action: {bt_context.action}\n"
                    f"Manner: {bt_context.dialogue_intent}"
                )

        if bt_parts:
            ctx.npc_behavior_context = "\n\n".join(bt_parts)
            ctx.add_injection("npc_behaviors", ctx.npc_behavior_context)

    except Exception as e:
        logger.debug(f"NPC behavior injection fallback: {e}")

    return ctx


def stage_few_shot_examples(ctx: NarrativeContext) -> NarrativeContext:
    """Inject tone-matched few-shot examples."""
    try:
        from src.narrator import get_examples_for_tone

        examples = get_examples_for_tone(ctx.tone, ctx.pacing, count=config.narrative.few_shot_example_count)
        if examples:
            few_shot_parts = []
            for ex in examples:
                few_shot_parts.append(
                    f"[Example - {ex.get('roll', 'Narrative')}]\n{ex.get('narrative', '')[:config.narrative.max_example_length]}"
                )
            ctx.few_shot_context = "\n\n".join(few_shot_parts)
            ctx.add_injection("style_examples", ctx.few_shot_context)

    except Exception as e:
        logger.debug(f"Few-shot examples injection fallback: {e}")

    return ctx


def stage_feedback_learning(ctx: NarrativeContext) -> NarrativeContext:
    """Inject learned preferences from feedback system."""
    try:
        from src.feedback_learning import FeedbackLearningEngine, PromptModifier, ExampleRetriever

        feedback_engine = FeedbackLearningEngine(db_path=config.paths.feedback_db)

        stats = feedback_engine.db.get_statistics()

        if stats["total_paragraphs"] >= config.feedback.min_paragraphs_for_analysis:
            current_profile = feedback_engine.current_profile
            should_analyze = (
                current_profile is None or
                stats["total_paragraphs"] - current_profile.total_decisions_analyzed >= config.feedback.reanalysis_threshold
            )

            if should_analyze:
                new_profile = feedback_engine.run_preference_analysis()
                feedback_engine.current_profile = new_profile

            if feedback_engine.current_profile:
                modifier = PromptModifier(feedback_engine.current_profile)
                preference_injection = modifier.generate_modifications()
                if preference_injection:
                    ctx.add_injection("learned_preferences", preference_injection)

            # Add few-shot examples from similar accepted paragraphs
            retriever = ExampleRetriever(feedback_engine.db)
            context = {
                "pacing": ctx.pacing,
                "tone": ctx.tone,
                "scene_type": "general",
            }
            few_shot_prompt = retriever.build_few_shot_prompt(
                context,
                n_positive=config.feedback.positive_examples,
                n_negative=config.feedback.negative_examples
            )
            if few_shot_prompt:
                ctx.add_injection("feedback_examples", few_shot_prompt)

    except Exception as e:
        logger.debug(f"Feedback learning injection fallback: {e}")

    return ctx


def stage_narrative_craft(ctx: NarrativeContext) -> NarrativeContext:
    """Inject narrative craft guidance (genre, McKee structure, archetypes)."""
    try:
        from src.narrative_craft import NarrativeCraftEngine

        craft_state = ctx.state.get("narrative_craft", {})
        craft_engine = NarrativeCraftEngine.from_dict(craft_state) if craft_state else NarrativeCraftEngine()
        craft_context = craft_engine.get_craft_context()

        if craft_context:
            ctx.add_injection("narrative_craft", craft_context)

        craft_engine.scenes_in_current_beat += 1

    except Exception as e:
        logger.debug(f"Narrative craft injection fallback: {e}")

    return ctx


def stage_prose_craft(ctx: NarrativeContext) -> NarrativeContext:
    """Inject prose craft guidance (sentence rhythm, sensory detail, dialogue)."""
    try:
        from src.prose_craft import ProseCraftEngine

        prose_engine = ProseCraftEngine()
        prose_guidance = prose_engine.generate_comprehensive_guidance(
            tension_level=ctx.tension_level,
            emotional_state=ctx.tone,
            pov_character=ctx.character_name,
            scene_type="general",
            location_type=ctx.location,
        )

        if prose_guidance:
            ctx.add_injection("prose_craft", prose_guidance)

    except Exception as e:
        logger.debug(f"Prose craft injection fallback: {e}")

    return ctx


def stage_world_coherence(ctx: NarrativeContext) -> NarrativeContext:
    """Inject world coherence guidance (state tracking, agency validation)."""
    try:
        from src.world_coherence import WorldCoherenceEngine

        coherence_state = ctx.state.get("world_coherence", {})
        coherence_engine = WorldCoherenceEngine.from_dict(coherence_state) if coherence_state else WorldCoherenceEngine()

        memory_state = ctx.state.get("memory")
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []

        coherence_guidance = coherence_engine.get_comprehensive_guidance(
            location=ctx.location,
            active_npcs=active_npcs[:config.narrative.max_npcs_in_scene],
            is_session_start=False,
            protagonist=ctx.character_name,
        )

        if coherence_guidance:
            ctx.add_injection("world_coherence", coherence_guidance)

    except Exception as e:
        logger.debug(f"World coherence injection fallback: {e}")

    return ctx


def stage_quest_lore(ctx: NarrativeContext) -> NarrativeContext:
    """Inject quest and lore context."""
    try:
        from src.quest_lore import QuestLoreEngine

        quest_lore_state = ctx.state.get("quest_lore")
        if not quest_lore_state:
            return ctx

        ql_data = quest_lore_state.model_dump() if hasattr(quest_lore_state, 'model_dump') else quest_lore_state
        ql_engine = QuestLoreEngine.from_dict(ql_data) if ql_data else QuestLoreEngine()

        memory_state = ctx.state.get("memory")
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []

        ql_guidance = ql_engine.get_comprehensive_guidance(
            current_location=ctx.location,
            active_npcs=active_npcs[:config.narrative.max_npcs_in_scene],
            current_day=1,
        )

        if ql_guidance:
            ctx.add_injection("quest_lore", ql_guidance)

    except Exception as e:
        logger.debug(f"Quest/lore injection fallback: {e}")

    return ctx


def stage_bonds_and_themes(ctx: NarrativeContext) -> NarrativeContext:
    """Inject character bonds and campaign theme context."""
    try:
        # Bond relationships
        emotional_state = ctx.state.get("emotional_storytelling", {})
        if emotional_state:
            from src.emotional_storytelling import BondManager

            bond_manager = BondManager.from_dict(emotional_state) if emotional_state else BondManager()
            bond_context = bond_manager.get_all_bonds_context()

            if ctx.tension_level > config.director.tension_threshold_high - 0.1:
                callback = bond_manager.get_callback_for_climax()
                if callback:
                    bond_context += f"\n\n[CALLBACK OPPORTUNITY]\n{callback}"

            if bond_context:
                ctx.add_injection("character_bonds", bond_context)

        # Campaign theme
        theme_state = ctx.state.get("theme_tracker", {})
        if theme_state:
            from src.moral_dilemma import ThemeTracker

            theme = ThemeTracker.from_dict(theme_state) if theme_state else None
            if theme:
                theme_context = theme.get_theme_context()
                if theme_context:
                    ctx.add_injection("campaign_theme", theme_context)

    except Exception as e:
        logger.debug(f"Bonds/themes injection fallback: {e}")

    return ctx


# Default pipeline stages in order
DEFAULT_PIPELINE: list[PipelineStage] = [
    stage_memory_context,
    stage_voice_profiles,
    stage_npc_behavior,
    stage_few_shot_examples,
    stage_feedback_learning,
    stage_narrative_craft,
    stage_prose_craft,
    stage_world_coherence,
    stage_quest_lore,
    stage_bonds_and_themes,
]


def run_pipeline(
    ctx: NarrativeContext,
    stages: Optional[list[PipelineStage]] = None
) -> NarrativeContext:
    """
    Run the narrative pipeline, accumulating context through each stage.

    Args:
        ctx: Initial narrative context
        stages: Optional custom list of stages (defaults to DEFAULT_PIPELINE)

    Returns:
        Context with all injections accumulated
    """
    stages = stages or DEFAULT_PIPELINE

    for stage in stages:
        try:
            ctx = stage(ctx)
        except Exception as e:
            stage_name = stage.__name__ if hasattr(stage, '__name__') else str(stage)
            logger.warning(f"Pipeline stage '{stage_name}' failed: {e}")
            # Continue with other stages even if one fails

    return ctx


def create_context_from_state(state: dict[str, Any]) -> NarrativeContext:
    """
    Create a NarrativeContext from game state.

    Args:
        state: Full game state dictionary

    Returns:
        NarrativeContext populated with core values
    """
    character = state.get("character")
    world = state.get("world")
    last_roll = state.get("last_roll")
    director_state = state.get("director")
    messages = state.get("messages", [])

    # Get last player input
    player_input = ""
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "user":
            player_input = msg.get("content", "")
            break

    ctx = NarrativeContext(
        player_input=player_input,
        character_name=character.name if character else "Traveler",
        location=world.current_location if world else "the void",
        state=state,
    )

    if last_roll:
        ctx.roll_result = last_roll.result_text if hasattr(last_roll, 'result_text') else ""
        ctx.roll_outcome = last_roll.outcome if hasattr(last_roll, 'outcome') else ""

    if director_state:
        ctx.pacing = director_state.last_pacing if hasattr(director_state, 'last_pacing') else "standard"
        ctx.tone = director_state.last_tone if hasattr(director_state, 'last_tone') else "mysterious"
        ctx.director_notes = director_state.last_notes if hasattr(director_state, 'last_notes') else ""
        ctx.active_beats = director_state.active_beats if hasattr(director_state, 'active_beats') else []
        ctx.tension_level = director_state.tension_level if hasattr(director_state, 'tension_level') else 0.5

    return ctx
