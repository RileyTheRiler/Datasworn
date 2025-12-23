"""
LangGraph Node Functions for Starforged AI Game Master.
Each node processes state and returns updates.
"""

from __future__ import annotations
import re
import time
from typing import Any

from langgraph.types import interrupt, Command

from src.logging_config import get_logger
from src.config import config

# Module logger
logger = get_logger("nodes")

from src.game_state import (
    GameState,
    RollState,
    SessionState,
    DirectorStateModel,
    QuestLoreState,
    CompanionManagerState,
    ThemeTrackerState,
)
from src.rules_engine import action_roll, RollResult
from src.datasworn import load_starforged_data


# Load game data at module level
_datasworn = None


def get_datasworn():
    """Lazy load datasworn data."""
    global _datasworn
    if _datasworn is None:
        _datasworn = load_starforged_data()
    return _datasworn


# ============================================================================
# Router Node
# ============================================================================

MOVE_KEYWORDS = {
    "face danger": ["face danger", "overcome", "act under pressure", "react to"],
    "gather information": ["investigate", "gather info", "search", "scan", "analyze"],
    "secure an advantage": ["prepare", "secure", "position", "ready"],
    "compel": ["convince", "persuade", "threaten", "compel"],
    "aid your ally": ["help", "aid", "assist"],
    "enter the fray": ["attack", "fight", "enter combat", "draw weapon"],
    "undertake an expedition": ["travel", "journey", "expedition", "set course"],
    "make a connection": ["meet", "connect", "introduce", "befriend"],
}

ORACLE_KEYWORDS = ["oracle", "roll on", "generate", "random", "what is", "who is"]


def router_node(state: GameState) -> dict[str, Any]:
    """
    Examine player input and route to the appropriate handler.

    Returns route: "move", "oracle", "narrative", "approval", "end_turn", "command"
    """
    messages = state.get("messages", [])
    if not messages:
        return {"route": "narrative"}

    last_message = messages[-1]
    content = last_message.get("content", "").lower() if isinstance(last_message, dict) else str(last_message).lower()

    # Check if awaiting approval
    session = state.get("session", SessionState())
    if session.awaiting_approval:
        return {"route": "approval"}

    # Check for special commands (start with !)
    if content.startswith("!"):
        command = content.split()[0]
        if command in ["!end_session", "!endsession"]:
            return {"route": "command", "command_type": "end_session"}
        elif command in ["!status", "!debug"]:
            return {"route": "command", "command_type": "status"}
        elif command in ["!vows"]:
            return {"route": "command", "command_type": "vows"}
        elif command in ["!npcs", "!characters"]:
            return {"route": "command", "command_type": "npcs"}
        elif command in ["!help"]:
            return {"route": "command", "command_type": "help"}

    # Check for oracle request
    for keyword in ORACLE_KEYWORDS:
        if keyword in content:
            return {"route": "oracle"}

    # Check for move triggers
    for move_name, keywords in MOVE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in content:
                return {"route": "move", "detected_move": move_name}

    # Check for end turn signals
    if any(word in content for word in ["end turn", "rest", "wait", "pass"]):
        return {"route": "end_turn"}

    # Track player intent for prediction
    predicted_context = "general"
    try:
        from src.intent_predictor import NGramPredictor, quick_intent_detection, get_recommended_context
        
        # Get or create intent predictor from state
        intent_state = state.get("intent_predictor", {})
        predictor = NGramPredictor.from_dict(intent_state) if intent_state else NGramPredictor()
        
        # Detect and record intent
        detected_intent = quick_intent_detection(content)
        predictor.record_action(content, detected_intent)
        
        # Get predictions for context preloading
        predictions = predictor.predict_next(2)
        recommended = get_recommended_context(predictions)
        predicted_context = recommended[0] if recommended else "general"
        
        # Return updated predictor state
        return {
            "route": "narrative",
            "intent_predictor": predictor.to_dict(),
            "predicted_context": predicted_context,
            "detected_intent": detected_intent,
        }
    except Exception as e:
        logger.debug(f"Intent prediction fallback: {e}")

    # Default to narrative interpretation
    return {"route": "narrative"}


# ============================================================================
# Rules Engine Node
# ============================================================================

def rules_engine_node(state: GameState) -> dict[str, Any]:
    """
    Handle move resolution with dice rolling.
    """
    messages = state.get("messages", [])
    character = state.get("character")
    detected_move = state.get("detected_move", "face danger")

    # Get the move from datasworn
    datasworn = get_datasworn()
    move = datasworn.get_move(detected_move)

    if not move:
        return {
            "last_roll": RollState(
                roll_type="action",
                result_text=f"Move '{detected_move}' not found. Proceeding with narrative.",
                outcome="",
            ),
            "route": "narrator",
        }

    # Determine which stat to use (simplified - could be smarter)
    stat_map = {
        "face danger": "wits",
        "gather information": "wits",
        "secure an advantage": "edge",
        "compel": "heart",
        "enter the fray": "iron",
        "undertake an expedition": "wits",
        "make a connection": "heart",
    }

    stat_name = stat_map.get(detected_move, "wits")
    stat_value = getattr(character.stats, stat_name, 2) if character else 2

    # Perform the roll
    result = action_roll(stat_value, adds=0)

    # Get outcome text from move
    if result.result == RollResult.STRONG_HIT:
        outcome_text = move.strong_hit
        outcome = "strong_hit"
    elif result.result == RollResult.WEAK_HIT:
        outcome_text = move.weak_hit
        outcome = "weak_hit"
    else:
        outcome_text = move.miss
        outcome = "miss"

    roll_text = (
        f"**{move.name}** ({stat_name.title()} +{stat_value})\n\n"
        f"{result}\n\n"
        f"**{result.result.value}**: {outcome_text}"
    )

    return {
        "last_roll": RollState(
            roll_type="action",
            result_text=roll_text,
            outcome=outcome,
            is_match=result.is_match,
        ),
        "route": "director",
    }


# ============================================================================
# Director Node - Enhanced with Vow and Consequence Integration
# ============================================================================

async def director_node(state: GameState) -> dict[str, Any]:
    """
    Analyze dramatic state and set pacing/tone for the narrator.
    Now integrates:
    - Vow phase for automatic pacing escalation
    - Consequence engine delayed beats
    - Full state persistence
    """
    from src.director import DirectorAgent, DirectorState, Pacing, Tone
    from src.knowledge_graph import VowTracker, VowManager, ConsequenceEngine, DelayedBeat
    from src.game_state import VowManagerState, ConsequenceEngineState, PhotoAlbumState
    from src.photo_album import PhotoAlbumManager
    from src.image_gen import generate_location_image

    
    last_roll = state.get("last_roll", RollState())
    character = state.get("character")
    world = state.get("world")
    director_state_model = state.get("director", DirectorStateModel())
    vow_state = state.get("vows", VowManagerState())
    consequence_state = state.get("consequences", ConsequenceEngineState())
    quest_lore_state = state.get("quest_lore", QuestLoreState())
    companion_state = state.get("companions", CompanionManagerState())
    
    # Reconstruct DirectorState from stored model
    director_state = DirectorState(
        current_act=director_state_model.current_act if hasattr(director_state_model, 'current_act') else "act_1_setup",
        recent_pacing=director_state_model.recent_pacing if hasattr(director_state_model, 'recent_pacing') else [],
        active_beats=director_state_model.active_beats if hasattr(director_state_model, 'active_beats') else [],
        tension_level=director_state_model.tension_level if hasattr(director_state_model, 'tension_level') else 0.2,
        scenes_since_breather=director_state_model.scenes_since_breather if hasattr(director_state_model, 'scenes_since_breather') else 0,
        foreshadowing=director_state_model.foreshadowing if hasattr(director_state_model, 'foreshadowing') else [],
        moral_patterns=director_state_model.moral_patterns if hasattr(director_state_model, 'moral_patterns') else [],
    )
    
    # Create Director with restored state
    director = DirectorAgent(state=director_state)
    
    # Reconstruct VowManager from state
    vow_manager = VowManager()
    if hasattr(vow_state, 'vows') and vow_state.vows:
        for vid, vdata in vow_state.vows.items():
            vow_manager.vows[vid] = VowTracker.from_dict(vdata)
    vow_manager._vow_counter = vow_state.vow_counter if hasattr(vow_state, 'vow_counter') else 0
    
    # Get vow-based pacing guidance
    primary_vow = vow_manager.get_primary_vow()
    vow_guidance = vow_manager.get_combined_director_guidance() if primary_vow else {}
    
    # Check for due delayed beats from consequence engine
    delayed_beats = consequence_state.delayed_beats if hasattr(consequence_state, 'delayed_beats') else []
    due_beats = []
    remaining_beats = []
    for beat_data in delayed_beats:
        if beat_data.get("trigger_after_scenes", 1) <= 0:
            due_beats.append(beat_data.get("beat", ""))
        else:
            # Decrement timer
            beat_data["trigger_after_scenes"] -= 1
            remaining_beats.append(beat_data)
    
    # Add due beats to Director's active beats
    if due_beats:
        for beat in due_beats[:2]:  # Max 2 due beats per scene
            director.state.add_beat(beat)
    
    # Story DAG - track narrative position and act progression
    story_context = ""
    story_state = state.get("story_graph", {})
    try:
        from src.story_graph import StoryDAG, ActNumber
        
        dag = StoryDAG.from_dict(story_state) if story_state else None
        
        if dag:
            # Get current narrative context
            story_context = dag.get_narrative_context()
            
            # Sync act between DAG and Director
            dag_act = dag.get_current_act()
            if dag_act == ActNumber.ACT_1:
                director.state.current_act = "act_1_setup"
            elif dag_act == ActNumber.ACT_2:
                director.state.current_act = "act_2_escalation"
            elif dag_act == ActNumber.ACT_3:
                director.state.current_act = "act_3_climax"
            
            # Get available transitions for Director awareness
            transitions = dag.get_available_transitions()
            if transitions:
                director.state.add_beat(f"Story paths: {', '.join([e.label or 'continue' for e in transitions[:3]])}")
    except Exception as e:
        logger.debug(f"Story DAG processing fallback: {e}")
    
    # Build session summary from recent messages
    messages = state.get("messages", [])
    session_summary = ""
    for msg in messages[-5:]:
        if isinstance(msg, dict):
            role = msg.get("role", "")
            content = msg.get("content", "")[:200]  # Truncate
            session_summary += f"{role}: {content}...\n"
    
    # Calculate vow progress (use primary vow)
    vow_progress = primary_vow.progress_percent if primary_vow else 0.0
    
    # Build world state with vow context
    world_state = {
        "character": character.name if character else "Unknown",
        "location": world.current_location if world else "the void",
        "vows": [v.model_dump() for v in character.vows] if character and hasattr(character, 'vows') else [],
        "primary_vow_phase": primary_vow.phase if primary_vow else "establishing",
    }
    
    # Analyze and get plan
    plan = director.analyze(
        world_state=world_state,
        session_history=session_summary,
        last_roll_outcome=last_roll.outcome if last_roll else "",
        vow_progress=vow_progress,
    )
    
    # Override with vow-based guidance for high-progress vows
    if primary_vow and primary_vow.progress_percent > 0.6:
        # Near vow completion - escalate tension
        if vow_guidance.get("pacing"):
            plan.pacing = Pacing(vow_guidance["pacing"])
        if vow_guidance.get("tone"):
            plan.tone = Tone(vow_guidance["tone"])
        if vow_guidance.get("notes"):
            plan.notes_for_narrator += f" {vow_guidance['notes']}"
    
    # Update stored director state
    current_act_val = director.state.current_act
    if hasattr(current_act_val, 'value'):
        current_act_val = current_act_val.value
        
    updated_director = DirectorStateModel(
        current_act=current_act_val,
        recent_pacing=director.state.recent_pacing,
        active_beats=director.state.active_beats,
        tension_level=director.state.tension_level,
        scenes_since_breather=director.state.scenes_since_breather,
        foreshadowing=director.state.foreshadowing,
        moral_patterns=director.state.moral_patterns,
        last_pacing=plan.pacing.value,
        last_tone=plan.tone.value,
        last_notes=plan.notes_for_narrator,
    )
    
    # Update consequence engine state with decremented timers
    updated_consequences = ConsequenceEngineState(
        delayed_beats=remaining_beats,
        moral_patterns=consequence_state.moral_patterns if hasattr(consequence_state, 'moral_patterns') else [],
        scene_count=(consequence_state.scene_count if hasattr(consequence_state, 'scene_count') else 0) + 1,
    )
    
    # TLOU-Style: Check for quiet moment needs
    quiet_moment_context = ""
    emotional_state = state.get("emotional_storytelling", {})
    try:
        from src.emotional_storytelling import BondManager
        
        bond_manager = BondManager.from_dict(emotional_state) if emotional_state else BondManager()
        
        # Check if we need a quiet moment
        if bond_manager.quiet_tracker.needs_quiet_moment():
            quiet_moment = bond_manager.quiet_tracker.get_quiet_moment(session_summary)
            quiet_moment_context = (
                f"[QUIET MOMENT NEEDED]\n"
                f"Type: {quiet_moment['type']}\n"
                f"Prompt: {quiet_moment['prompt']}\n"
                f"Instruction: {quiet_moment['narrator_instruction']}"
            )
            plan.pacing = Pacing.BREATHER
            plan.notes_for_narrator += f" ** MANDATE QUIET SCENE: {quiet_moment['prompt']} **"
    except Exception as e:
        logger.debug(f"Quiet moment check fallback: {e}")

    # TLOU-Style: Check for moral dilemma opportunity
    dilemma_context = ""
    theme_state = state.get("theme_tracker", {})
    try:
        from src.moral_dilemma import ThemeTracker, DilemmaGenerator, CampaignTheme
        
        theme = ThemeTracker.from_dict(theme_state) if theme_state else None
        
        if theme:
            generator = DilemmaGenerator(theme=theme.primary_theme)
            scenes_since = consequence_state.scene_count if hasattr(consequence_state, 'scene_count') else 10
            
            if generator.should_present_dilemma(scenes_since, director.state.tension_level):
                dilemma = generator.generate()
                dilemma_context = dilemma.get_narrator_context()
                plan.notes_for_narrator += " ** PRESENT MORAL DILEMMA TO PLAYER **"
    except Exception as e:
        logger.debug(f"Moral dilemma check fallback: {e}")

    # Quest & Lore Integration
    quest_lore_engine = None
    try:
        from src.quest_lore import QuestLoreEngine
        quest_lore_engine = QuestLoreEngine.from_dict(quest_lore_state.model_dump())
        # Automatically advance scene count for time tracking
        quest_lore_engine.quests.current_scene = consequence_state.scene_count
        
        # Check for urgent quests
        urgent = quest_lore_engine.quests.get_urgent_quests(current_day=1) # Simplified day tracking
        if urgent:
            plan.notes_for_narrator += " ** REMINDER: TIME SENSITIVE OBJECTIVE **"
    except Exception as e:
        logger.debug(f"Quest/lore integration fallback: {e}")

    # Combat Prediction Integration
    combat_warning = ""
    if getattr(world, 'combat_active', False):
        try:
            from src.combat_prediction import quick_combat_check
            # Simple heuristic since we don't have full combat state yet
            warning = quick_combat_check(
                player_strength=1.0, player_count=1,
                enemy_strength=1.0, enemy_count=3, # Placeholder
                is_ranged=True
            )
            combat_warning = warning.get("narrative", "")
            if warning.get("warning") in ["SUICIDE", "EXTREME"]:
                plan.notes_for_narrator += f" ** WARNING: {combat_warning} **"
        except Exception as e:
            logger.debug(f"Combat prediction fallback: {e}")

    # Cinematic Scene Trigger Logic
    # -----------------------------
    album_state = state.get("album", PhotoAlbumState())
    album_manager = PhotoAlbumManager(album_state)
    
    # 1. Tension Peak Trigger
    # Trigger if tension is high (>0.8) and we haven't just taken a photo of this scene (heuristic)
    # Using a simple check on the last photo's timestamp or ID vs current turn count could work better,
    # but for now we'll rely on the director's state change or a random chance at peak tension.
    if director.state.tension_level >= 0.8 and plan.pacing == Pacing.CLIMAX:
        # Check if we already have a recent photo for this "climax"
        latest_photo = album_manager.get_latest_photo()
        should_snap = True
        if latest_photo and "Climax" in latest_photo.tags:
             # Avoid spamming photos during prolonged climax
            should_snap = False 
            
        if should_snap:
             try:
                scene_desc = f"Dramatic climax in {world.current_location}. {plan.notes_for_narrator}"
                filename = f"cinematic_{hash(scene_desc)}_{int(time.time())}.png"
                img_url = await generate_location_image(scene_desc, filename)
                if img_url:
                    album_manager.capture_moment(
                        image_url=img_url,
                        caption=f"High tension at {world.current_location}",
                        tags=["Climax", "High Tension"],
                        scene_id=world.current_location
                    )
             except Exception as e:
                logger.warning(f"Photo album auto-capture failed: {e}")

    return {
        "director": updated_director,

        "consequences": updated_consequences,
        "quiet_moment": quiet_moment_context if quiet_moment_context else None,
        "dilemma": dilemma_context if dilemma_context else None,
        "quest_lore": QuestLoreState(**quest_lore_engine.to_dict()) if quest_lore_engine else quest_lore_state,
        "route": "narrator",
        "combat_warning": combat_warning,
    }


# ============================================================================
# Oracle Interpreter Node
# ============================================================================

def oracle_interpreter_node(state: GameState) -> dict[str, Any]:
    """
    Handle oracle rolls and return results.
    """
    messages = state.get("messages", [])
    content = ""
    if messages:
        last_msg = messages[-1]
        content = last_msg.get("content", "") if isinstance(last_msg, dict) else str(last_msg)

    datasworn = get_datasworn()

    # Try to find the oracle they want
    # Common oracle keywords to look for
    oracle_mappings = {
        "name": "character/name",
        "planet": "planets/class",
        "settlement": "settlements/name",
        "npc": "characters/name",
        "action": "core/action",
        "theme": "core/theme",
        "descriptor": "core/descriptor",
        "focus": "core/focus",
    }

    oracle_path = None
    for keyword, path in oracle_mappings.items():
        if keyword in content.lower():
            # Search for matching oracle
            results = datasworn.search_oracles(path)
            if results:
                oracle_path = f"{results[0].name}"
                result = datasworn.roll_oracle(list(datasworn._oracles.keys())[0])
                break

    if not oracle_path:
        # Default to action + theme
        oracles = datasworn.search_oracles("action")
        if oracles:
            key = [k for k in datasworn._oracles.keys() if "action" in k][0]
            action = datasworn.roll_oracle(key)
            theme_key = [k for k in datasworn._oracles.keys() if "theme" in k]
            theme = datasworn.roll_oracle(theme_key[0]) if theme_key else "unknown"
            oracle_path = "Action + Theme"
            result = f"{action} / {theme}"
        else:
            oracle_path = "Unknown"
            result = "The oracle is silent."

    roll_text = f"**Oracle: {oracle_path}**\n\nResult: **{result}**"

    return {
        "last_roll": RollState(
            roll_type="oracle",
            result_text=roll_text,
            outcome="",
            is_match=False,
        ),
        "route": "narrator",
    }


# ============================================================================
# Narrator Node - Enhanced with Memory, Voice, and Dynamic Few-Shot
# ============================================================================

def narrator_node(state: GameState) -> dict[str, Any]:
    """
    Generate narrative prose with full system integration:
    - Director guidance for pacing and tone
    - Memory context for continuity
    - Voice profiles for NPC consistency
    - Dynamic few-shot examples matching current tone
    """
    from src.narrator import (
        build_narrative_prompt, NarratorConfig, SYSTEM_PROMPT,
        get_examples_for_tone, validate_narrative,
    )
    from src.director import DirectorPlan, Pacing, Tone
    from src.memory import MemoryManager, ActiveContext, SessionBuffer, CampaignSummary
    from src.character_voice import VoiceManager, CharacterProfile
    from src.game_state import MemoryStateModel, VoiceManagerState

    last_roll = state.get("last_roll", RollState())
    character = state.get("character")
    world = state.get("world")
    messages = state.get("messages", [])
    director_state = state.get("director", DirectorStateModel())
    memory_state = state.get("memory", MemoryStateModel())
    voice_state = state.get("voices", VoiceManagerState())
    quest_lore_state = state.get("quest_lore", QuestLoreState())
    companion_state = state.get("companions", CompanionManagerState())

    # Get last player input
    player_input = ""
    if messages:
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                player_input = msg.get("content", "")
                break

    # Reconstruct DirectorPlan from state
    pacing = director_state.last_pacing if hasattr(director_state, 'last_pacing') else "standard"
    tone = director_state.last_tone if hasattr(director_state, 'last_tone') else "mysterious"
    
    director_plan = DirectorPlan(
        pacing=Pacing(pacing),
        tone=Tone(tone),
        beats=director_state.active_beats if hasattr(director_state, 'active_beats') else [],
        notes_for_narrator=director_state.last_notes if hasattr(director_state, 'last_notes') else "",
    )
    
    # Build Memory context
    memory_context = ""
    if memory_state:
        context_parts = []
        
        # Recent scene summaries
        if hasattr(memory_state, 'scene_summaries') and memory_state.scene_summaries:
            recent = memory_state.scene_summaries[-3:]
            context_parts.append("[Recent Events]\n" + "\n".join(f"- {s}" for s in recent))
        
        # Key relationships from campaign
        if hasattr(memory_state, 'key_relationships') and memory_state.key_relationships:
            rels = [f"{npc}: {rel}" for npc, rel in list(memory_state.key_relationships.items())[:5]]
            context_parts.append("[Key Relationships]\n" + "\n".join(f"- {r}" for r in rels))
        
        # Major story beats
        if hasattr(memory_state, 'major_beats') and memory_state.major_beats:
            context_parts.append("[Campaign History]\n" + "\n".join(f"- {b}" for b in memory_state.major_beats[-3:]))
        
        if context_parts:
            memory_context = "\n\n".join(context_parts)

    # Build Voice context for active NPCs
    voice_context = ""
    if voice_state and hasattr(voice_state, 'active_characters') and voice_state.active_characters:
        voice_parts = []
        for char_name in voice_state.active_characters:
            profile = voice_state.profiles.get(char_name.lower(), {})
            if profile:
                lines = [f"[CHARACTER VOICE: {profile.get('name', char_name)}]"]
                if profile.get('speech_patterns'):
                    lines.append(f"Speech: {'; '.join(profile['speech_patterns'][:2])}")
                if profile.get('relationship_to_player'):
                    lines.append(f"Relationship: {profile['relationship_to_player']}")
                voice_parts.append("\n".join(lines))
        if voice_parts:
            voice_context = "\n\n".join(voice_parts)

    # Evaluate Behavior Trees for active NPCs
    npc_behavior_context = ""
    if memory_state and hasattr(memory_state, 'active_npcs') and memory_state.active_npcs:
        from src.behavior_tree import evaluate_npc_behavior
        
        bt_parts = []
        for npc_name in memory_state.active_npcs[:3]:  # Limit to 3 NPCs
            # Get archetype from voice profiles or default
            archetype = "civilian"
            if voice_state and hasattr(voice_state, 'profiles'):
                profile = voice_state.profiles.get(npc_name.lower(), {})
                archetype = profile.get("archetype", "civilian")
            
            # Evaluate BT
            bt_context = evaluate_npc_behavior(
                npc_name=npc_name,
                archetype=archetype,
                player_name=character.name if character else "Traveler",
                player_reputation=0.5,  # Could be pulled from memory
                in_combat=False,  # Could be pulled from world state
                has_quest=False,  # Could be pulled from NPC data
            )
            
            if bt_context.action and bt_context.dialogue_intent:
                bt_parts.append(
                    f"[NPC BEHAVIOR: {npc_name}]\n"
                    f"Action: {bt_context.action}\n"
                    f"Manner: {bt_context.dialogue_intent}"
                )
        
        if bt_parts:
            npc_behavior_context = "\n\n".join(bt_parts)

    # Get tone-matched few-shot examples
    examples = get_examples_for_tone(tone, pacing, count=2)
    few_shot_context = ""
    if examples:
        few_shot_parts = []
        for ex in examples:
            few_shot_parts.append(
                f"[Example - {ex.get('roll', 'Narrative')}]\n{ex.get('narrative', '')[:400]}"
            )
        few_shot_context = "\n\n".join(few_shot_parts)
    
    # Build enhanced prompt with Director guidance
    prompt = build_narrative_prompt(
        player_input=player_input,
        roll_result=last_roll.result_text if last_roll else "",
        outcome=last_roll.outcome if last_roll else "",
        character_name=character.name if character else "Traveler",
        location=world.current_location if world else "the void",
    )
    
    # Compose enhanced system prompt with all injections
    enhanced_system = SYSTEM_PROMPT
    enhanced_system += director_plan.to_prompt_injection()
    
    # FEEDBACK LEARNING: Auto-inject learned preferences
    try:
        from src.feedback_learning import FeedbackLearningEngine, PromptModifier, ExampleRetriever
        
        feedback_engine = FeedbackLearningEngine(db_path=config.paths.feedback_db)
        
        # Check if we have enough data for analysis
        stats = feedback_engine.db.get_statistics()
        
        if stats["total_paragraphs"] >= 20:
            # Run analysis if we haven't recently or if we have 10+ new decisions
            current_profile = feedback_engine.current_profile
            should_analyze = (
                current_profile is None or 
                stats["total_paragraphs"] - current_profile.total_decisions_analyzed >= 10
            )
            
            if should_analyze:
                # Analyze and save new preferences
                new_profile = feedback_engine.run_preference_analysis()
                feedback_engine.current_profile = new_profile
            
            # Inject learned preferences into prompt
            if feedback_engine.current_profile:
                modifier = PromptModifier(feedback_engine.current_profile)
                preference_injection = modifier.generate_modifications()
                if preference_injection:
                    enhanced_system += f"\n\n{preference_injection}"
            
            # Add few-shot examples from similar accepted paragraphs
            retriever = ExampleRetriever(feedback_engine.db)
            context = {
                "pacing": pacing,
                "tone": tone,
                "scene_type": "general",
            }
            few_shot_prompt = retriever.build_few_shot_prompt(context, n_positive=2, n_negative=1)
            if few_shot_prompt:
                enhanced_system += f"\n\n{few_shot_prompt}"
    
    except Exception as e:
        # Graceful fallback if feedback learning fails
        logger.warning(f"Feedback learning injection failed: {e}")
    
    # Narrative Craft Engine - genre, McKee structure, archetypes
    craft_state = state.get("narrative_craft", {})
    try:
        from src.narrative_craft import NarrativeCraftEngine, Genre
        
        craft_engine = NarrativeCraftEngine.from_dict(craft_state) if craft_state else NarrativeCraftEngine()
        craft_context = craft_engine.get_craft_context()
        
        if craft_context:
            enhanced_system += f"\n\n<narrative_craft>\n{craft_context}\n</narrative_craft>"
        
        craft_engine.scenes_in_current_beat += 1
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Prose Craft System - sentence rhythm, sensory detail, dialogue craft
    try:
        from src.prose_craft import ProseCraftEngine
        
        # Get tension and emotional context for prose guidance
        director_model = state.get("director", DirectorStateModel())
        prose_tension = getattr(director_model, 'tension_level', 0.5)
        emotional_state = getattr(director_model, 'tone', 'neutral')
        
        # Get POV character info
        pov_character = character.name if character else "the protagonist"
        
        prose_engine = ProseCraftEngine()
        prose_guidance = prose_engine.generate_comprehensive_guidance(
            tension_level=prose_tension,
            emotional_state=emotional_state,
            pov_character=pov_character,
            scene_type=getattr(director_model, 'beat_type', 'general'),
            location_type=world.current_location if world else "generic"
        )
        
        if prose_guidance:
            enhanced_system += prose_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Prose Enhancement - sensory tracking, voice consistency, metaphors
    prose_enhancement_state = state.get("prose_enhancement", {})
    try:
        from src.prose_enhancement import ProseEnhancementEngine
        
        prose_enhancer = ProseEnhancementEngine.from_dict(prose_enhancement_state) if prose_enhancement_state else ProseEnhancementEngine()
        
        # Determine active NPCs
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []
        
        # Get genre from narrative craft if available
        genre = "space_opera"
        if craft_state and "genre" in craft_state:
            genre = craft_state["genre"]
        
        # Generate enhancement guidance
        enhancement_context = prose_enhancer.get_comprehensive_guidance(
            location=world.current_location if world else "",
            active_npcs=active_npcs[:3],
            genre=genre,
            subjects=["danger", "technology", "emotion"]
        )
        
        if enhancement_context:
            enhanced_system += enhancement_context
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Narrative Systems - tension arc, dialogue, transitions, themes
    narrative_systems_state = state.get("narrative_systems", {})
    try:
        from src.narrative_systems import NarrativeSystemsEngine
        
        narrative_systems = NarrativeSystemsEngine.from_dict(narrative_systems_state) if narrative_systems_state else NarrativeSystemsEngine()
        
        # Get tension from director
        director_model = state.get("director", DirectorStateModel())
        ns_tension = getattr(director_model, 'tension_level', 0.5)
        
        # Determine scene position based on session state
        session = state.get("session", SessionState())
        turn_count = getattr(session, 'turn_count', 0) if hasattr(session, 'turn_count') else 0
        scene_position = "middle"  # Default
        
        # Is this a climactic moment?
        is_climactic = ns_tension >= 0.8
        
        # Generate narrative systems guidance
        ns_guidance = narrative_systems.get_comprehensive_guidance(
            tension_level=ns_tension,
            scene_position=scene_position,
            is_climactic=is_climactic,
            include_themes=True
        )
        
        if ns_guidance:
            enhanced_system += ns_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Character Arcs - Hero's Journey, foreshadowing, pacing, emotional beats
    character_arcs_state = state.get("character_arcs", {})
    try:
        from src.character_arcs import CharacterArcEngine
        
        arc_engine = CharacterArcEngine.from_dict(character_arcs_state) if character_arcs_state else CharacterArcEngine()
        
        # Get protagonist name from character state
        protagonist_name = character.name if character else ""
        
        # Generate character arc guidance
        arc_guidance = arc_engine.get_comprehensive_guidance(
            protagonist_name=protagonist_name,
            detected_emotion=None,  # Could enhance with emotion detection
            current_scene_type=None  # Could enhance with scene type detection
        )
        
        if arc_guidance:
            enhanced_system += arc_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # World Coherence - state tracking, agency validation, surprises, recaps
    world_coherence_state = state.get("world_coherence", {})
    try:
        from src.world_coherence import WorldCoherenceEngine
        
        coherence_engine = WorldCoherenceEngine.from_dict(world_coherence_state) if world_coherence_state else WorldCoherenceEngine()
        
        # Determine active NPCs
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []
        
        # Generate world coherence guidance
        coherence_guidance = coherence_engine.get_comprehensive_guidance(
            location=world.current_location if world else "",
            active_npcs=active_npcs[:3],
            is_session_start=False,  # Could enhance with session detection
            protagonist=character.name if character else ""
        )
        
        if coherence_guidance:
            enhanced_system += coherence_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Specialized Scenes - combat, investigation, social, exploration, horror
    specialized_scenes_state = state.get("specialized_scenes", {})
    try:
        from src.specialized_scenes import SpecializedScenesEngine
        
        scenes_engine = SpecializedScenesEngine.from_dict(specialized_scenes_state) if specialized_scenes_state else SpecializedScenesEngine()
        
        # Detect scene type from context
        scene_type = "general"
        if getattr(world, 'combat_active', False) if world else False:
            scene_type = "combat"
        
        # Get scene-specific guidance
        scene_guidance = scenes_engine.get_scene_guidance(scene_type)
        
        if scene_guidance:
            enhanced_system += f"\n\n{scene_guidance}"
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Advanced Simulation - relationships, flashbacks, consequences, time, dialogue
    advanced_sim_state = state.get("advanced_simulation", {})
    try:
        from src.advanced_simulation import AdvancedSimulationEngine
        
        sim_engine = AdvancedSimulationEngine.from_dict(advanced_sim_state) if advanced_sim_state else AdvancedSimulationEngine()
        
        # Get active NPCs
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []
        
        # Build context for flashback triggers
        current_context = {
            "location": world.current_location if world else ""
        }
        
        # Generate simulation guidance
        sim_guidance = sim_engine.get_comprehensive_guidance(
            active_npcs=active_npcs[:3],
            player_name=character.name if character else "player",
            current_context=current_context
        )
        
        if sim_guidance:
            enhanced_system += sim_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")


    
    # Quest and Lore - objectives, worldbuilding, NPC schedules, rumors
    try:
        from src.quest_lore import QuestLoreEngine
        
        # Use model_dump() if it's a Pydantic model (which it should be now)
        ql_data = quest_lore_state.model_dump() if hasattr(quest_lore_state, 'model_dump') else quest_lore_state
        ql_engine = QuestLoreEngine.from_dict(ql_data) if ql_data else QuestLoreEngine()
        
        # Get active NPCs
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []
        
        # Generate quest/lore guidance
        ql_guidance = ql_engine.get_comprehensive_guidance(
            current_location=world.current_location if world else "",
            active_npcs=active_npcs[:3],
            current_day=1  # Could enhance with time tracking
        )
        
        if ql_guidance:
            enhanced_system += ql_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Faction and Environment - politics, weather, economy, companions
    faction_env_state = state.get("faction_environment", {})
    try:
        from src.faction_environment import FactionEnvironmentEngine
        
        fe_engine = FactionEnvironmentEngine.from_dict(faction_env_state) if faction_env_state else FactionEnvironmentEngine()
        
        # Get active NPCs
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []
        
        # Generate faction/environment guidance
        fe_guidance = fe_engine.get_comprehensive_guidance(
            location=world.current_location if world else "",
            active_npcs=active_npcs[:3]
        )
        
        if fe_guidance:
            enhanced_system += fe_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Final Systems - encounters, voice consistency, memory consolidation
    final_systems_state = state.get("final_systems", {})
    try:
        from src.final_systems import FinalSystemsEngine
        
        final_engine = FinalSystemsEngine.from_dict(final_systems_state) if final_systems_state else FinalSystemsEngine()
        
        # Get current tension from director if available
        tension = 0.5
        director_state = state.get("director", {})
        if director_state and "tension" in director_state:
            tension = director_state.get("tension", 0.5)
        
        final_guidance = final_engine.get_comprehensive_guidance(current_tension=tension)
        
        if final_guidance:
            enhanced_system += final_guidance
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    
    # Campaign Truths - inject world settings
    campaign_truths_state = state.get("campaign_truths", {})










    try:
        from src.campaign_truths import CampaignTruths, create_default_campaign
        
        truths = CampaignTruths.from_dict(campaign_truths_state) if campaign_truths_state else create_default_campaign()
        truths_context = truths.get_narrative_context()
        
        if truths_context:
            enhanced_system += f"\n\n<world_truths>\n{truths_context}\n</world_truths>"
        
        # Add forbidden elements to narrator constraints
        forbidden = truths.get_forbidden_elements()
        if forbidden:
            enhanced_system += f"\n\n<forbidden_by_setting>\nDo not include: {', '.join(forbidden)}\n</forbidden_by_setting>"
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # OCEAN Personality - Big Five traits for NPCs
    if memory_state and hasattr(memory_state, 'active_npcs') and memory_state.active_npcs:
        try:
            from src.personality import create_personality, OCEANProfile
            
            npc_personalities = state.get("npc_personalities", {})
            personality_context = ""
            
            for npc in memory_state.active_npcs[:3]:
                if npc in npc_personalities:
                    profile = OCEANProfile.from_dict(npc_personalities[npc])
                else:
                    # Generate random personality for new NPCs
                    profile = create_personality("everyman")
                    npc_personalities[npc] = profile.to_dict()
                
                personality_context += profile.get_narrator_context(npc) + "\n\n"
            
            if personality_context:
                enhanced_system += f"\n\n<npc_personalities>\n{personality_context.strip()}\n</npc_personalities>"
        except Exception as e:
            logger.debug(f"System fallback: {e}")
    
    # Cinematography - shot selection based on emotion/action
    try:
        from src.personality import CinematographyDirector
        
        # Estimate emotional intensity from director state
        director_model = state.get("director", DirectorStateModel())
        tension = director_model.tension_level if hasattr(director_model, 'tension_level') else 0.5
        
        # Determine if this is action or dialogue
        is_action = getattr(world, 'combat_active', False) if world else False
        is_dialogue = any(npc in player_input.lower() for npc in (memory_state.active_npcs if memory_state else []))
        
        cinematographer = CinematographyDirector()
        camera_context = cinematographer.get_narrator_context(
            emotional_intensity=tension,
            tactical_complexity=0.7 if is_action else 0.3,
            is_dialogue=is_dialogue,
            is_action=is_action,
        )
        enhanced_system += f"\n\n<cinematography>\n{camera_context}\n</cinematography>"
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Smart Zones - living scene context
    smart_zone_state = state.get("smart_zones", {})
    try:
        from src.smart_zones import SmartZoneManager
        
        zone_manager = SmartZoneManager.from_dict(smart_zone_state) if smart_zone_state else None
        if zone_manager:
            zone_context = zone_manager.get_current_zone_context()
            if zone_context:
                enhanced_system += f"\n\n<living_scene>\n{zone_context}\n</living_scene>"
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    # Combat Orchestrator - Belgian AI attack grid
    if getattr(world, 'combat_active', False) if world else False:
        combat_state = state.get("combat_orchestrator", {})
        try:
            from src.combat_orchestrator import CombatOrchestrator
            
            orchestrator = CombatOrchestrator.from_dict(combat_state) if combat_state else None
            if orchestrator:
                combat_context = orchestrator.get_combat_context()
                enhanced_system += f"\n\n<combat_orchestration>\n{combat_context}\n</combat_orchestration>"
        except Exception as e:
            logger.debug(f"System fallback: {e}")
    
    # Bark System - NPC vocalizations and evidence
    bark_context = ""
    bark_state = state.get("barks", {})
    try:
        from src.barks import BarkManager, detect_evidence, EvidenceType
        
        bark_manager = BarkManager.from_dict(bark_state) if bark_state else BarkManager()
        
        # Detect evidence from player action
        evidence_types = detect_evidence(player_input)
        for ev_type in evidence_types:
            bark_manager.add_evidence(
                ev_type,
                location=world.current_location if world else "unknown",
            )
        
        bark_context = bark_manager.get_narrator_context()
        bark_manager.update_cooldowns()
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if bark_context:
        enhanced_system += f"\n\n<npc_barks>\n{bark_context}\n</npc_barks>"
    
    # Daily Scripts - Time-based NPC activities
    daily_context = ""
    daily_state = state.get("daily_scripts", {})
    try:
        from src.daily_scripts import DailyScriptManager
        
        daily_manager = DailyScriptManager.from_dict(daily_state) if daily_state else None
        if daily_manager:
            daily_context = daily_manager.get_narrator_context()
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if daily_context:
        enhanced_system += f"\n\n<world_time>\n{daily_context}\n</world_time>"
    
    # Lorebook - Keyword-activated lore retrieval
    lore_context = ""
    lorebook_state = state.get("lorebook", {})
    try:
        from src.daily_scripts import Lorebook
        
        lorebook = Lorebook.from_dict(lorebook_state) if lorebook_state else None
        if lorebook:
            lore_context = lorebook.get_context_for_input(player_input)
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if lore_context:
        enhanced_system += f"\n\n<lorebook>\n{lore_context}\n</lorebook>"
    
    # Influence Maps - Tactical spatial analysis
    if getattr(world, 'combat_active', False) if world else False:
        tactical_context = ""
        influence_state = state.get("influence_maps", {})
        try:
            from src.influence_maps import InfluenceMap, Position
            
            imap = InfluenceMap.from_dict(influence_state) if influence_state else None
            if imap:
                # Assume player at origin for text-based game
                player_pos = Position(0, 0)
                tactical_context = imap.get_narrator_context(player_pos)
        except Exception as e:
            logger.debug(f"System fallback: {e}")
        
        if tactical_context:
            enhanced_system += f"\n\n<tactical_map>\n{tactical_context}\n</tactical_map>"
    
    if memory_context:
        enhanced_system += f"\n\n<memory_context>\n{memory_context}\n</memory_context>"
    
    if voice_context:
        enhanced_system += f"\n\n<character_voices>\n{voice_context}\n</character_voices>"
    
    if npc_behavior_context:
        enhanced_system += f"\n\n<npc_behaviors>\n{npc_behavior_context}\n</npc_behaviors>"
    
    # Social Memory - Witcher III-style vendettas and history
    social_context = ""
    social_state = state.get("social_memory", {})
    try:
        from src.social_memory import SocialGraph
        
        graph = SocialGraph()
        # Rebuild from state (simplified)
        stored_histories = social_state.get("histories", {})
        if stored_histories and memory_state and hasattr(memory_state, 'active_npcs'):
            for npc in memory_state.active_npcs[:3]:
                vendetta_context = graph.get_narrator_context(npc)
                if vendetta_context:
                    social_context += vendetta_context + "\n"
                
                history = graph.get_history(npc)
                history_context = history.get_narrative_context()
                if history_context:
                    social_context += history_context + "\n"
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if social_context:
        enhanced_system += f"\n\n<social_memory>\n{social_context.strip()}\n</social_memory>"
    
    
    # Combat Prediction - warn about unfair fights
    combat_warning_context = ""
    if world and hasattr(world, 'combat_active') and world.combat_active:
        try:
            from src.combat_prediction import quick_combat_check, get_combat_warning_context
            
            # Estimate player vs enemy strength
            player_count = 1  # Could be expanded for companion/party
            player_strength = 1.0
            enemy_count = getattr(world, 'enemy_count', 1)
            enemy_strength = getattr(world, 'enemy_strength', 1.0)
            
            prediction = quick_combat_check(
                player_strength, player_count,
                enemy_strength, enemy_count,
                is_ranged=True
            )
            combat_warning_context = get_combat_warning_context(prediction)
        except Exception as e:
            logger.debug(f"Combat warning fallback: {e}")
    
    if combat_warning_context:
        enhanced_system += f"\n\n<combat_assessment>\n{combat_warning_context}\n</combat_assessment>"
    
    # Companion AI - buddy intervention context
    companion_context = ""
    if companion_state.active_companion and companion_state.companions:
        try:
            from src.companion import CompanionAI, CompanionContext, create_companion
            
            comp_data = companion_state.companions.get(companion_state.active_companion)
            if not comp_data:
                raise ValueError("Active companion data not found")

            companion = create_companion(
                comp_data.get("archetype", "soldier"),
                comp_data.get("name", "Companion")
            )
            
            ctx = CompanionContext(
                player_health=character.health if hasattr(character, 'health') else 1.0,
                player_in_combat=getattr(world, 'combat_active', False) if world else False,
                threat_level=getattr(world, 'threat_level', 0.0) if world else 0.0,
                current_scene=session.scene_number if hasattr(session, 'scene_number') else 0,
            )
            
            # Check for intervention
            intervention = companion.update(ctx)
            if intervention:
                companion_context = (
                    f"[COMPANION: {intervention['companion_name']}]\n"
                    f"Action: {intervention['action']}\n"
                    f"Intent: {intervention['dialogue_intent']}\n"
                    f"Style: {intervention['speech_style']}"
                )
                if intervention.get('signature_phrase'):
                    companion_context += f"\nPhrase: \"{intervention['signature_phrase']}\""
            else:
                companion_context = companion.get_narrator_context(ctx)
        except Exception as e:
            logger.debug(f"System fallback: {e}")
    
    if companion_context:
        enhanced_system += f"\n\n<companion>\n{companion_context}\n</companion>"
    
    # GOAP - complex NPC planning for key NPCs
    goap_context = ""
    if memory_state and hasattr(memory_state, 'active_npcs') and memory_state.active_npcs:
        try:
            from src.goap import plan_npc_action, get_plan_narrative
            
            # Only plan for first significant NPC
            npc_name = memory_state.active_npcs[0]
            
            # Build current world state for GOAP
            goap_state = {
                "has_weapon": True,
                "weapon_drawn": getattr(world, 'combat_active', False) if world else False,
                "target_visible": True,
                "target_in_range": False,
            }
            
            # Target goal based on situation
            if getattr(world, 'combat_active', False) if world else False:
                plan = plan_npc_action(
                    "attack_player",
                    {"target_damaged": True},
                    goap_state,
                    "combat"
                )
                if plan:
                    goap_context = f"[{npc_name} PLAN]\n"
                    goap_context += "\n".join([f"- {a['description']}" for a in plan])
        except Exception as e:
            logger.debug(f"System fallback: {e}")
    
    if goap_context:
        enhanced_system += f"\n\n<npc_plans>\n{goap_context}\n</npc_plans>"
    
    # TLOU-Style: Bond relationships context
    bond_context = ""
    emotional_state = state.get("emotional_storytelling", {})
    try:
        from src.emotional_storytelling import BondManager
        
        bond_manager = BondManager.from_dict(emotional_state) if emotional_state else BondManager()
        bond_context = bond_manager.get_all_bonds_context()
        
        # Check for callback opportunity at high-tension moments
        director_plan = state.get("director", DirectorStateModel())
        if hasattr(director_plan, 'tension_level') and director_plan.tension_level > 0.7:
            callback = bond_manager.get_callback_for_climax()
            if callback:
                bond_context += f"\n\n[CALLBACK OPPORTUNITY]\n{callback}"
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if bond_context:
        enhanced_system += f"\n\n<character_bonds>\n{bond_context}\n</character_bonds>"
    
    # TLOU-Style: Theme context
    theme_context = ""
    theme_state = state.get("theme_tracker", {})
    try:
        from src.moral_dilemma import ThemeTracker
        
        theme = ThemeTracker.from_dict(theme_state) if theme_state else None
        if theme:
            theme_context = theme.get_theme_context()
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if theme_context:
        enhanced_system += f"\n\n<campaign_theme>\n{theme_context}\n</campaign_theme>"
    
    # TLOU-Style: Environmental storytelling guidance
    env_story_context = ""
    try:
        from src.environmental_storytelling import EnvironmentalStoryGenerator
        
        generator = EnvironmentalStoryGenerator()
        env_story_context = generator.get_show_dont_tell_guidance()
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if env_story_context:
        enhanced_system += f"\n\n<environmental_storytelling>\n{env_story_context}\n</environmental_storytelling>"
    
    if few_shot_context:
        enhanced_system += f"\n\n<style_examples>\n{few_shot_context}\n</style_examples>"
    
    # ==========================================================================
    # ENHANCEMENT ENGINE INTEGRATION
    # All 13 enhancement systems unified here
    # ==========================================================================
    enhancement_context = ""
    enhancement_state = state.get("enhancements", {})
    try:
        from src.enhancement_engine import EnhancementEngine
        
        enhancement_engine = EnhancementEngine.from_dict(enhancement_state) if enhancement_state else EnhancementEngine()
        
        # Set current scene
        turn_count = state.get("session", SessionState()).turn_count if hasattr(state.get("session", SessionState()), 'turn_count') else 0
        enhancement_engine.set_scene(turn_count)
        
        # Get active NPCs
        active_npcs = memory_state.active_npcs if memory_state and hasattr(memory_state, 'active_npcs') else []
        
        # Build vow states for vow complication engine
        vow_states = []
        if character and hasattr(character, 'vows'):
            for vow in character.vows:
                vow_states.append(vow.model_dump() if hasattr(vow, 'model_dump') else vow.__dict__)
        
        # Build asset states for asset narrative engine
        asset_states = []
        if character and hasattr(character, 'assets'):
            for asset in character.assets:
                asset_states.append(asset.model_dump() if hasattr(asset, 'model_dump') else asset.__dict__)
        
        # Process turn through all enhancement systems
        ctx = enhancement_engine.process_turn(
            player_input=player_input,
            location=world.current_location if world else "",
            active_npcs=active_npcs,
            player_name=character.name if character else "the protagonist",
            vow_states=vow_states,
            asset_states=asset_states,
            is_session_start=(turn_count == 0),
        )
        
        # Get narrator injection from all systems
        enhancement_context = ctx.get_narrator_injection()
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    if enhancement_context:
        enhanced_system += f"\n\n{enhancement_context}"

    # Generate narrative with configurable backend
    from src.narrator import check_provider_availability, get_llm_provider_for_config

    config = NarratorConfig()
    provider = get_llm_provider_for_config(config)
    available, status_message = check_provider_availability(config, provider)

    if available:
        response = provider.chat(
            messages=[
                {"role": "system", "content": enhanced_system},
                {"role": "user", "content": prompt},
            ],
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            stream=False,
        )
        narrative = response if isinstance(response, str) else "".join(response)

        # Validate and log issues (non-blocking)
        is_valid, issues = validate_narrative(narrative)
        if not is_valid:
            import logging
            logging.getLogger("narrator").warning(f"Narrative validation issues: {issues}")
    else:
        narrative = f"{status_message}\n\n*Placeholder for: {player_input}*"

    # Update memory with new exchange
    updated_memory = MemoryStateModel(
        current_scene=narrative[:500],
        active_npcs=memory_state.active_npcs if hasattr(memory_state, 'active_npcs') else [],
        current_vow=memory_state.current_vow if hasattr(memory_state, 'current_vow') else "",
        recent_exchanges=memory_state.recent_exchanges if hasattr(memory_state, 'recent_exchanges') else [],
        scene_summaries=memory_state.scene_summaries if hasattr(memory_state, 'scene_summaries') else [],
        decisions_made=memory_state.decisions_made if hasattr(memory_state, 'decisions_made') else [],
        npcs_encountered=memory_state.npcs_encountered if hasattr(memory_state, 'npcs_encountered') else {},
        major_beats=memory_state.major_beats if hasattr(memory_state, 'major_beats') else [],
        key_relationships=memory_state.key_relationships if hasattr(memory_state, 'key_relationships') else {},
        world_changes=memory_state.world_changes if hasattr(memory_state, 'world_changes') else [],
    )
    
    # Add this exchange to recent
    if len(updated_memory.recent_exchanges) >= 5:
        updated_memory.recent_exchanges.pop(0)
    updated_memory.recent_exchanges.append({"role": "user", "content": player_input[:300]})

    return {
        "narrative": state.get("narrative", {}).__class__(
            **(state.get("narrative", {}).__dict__ if hasattr(state.get("narrative", {}), '__dict__') else {}),
            pending_narrative=narrative,
        ),
        "memory": updated_memory,
        "session": SessionState(
            awaiting_approval=True,
            turn_count=state.get("session", SessionState()).turn_count,
        ),
        "route": "approval",
    }


# ============================================================================
# Approval Node (Human-in-the-loop)
# ============================================================================

def approval_node(state: GameState) -> dict[str, Any]:
    """
    Pause for human approval of the generated narrative.
    Uses LangGraph interrupt() for human-in-the-loop.
    NOW INCLUDES: Feedback learning from accept/reject decisions.
    """
    from src.feedback_learning import FeedbackLearningEngine
    
    narrative = state.get("narrative")
    last_roll = state.get("last_roll")
    director_state = state.get("director", DirectorStateModel())
    character = state.get("character")
    world = state.get("world")
    session = state.get("session", SessionState())

    pending = narrative.pending_narrative if narrative else ""
    roll_text = last_roll.result_text if last_roll else ""

    # Interrupt and wait for user decision
    decision = interrupt({
        "type": "narrative_approval",
        "pending_narrative": pending,
        "roll_result": roll_text,
        "message": "Accept this narrative? (accept/retry/edit)",
    })

    # Initialize feedback engine
    try:
        feedback_engine = FeedbackLearningEngine(db_path=config.paths.feedback_db)
        
        # Build context for feedback recording
        feedback_context = {
            "pacing": director_state.last_pacing if hasattr(director_state, 'last_pacing') else "standard",
            "tone": director_state.last_tone if hasattr(director_state, 'last_tone') else "neutral",
            "scene_type": "general",  # Could be enhanced
            "npcs_present": [],  # Could extract from narrative
            "location": world.current_location if world else "",
            "oracle_result": "",
            "move_triggered": "",
            "session_number": session.turn_count if hasattr(session, 'turn_count') else 0,
        }
        
        # Record feedback based on decision
        if decision.get("decision") == "accept":
            feedback_engine.record_feedback(pending, accepted=True, context=feedback_context)
        elif decision.get("decision") == "retry":
            feedback_engine.record_feedback(pending, accepted=False, context=feedback_context)
    except Exception as e:
        # Graceful fallback if feedback system fails
        logger.warning(f"Feedback recording failed: {e}")

    # This will resume when user provides decision
    if decision.get("decision") == "accept":
        return {
            "session": SessionState(
                awaiting_approval=False,
                user_decision="accept",
                turn_count=state.get("session", SessionState()).turn_count + 1,
            ),
            "route": "world_state",
        }
    elif decision.get("decision") == "retry":
        return {
            "session": SessionState(
                awaiting_approval=False,
                user_decision="retry",
            ),
            "route": "narrator",
        }
    elif decision.get("decision") == "edit":
        edited = decision.get("edited_text", pending)
        # Record edit as partial accept
        try:
            feedback_engine.record_feedback(edited, accepted=True, context=feedback_context)
        except Exception as e:
            logger.debug(f"Feedback recording fallback: {e}")
        
        return {
            "narrative": state.get("narrative", {}).__class__(
                **(state.get("narrative", {}).__dict__ if hasattr(state.get("narrative", {}), '__dict__') else {}),
                pending_narrative=edited,
            ),
            "session": SessionState(
                awaiting_approval=False,
                user_decision="edit",
                edited_text=edited,
                turn_count=state.get("session", SessionState()).turn_count + 1,
            ),
            "route": "world_state",
        }

    return {"route": "world_state"}


# ============================================================================
# World State Manager Node - Enhanced with Consequence and Memory Integration
# ============================================================================

def world_state_manager_node(state: GameState) -> dict[str, Any]:
    """
    Update world state based on narrative outcomes.
    Now includes:
    - Event detection for consequence engine
    - Memory summarization
    - Vow progress tracking
    """
    from src.game_state import MemoryStateModel, ConsequenceEngineState
    
    character = state.get("character")
    last_roll = state.get("last_roll")
    narrative = state.get("narrative")
    session = state.get("session")
    memory_state = state.get("memory", MemoryStateModel())
    consequence_state = state.get("consequences", ConsequenceEngineState())

    # Finalize the narrative
    final_narrative = narrative.pending_narrative if narrative else ""

    # Apply stat changes based on outcome
    if character and last_roll:
        if last_roll.outcome == "strong_hit":
            # Gain momentum on strong hit
            character.momentum.value = min(character.momentum.value + 1, character.momentum.max_value)
        elif last_roll.outcome == "miss":
            # Lose momentum on miss
            character.momentum.value = max(character.momentum.value - 1, -6)

    # Detect significant events in the narrative for consequence engine
    new_delayed_beats = []
    narrative_lower = final_narrative.lower()
    
    # Simple event detection (would be enhanced with LLM in production)
    if any(word in narrative_lower for word in ["killed", "slain", "murdered", "destroyed"]):
        new_delayed_beats.append({
            "beat": "Someone connected to the fallen seeks answers",
            "trigger_after_scenes": 4,
            "priority": 6,
        })
    
    if any(word in narrative_lower for word in ["betrayed", "lied", "deceived"]):
        new_delayed_beats.append({
            "beat": "Word of the betrayal spreads",
            "trigger_after_scenes": 3,
            "priority": 7,
        })
    
    if any(word in narrative_lower for word in ["spared", "mercy", "let go"]):
        new_delayed_beats.append({
            "beat": "The one spared may return with unexpected news",
            "trigger_after_scenes": 5,
            "priority": 5,
        })
    
    if any(word in narrative_lower for word in ["discovery", "found", "uncovered", "revealed"]):
        new_delayed_beats.append({
            "beat": "Others learn of what was discovered",
            "trigger_after_scenes": 4,
            "priority": 4,
        })

    # Spawner integration - check for encounter spawn
    spawn_context_text = ""
    spawner_state = state.get("spawner", {})
    try:
        from src.spawner import EncounterDirector, SpawnContext
        
        director = EncounterDirector.from_dict(spawner_state) if spawner_state else EncounterDirector()
        
        world = state.get("world")
        character = state.get("character")
        
        spawn_ctx = SpawnContext(
            location=world.current_location if world else "unknown",
            location_type=getattr(world, 'location_type', 'neutral') if world else 'neutral',
            threat_level=getattr(world, 'threat_level', 0.3) if world else 0.3,
            player_health=character.health if hasattr(character, 'health') else 1.0,
            player_visible=True,
            recent_combat=any(word in narrative_lower for word in ["combat", "fight", "attack", "battle"]),
            difficulty=getattr(session, 'difficulty', 'normal') if session else 'normal',
        )
        
        decision = director.evaluate(spawn_ctx)
        
        if decision.should_spawn and decision.template:
            # Add spawn as a delayed beat for immediate processing
            new_delayed_beats.append({
                "beat": f"ENCOUNTER: {decision.narrative_intro}",
                "trigger_after_scenes": 0,  # Immediate
                "priority": 8,
            })
            
            # Update world state with enemy info
            if world:
                world.combat_active = True
                world.enemy_count = decision.count
                world.enemy_strength = decision.template.threat_value
        
        # Store updated spawner state
        spawner_state = director.to_dict()
        spawn_context_text = director.get_encounter_context()
    except Exception as e:
        logger.debug(f"System fallback: {e}")

    # Update consequence engine with new beats
    existing_beats = consequence_state.delayed_beats if hasattr(consequence_state, 'delayed_beats') else []
    updated_consequences = ConsequenceEngineState(
        delayed_beats=existing_beats + new_delayed_beats,
        moral_patterns=consequence_state.moral_patterns if hasattr(consequence_state, 'moral_patterns') else [],
        scene_count=consequence_state.scene_count if hasattr(consequence_state, 'scene_count') else 0,
    )

    # Update memory with scene summary
    # Simple summarization (would use LLM in production)
    scene_summary = final_narrative[:150] + "..." if len(final_narrative) > 150 else final_narrative
    
    updated_memory = MemoryStateModel(
        current_scene=final_narrative[:500],
        active_npcs=memory_state.active_npcs if hasattr(memory_state, 'active_npcs') else [],
        current_vow=memory_state.current_vow if hasattr(memory_state, 'current_vow') else "",
        recent_exchanges=memory_state.recent_exchanges if hasattr(memory_state, 'recent_exchanges') else [],
        scene_summaries=(memory_state.scene_summaries if hasattr(memory_state, 'scene_summaries') else []) + [scene_summary],
        decisions_made=memory_state.decisions_made if hasattr(memory_state, 'decisions_made') else [],
        npcs_encountered=memory_state.npcs_encountered if hasattr(memory_state, 'npcs_encountered') else {},
        major_beats=memory_state.major_beats if hasattr(memory_state, 'major_beats') else [],
        key_relationships=memory_state.key_relationships if hasattr(memory_state, 'key_relationships') else {},
        world_changes=memory_state.world_changes if hasattr(memory_state, 'world_changes') else [],
    )
    
    # Keep scene summaries limited
    if len(updated_memory.scene_summaries) > 10:
        updated_memory.scene_summaries = updated_memory.scene_summaries[-10:]

    # Auto-detect NPC names from narrative
    detected_npcs = extract_npc_names(final_narrative)
    if detected_npcs:
        current_npcs = updated_memory.active_npcs.copy()
        for npc in detected_npcs:
            if npc not in current_npcs:
                current_npcs.append(npc)
        updated_memory.active_npcs = current_npcs[:10]  # Limit to 10

    # Add the finalized narrative to messages
    new_message = {
        "role": "assistant",
        "content": final_narrative,
    }

    # ==========================================================================
    # ENHANCEMENT ENGINE - Post-Narrative Processing
    # Event detection, world state updates, and auto-save
    # ==========================================================================
    enhancement_state = state.get("enhancements", {})
    updated_enhancement_state = {}
    try:
        from src.enhancement_engine import EnhancementEngine
        
        enhancement_engine = EnhancementEngine.from_dict(enhancement_state) if enhancement_state else EnhancementEngine()
        
        world = state.get("world")
        
        # Post-narrative processing: detect events, update world state
        enhancement_engine.post_narrative(
            narrative_output=final_narrative,
            location=world.current_location if world else "",
            active_npcs=updated_memory.active_npcs if updated_memory else [],
            player_name=character.name if character else "the protagonist",
        )
        
        # Auto-save
        full_state = {
            "character": character.model_dump() if character and hasattr(character, 'model_dump') else {},
            "world": world.model_dump() if world and hasattr(world, 'model_dump') else {},
            "memory": updated_memory.model_dump() if updated_memory and hasattr(updated_memory, 'model_dump') else {},
            "turn_count": session.turn_count if session else 0,
        }
        enhancement_engine.auto_save(full_state)
        
        # Serialize updated enhancement state
        updated_enhancement_state = enhancement_engine.to_dict()
    except Exception as e:
        logger.debug(f"System fallback: {e}")

    return {
        "messages": [new_message],
        "character": character,
        "narrative": narrative.__class__(
            current_scene=final_narrative,
            pending_narrative="",
            campaign_summary=narrative.campaign_summary if narrative else "",
            session_summary=narrative.session_summary if narrative else "",
        ) if narrative else None,
        "memory": updated_memory,
        "consequences": updated_consequences,
        "enhancements": updated_enhancement_state,
        "session": SessionState(
            awaiting_approval=False,
            turn_count=session.turn_count if session else 0,
        ),
        "route": "end",
    }


# ============================================================================
# NPC Name Detection Helper
# ============================================================================

def extract_npc_names(text: str) -> list[str]:
    """
    Extract potential NPC names from narrative text.
    Looks for capitalized words that appear in dialogue attribution.
    """
    import re
    
    names = set()
    
    # Pattern 1: Direct quotes with attribution (e.g., "..." said Kira)
    quote_pattern = r'["\'].*?["\'][,\s]+(?:said|replied|asked|muttered|whispered|shouted|growled|answered|responded)\s+([A-Z][a-z]+)'
    matches = re.findall(quote_pattern, text)
    names.update(matches)
    
    # Pattern 2: Attribution before quote (e.g., Kira said "...")
    pre_quote_pattern = r'([A-Z][a-z]+)\s+(?:said|replied|asked|muttered|whispered|shouted|growled|answered|responded|looked|turned|nodded)[,\s]'
    matches = re.findall(pre_quote_pattern, text)
    names.update(matches)
    
    # Pattern 3: Possessive names (e.g., "Kira's eyes")
    possessive_pattern = r"([A-Z][a-z]+)'s\s+\w+"
    matches = re.findall(possessive_pattern, text)
    names.update(matches)
    
    # Filter out common non-names
    excluded = {"The", "You", "Your", "They", "Their", "This", "That", "There", "Here", 
                "When", "Where", "What", "Who", "Why", "How", "But", "And", "She", "He", "It"}
    names = {n for n in names if n not in excluded}
    
    return list(names)


# ============================================================================
# LLM-Powered Event Extraction (Optional Enhancement)
# ============================================================================

def extract_events_llm(narrative: str) -> list[dict]:
    """
    Use LLM to extract significant events from narrative.
    Falls back to regex if LLM unavailable.
    
    Returns list of events with type, description, and priority.
    """
    try:
        import ollama
        
        prompt = f"""Analyze this narrative and extract any significant events.
Output ONLY valid JSON array with events, no explanation.

Event types: kill, spare, betray, ally, discover, promise, threat, loss

Example output:
[{{"type": "kill", "target": "Raider Captain", "description": "Player killed enemy", "priority": 6}}]

If no significant events, output: []

Narrative:
{narrative[:1000]}"""

        client = ollama.Client()
        response = client.chat(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3, "num_predict": 256},
        )
        
        content = response.get("message", {}).get("content", "[]")
        
        # Parse JSON
        import json
        json_start = content.find("[")
        json_end = content.rfind("]") + 1
        if json_start >= 0 and json_end > json_start:
            events = json.loads(content[json_start:json_end])
            return events
    except Exception as e:
        logger.debug(f"System fallback: {e}")
    
    return []


def regex_event_fallback(narrative: str) -> list[dict]:
    """
    Fallback regex-based event detection.
    Used when LLM is unavailable.
    """
    events = []
    narrative_lower = narrative.lower()
    
    if any(word in narrative_lower for word in ["killed", "slain", "murdered", "destroyed"]):
        events.append({
            "type": "kill",
            "description": "Combat death detected",
            "beat": "Someone connected to the fallen seeks answers",
            "trigger_after_scenes": 4,
            "priority": 6,
        })
    
    if any(word in narrative_lower for word in ["betrayed", "lied", "deceived"]):
        events.append({
            "type": "betray",
            "description": "Betrayal detected",
            "beat": "Word of the betrayal spreads",
            "trigger_after_scenes": 3,
            "priority": 7,
        })
    
    if any(word in narrative_lower for word in ["spared", "mercy", "let go"]):
        events.append({
            "type": "spare",
            "description": "Mercy shown",
            "beat": "The one spared may return with unexpected news",
            "trigger_after_scenes": 5,
            "priority": 5,
        })
    
    if any(word in narrative_lower for word in ["discovery", "found", "uncovered", "revealed"]):
        events.append({
            "type": "discover",
            "description": "Discovery made",
            "beat": "Others learn of what was discovered",
            "trigger_after_scenes": 4,
            "priority": 4,
        })
    
    return events


# ============================================================================
# Command Node - Handles Session Commands
# ============================================================================

def command_node(state: GameState) -> dict[str, Any]:
    """
    Handle special commands like !end_session, !status, etc.
    """
    from src.game_state import MemoryStateModel, VowManagerState, ConsequenceEngineState
    
    command_type = state.get("command_type", "help")
    character = state.get("character")
    memory_state = state.get("memory", MemoryStateModel())
    vow_state = state.get("vows", VowManagerState())
    consequence_state = state.get("consequences", ConsequenceEngineState())
    director_state = state.get("director", DirectorStateModel())
    
    response = ""
    
    if command_type == "end_session":
        # Summarize session and move to campaign memory
        session_scenes = memory_state.scene_summaries if hasattr(memory_state, 'scene_summaries') else []
        session_summary = " ".join(session_scenes[-5:]) if session_scenes else "No significant events this session."
        
        # Update memory
        updated_memory = MemoryStateModel(
            current_scene="",
            active_npcs=[],
            current_vow=memory_state.current_vow if hasattr(memory_state, 'current_vow') else "",
            recent_exchanges=[],
            scene_summaries=[],  # Clear session scenes
            decisions_made=[],
            npcs_encountered={},
            major_beats=(memory_state.major_beats if hasattr(memory_state, 'major_beats') else []) + [f"Session: {session_summary[:200]}"],
            key_relationships=memory_state.key_relationships if hasattr(memory_state, 'key_relationships') else {},
            world_changes=memory_state.world_changes if hasattr(memory_state, 'world_changes') else [],
        )
        
        response = f"**Session Ended**\n\nSession summary added to campaign memory:\n> {session_summary[:300]}..."
        
        return {
            "messages": [{"role": "assistant", "content": response}],
            "memory": updated_memory,
            "route": "end",
        }
    
    elif command_type == "status":
        # Show current game state
        lines = ["**Current Status**\n"]
        lines.append(f"**Character:** {character.name if character else 'Unknown'}")
        lines.append(f"**Director Pacing:** {director_state.last_pacing if hasattr(director_state, 'last_pacing') else 'standard'}")
        lines.append(f"**Director Tone:** {director_state.last_tone if hasattr(director_state, 'last_tone') else 'mysterious'}")
        lines.append(f"**Tension Level:** {director_state.tension_level if hasattr(director_state, 'tension_level') else 0.2:.0%}")
        lines.append(f"**Scenes Since Breather:** {director_state.scenes_since_breather if hasattr(director_state, 'scenes_since_breather') else 0}")
        
        delayed = consequence_state.delayed_beats if hasattr(consequence_state, 'delayed_beats') else []
        lines.append(f"\n**Delayed Beats Queued:** {len(delayed)}")
        
        npcs = memory_state.active_npcs if hasattr(memory_state, 'active_npcs') else []
        if npcs:
            lines.append(f"**Active NPCs:** {', '.join(npcs)}")
        
        response = "\n".join(lines)
    
    elif command_type == "vows":
        # Show vow status
        lines = ["**Active Vows**\n"]
        
        if character and hasattr(character, 'vows') and character.vows:
            for vow in character.vows:
                progress = vow.ticks / 40.0
                bar = "█" * int(progress * 10) + "░" * (10 - int(progress * 10))
                lines.append(f"• **{vow.name}** ({vow.rank})")
                lines.append(f"  Progress: [{bar}] {progress:.0%}")
        else:
            lines.append("No active vows.")
        
        response = "\n".join(lines)
    
    elif command_type == "npcs":
        # Show known NPCs
        lines = ["**Known NPCs**\n"]
        
        relationships = memory_state.key_relationships if hasattr(memory_state, 'key_relationships') else {}
        if relationships:
            for npc, rel in relationships.items():
                lines.append(f"• **{npc}:** {rel}")
        else:
            lines.append("No NPCs recorded yet.")
        
        active = memory_state.active_npcs if hasattr(memory_state, 'active_npcs') else []
        if active:
            lines.append(f"\n**Currently Active:** {', '.join(active)}")
        
        response = "\n".join(lines)
    
    elif command_type == "help":
        response = """**Available Commands**

• `!status` - Show Director state, tension, and game info
• `!vows` - Display active vows and progress
• `!npcs` - List known NPCs and relationships
• `!end_session` - End session and save to campaign memory
• `!help` - Show this help message"""
    
    return {
        "messages": [{"role": "assistant", "content": response}],
        "route": "end",
    }
