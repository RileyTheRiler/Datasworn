"""
Gradio UI for Starforged AI Game Master.
Dark sci-fi themed interface with chat, sidebar, and action buttons.
"""

from __future__ import annotations
import json
import threading
from pathlib import Path
from typing import Generator, Optional
from uuid import uuid4

import gradio as gr

from src.game_state import Character
from src.narrator import generate_narrative_stream, NarratorConfig
from src.game_state import Character, create_initial_state
from src.narrator import generate_narrative_stream, NarratorConfig, check_provider_availability


# ============================================================================
# Custom CSS for Dark Sci-Fi Theme
# ============================================================================

CUSTOM_CSS = """
.gradio-container {
    background: linear-gradient(to bottom, #0f0f23, #1a1a2e) !important;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
}

#game-chat {
    border: 1px solid #ffd700 !important;
    background: rgba(26, 26, 46, 0.9) !important;
    border-radius: 8px;
}

#game-chat .message {
    background: rgba(45, 45, 68, 0.8) !important;
    border-radius: 4px;
    margin: 4px 0;
}

.stat-display {
    font-family: 'Courier New', monospace;
    font-size: 1.2em;
    color: #ffd700;
    background: rgba(45, 45, 68, 0.8);
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #3d3d5c;
}

.dice-result {
    background: #2d2d44;
    padding: 12px;
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    border-left: 3px solid #ffd700;
    margin: 8px 0;
}

.section-header {
    color: #ffd700;
    font-weight: bold;
    font-size: 0.9em;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid #3d3d5c;
}

.momentum-positive {
    color: #4ade80;
}

.momentum-negative {
    color: #f87171;
}

.vow-track {
    background: rgba(45, 45, 68, 0.6);
    padding: 8px;
    margin: 4px 0;
    border-radius: 4px;
    font-size: 0.9em;
}

.action-btn {
    min-height: 40px;
}

#accept-btn {
    background: #22c55e !important;
    border: none !important;
}

#retry-btn {
    background: #f59e0b !important;
    border: none !important;
}

#edit-btn {
    background: #3b82f6 !important;
    border: none !important;
}

.director-panel {
    background: rgba(45, 45, 68, 0.6);
    padding: 8px;
    border-radius: 4px;
    font-size: 0.85em;
}

.pacing-slow { color: #60a5fa; }
.pacing-standard { color: #a3a3a3; }
.pacing-fast { color: #f87171; }

.tone-ominous { color: #8b5cf6; }
.tone-tense { color: #ef4444; }
.tone-mysterious { color: #6366f1; }
.tone-hopeful { color: #22c55e; }
.tone-triumphant { color: #fbbf24; }
.tone-melancholic { color: #64748b; }

.beat-countdown {
    background: rgba(139, 92, 246, 0.2);
    padding: 4px 8px;
    border-radius: 4px;
    margin: 2px 0;
    font-size: 0.85em;
    border-left: 2px solid #8b5cf6;
}
"""


# ============================================================================
# State Management
# ============================================================================

class GameSession:
    """Manages game session state for the UI."""

    def __init__(self, session_id: Optional[str] = None):
        self.character: Character | None = None
        self.session_id: str = session_id or ""
        self.pending_narrative: str = ""
        self.last_roll: str = ""
        self.awaiting_approval: bool = False
        self.chat_history: list[tuple[str, str]] = []

        # New System States
        self.quest_lore: dict | None = None
        self.world: dict | None = None
        self.companions: dict | None = None

    def reset(self, session_id: Optional[str] = None):
        """Reset session state."""
        self.__init__(session_id=session_id or self.session_id)

    def to_dict(self) -> dict:
        """Serialize the session for persistence."""
        return {
            "session_id": self.session_id,
            "character": self.character.model_dump() if self.character else None,
            "pending_narrative": self.pending_narrative,
            "last_roll": self.last_roll,
            "awaiting_approval": self.awaiting_approval,
            "chat_history": [list(item) for item in self.chat_history],
            "quest_lore": self.quest_lore,
            "world": self.world,
            "companions": self.companions,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameSession":
        session = cls(session_id=data.get("session_id", ""))
        if data.get("character"):
            session.character = Character.model_validate(data["character"])
        session.pending_narrative = data.get("pending_narrative", "")
        session.last_roll = data.get("last_roll", "")
        session.awaiting_approval = data.get("awaiting_approval", False)
        session.chat_history = [tuple(item) for item in data.get("chat_history", [])]
        session.quest_lore = data.get("quest_lore")
        session.world = data.get("world")
        session.companions = data.get("companions")
        return session


class SessionStore:
    """Lightweight JSON persistence for UI sessions."""

    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _read_all(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text())
        except json.JSONDecodeError:
            return {}

    def _write_all(self, data: dict):
        self.path.write_text(json.dumps(data, indent=2))

    def load_session(self, session_id: str) -> GameSession:
        with self._lock:
            data = self._read_all()
            if session_id in data:
                return GameSession.from_dict(data[session_id])
        return GameSession(session_id=session_id)

    def save_session(self, session: GameSession):
        with self._lock:
            data = self._read_all()
            data[session.session_id] = session.to_dict()
            self._write_all(data)


SESSION_STORE = SessionStore(Path("saves/ui_sessions.json"))


# ============================================================================
# UI Functions
# ============================================================================

def _get_or_create_session(session_id: Optional[str], request: Optional[gr.Request]) -> GameSession:
    """Resolve the active session using the request session hash when needed."""
    resolved_id = session_id or getattr(request, "session_hash", None) or f"session_{uuid4().hex}"
    session = SESSION_STORE.load_session(resolved_id)
    if not session.session_id:
        session.session_id = resolved_id
    return session


def _render_session(session: GameSession):
    """Return UI-friendly values for the current session state."""
    if not session.character:
        return (
            session.chat_history,
            "*Create a character to begin*",
            "*—*",
            "*—*",
            "*No active vows*",
            "*No active quests*",
            "*Safe*",
            "*Solo*",
        )

    return (
        session.chat_history,
        format_stats(session.character),
        format_momentum(session.character.momentum.value),
        format_condition(session.character.condition),
        format_vows(session.character.vows),
        format_quests(session.quest_lore),
        format_combat(session.world),
        format_companions(session.companions),
    )


def create_character(
    name: str,
    edge: int,
    heart: int,
    iron: int,
    shadow: int,
    wits: int,
    session_id: Optional[str],
    request: gr.Request | None = None,
):
    """Create a new character and start the game."""
    from src.game_state import Character, CharacterStats, CharacterCondition, MomentumState, VowState

    session = _get_or_create_session(session_id, request)
    session.reset(session.session_id or f"session_{hash(name)}")

    session.character = Character(
        name=name,
        stats=CharacterStats(edge=edge, heart=heart, iron=iron, shadow=shadow, wits=wits),
        condition=CharacterCondition(),
        momentum=MomentumState(),
        vows=[VowState(name="Background Vow", rank="epic")],
    )

    intro = f"Welcome, {name}. Your journey through the Forge begins..."
    session.chat_history.append(("System", intro))
    SESSION_STORE.save_session(session)

    rendered = _render_session(session)
    return (*rendered, session.session_id)


def format_stats(character: Character | None) -> str:
    """Format character stats for display."""
    if not character:
        return "*Create a character to begin*"

    stats = character.stats
    return f"""
**Edge:** {stats.edge} | **Heart:** {stats.heart} | **Iron:** {stats.iron}
**Shadow:** {stats.shadow} | **Wits:** {stats.wits}
    """.strip()


def format_momentum(value: int) -> str:
    """Format momentum with color coding."""
    color_class = "momentum-positive" if value >= 0 else "momentum-negative"
    bar = "█" * max(0, value + 6) + "░" * max(0, 10 - value)
    return f"**Momentum:** {value:+d}\n`[{bar}]`"


def format_condition(condition) -> str:
    """Format condition meters."""
    if not condition:
        return "*No condition data*"

    health_bar = "●" * condition.health + "○" * (5 - condition.health)
    spirit_bar = "●" * condition.spirit + "○" * (5 - condition.spirit)
    supply_bar = "●" * condition.supply + "○" * (5 - condition.supply)
    return f"""
**Health:** [{health_bar}] {condition.health}/5
**Spirit:** [{spirit_bar}] {condition.spirit}/5
**Supply:** [{supply_bar}] {condition.supply}/5
    """.strip()


def format_vows(vows: list | None) -> str:
    """Format active vows."""
    if not vows:
        return "*No active vows*"

    lines = []
    for vow in vows:
        boxes = vow.ticks // 4
        bar = "█" * boxes + "░" * (10 - boxes)
        status = "✓" if vow.completed else ""
        lines.append(f"**{vow.name}** ({vow.rank}) [{bar}] {status}")

    return "\n".join(lines)


def format_director_state(director_state) -> str:
    """Format Director state for display."""
    if not director_state:
        return "*Awaiting first scene...*"
    
    pacing = getattr(director_state, 'last_pacing', 'standard')
    tone = getattr(director_state, 'last_tone', 'mysterious')
    tension = getattr(director_state, 'tension_level', 0.2)
    scenes_since = getattr(director_state, 'scenes_since_breather', 0)
    
    # Pacing indicator
    pacing_emoji = {"slow": "🐢", "standard": "➡️", "fast": "⚡"}.get(pacing, "➡️")
    
    # Tone indicator
    tone_emoji = {
        "ominous": "👁️", "tense": "⚠️", "mysterious": "🔮",
        "hopeful": "🌟", "triumphant": "🏆", "melancholic": "🌧️"
    }.get(tone, "🔮")
    
    # Tension bar
    tension_bar = "█" * int(tension * 10) + "░" * (10 - int(tension * 10))
    
    lines = [
        f"**Pacing:** {pacing_emoji} {pacing.title()}",
        f"**Tone:** {tone_emoji} {tone.title()}",
        f"**Tension:** [{tension_bar}] {tension:.0%}",
        f"**No breather for:** {scenes_since} scenes",
    ]
    
    return "\n".join(lines)


def format_delayed_beats(consequence_state) -> str:
    """Format upcoming delayed beats for display."""
    if not consequence_state:
        return "*No events queued*"
    
    beats = getattr(consequence_state, 'delayed_beats', [])
    if not beats:
        return "*No events queued*"
    
    lines = []
    for beat in beats[:4]:  # Show max 4
        scenes_left = beat.get("trigger_after_scenes", 1)
        beat_text = beat.get("beat", "Unknown event")[:50]
        priority = beat.get("priority", 5)
        
        # Priority indicator
        if priority >= 7:
            indicator = "🔴"
        elif priority >= 5:
            indicator = "🟡"
        else:
            indicator = "🟢"
        
        lines.append(f"{indicator} **{scenes_left}** scenes: {beat_text}...")
    
    if len(beats) > 4:
        lines.append(f"*...and {len(beats) - 4} more*")
    
    return "\n".join(lines) if lines else "*No events queued*"


def format_quests(quest_lore_state) -> str:
    """Format active quests and objectives."""
    from src.quest_lore import QuestLoreEngine

    # Safely handle Dict or Pydantic model
    if hasattr(quest_lore_state, 'model_dump'):
        data = quest_lore_state.model_dump()
    elif isinstance(quest_lore_state, dict):
        data = quest_lore_state
    else:
        return "*No active quests*"

    try:
        engine = QuestLoreEngine.from_dict(data)
        quests_dict = engine.quests.quests
        
        # Get simplified text representation
        lines = []
        for q_id, quest in engine.quests.quests.items():
            if quest.status.value != "completed":
                lines.append(f"**{quest.title}**")
                for obj in quest.objectives:
                    completed = getattr(obj, "is_completed", getattr(obj, "completed", False))
                    status = "☑️" if completed else "⬜"
                    lines.append(f"{status} {obj.description}")
        
        return "\n".join(lines) if lines else "*No active quests*"
    except Exception:
        # Fall back to raw dict traversal if dataclass parsing fails
        quests_dict = data.get("quests", {}).get("quests", {}) if isinstance(data, dict) else {}

    lines = []
    for quest in quests_dict.values():
        if isinstance(quest, dict):
            title = quest.get("title")
            status = quest.get("status", "")
            objectives = quest.get("objectives", [])
        else:
            title = getattr(quest, "title", None)
            status_val = getattr(quest, "status", "")
            status = status_val.value if hasattr(status_val, "value") else status_val
            objectives = getattr(quest, "objectives", [])

        if status == "completed":
            continue

        if title:
            lines.append(f"**{title}**")

        for obj in objectives:
            if isinstance(obj, dict):
                completed = obj.get("is_completed", False) or obj.get("completed", False)
                desc = obj.get("description", "")
            else:
                completed = getattr(obj, "is_completed", False)
                desc = getattr(obj, "description", "")

            status_icon = "☑️" if completed else "⬜"
            lines.append(f"{status_icon} {desc}")

    return "\n".join(lines) if lines else "*No active quests*"


def format_combat(world_state) -> str:
    """Format combat status if active."""
    if not world_state or not getattr(world_state, 'combat_active', False):
        return "*Safe*"
        
    count = getattr(world_state, 'enemy_count', 0)
    strength = getattr(world_state, 'enemy_strength', 1.0)
    threat = getattr(world_state, 'threat_level', 0.0)
    
    # Visual threat bar
    threat_int = int(threat * 5)
    bar = "⚠️" * threat_int + "⚪" * (5 - threat_int)
    
    return f"""
**COMBAT ACTIVE**
{bar}
**Enemies:** {count}
**Strength:** {strength:.1f}
    """.strip()


def format_companions(companion_state) -> str:
    """Format active companion status."""
    active_id = getattr(companion_state, 'active_companion', "")
    companions = getattr(companion_state, 'companions', {})
    
    if not active_id or active_id not in companions:
        return "*Solo*"
        
    comp = companions[active_id]
    name = comp.get("name", "Companion")
    role = comp.get("archetype", "Ally").title()
    loyalty = comp.get("loyalty", 0)
    
    return f"""
**{name}** ({role})
Loyalty: {loyalty}/10
    """.strip()


def process_player_input(message: str, history: list, session_id: Optional[str], request: gr.Request | None = None) -> Generator:
    """Process player input and generate narrative response."""
    session = _get_or_create_session(session_id, request)
    history = session.chat_history or history

    if not session.character:
        updated_history = history + [("System", "Please create a character first.")]
        session.chat_history = updated_history
        SESSION_STORE.save_session(session)
        yield (*_render_session(session), session.session_id)
        return

    # Add player message to history
    history = history + [(message, None)]
    session.chat_history = history
    SESSION_STORE.save_session(session)
    yield (*_render_session(session), session.session_id)

    # Generate narrative response
    config = NarratorConfig()
    available, status_message = check_provider_availability(config)
    narrative = ""

    if not available:
        narrative = status_message
        history[-1] = (message, narrative)
        session.chat_history = history
        SESSION_STORE.save_session(session)
        yield (*_render_session(session), session.session_id)
        return

    for chunk in generate_narrative_stream(
        player_input=message,
        roll_result=session.last_roll,
        outcome="",
        character_name=session.character.name,
        location="the Forge",
    ):
        narrative += chunk
        history[-1] = (message, narrative)
        session.chat_history = history
        yield (*_render_session(session), session.session_id)

    session.pending_narrative = narrative
    session.awaiting_approval = True
    SESSION_STORE.save_session(session)
    yield (*_render_session(session), session.session_id)


def accept_narrative(session_id: Optional[str], request: gr.Request | None = None):
    """Accept the pending narrative."""
    session = _get_or_create_session(session_id, request)
    session.awaiting_approval = False
    session.pending_narrative = ""
    SESSION_STORE.save_session(session)
    return "✓ Narrative accepted"


def retry_narrative(session_id: Optional[str], request: gr.Request | None = None):
    """Request a new narrative."""
    session = _get_or_create_session(session_id, request)
    if session.chat_history:
        _ = session.chat_history[-1][0]
        session.chat_history = session.chat_history[:-1]
    SESSION_STORE.save_session(session)
    return "Regenerating..."


def edit_narrative(edited_text: str, session_id: Optional[str], request: gr.Request | None = None):
    """Apply edited narrative."""
    session = _get_or_create_session(session_id, request)
    if session.chat_history:
        msg, _ = session.chat_history[-1]
        session.chat_history[-1] = (msg, edited_text)
    session.awaiting_approval = False
    SESSION_STORE.save_session(session)
    return session.chat_history


def restore_session(session_id: Optional[str], request: gr.Request | None = None):
    """Load a persisted session when the UI initializes."""
    session = _get_or_create_session(session_id, request)
    SESSION_STORE.save_session(session)
    return (*_render_session(session), session.session_id)


# ============================================================================
# Main UI
# ============================================================================

def create_ui() -> gr.Blocks:
    """Create the complete Gradio interface."""

    with gr.Blocks(css=CUSTOM_CSS, title="Starforged AI Game Master", theme=gr.themes.Base()) as demo:
        gr.Markdown("# ⚔️ Starforged AI Game Master", elem_classes=["section-header"])

        session_state = gr.State()


        with gr.Tabs():
            # Character Creation Tab
            with gr.Tab("Character Creation"):
                gr.Markdown("### Create Your Character")
                with gr.Row():
                    with gr.Column(scale=2):
                        char_name = gr.Textbox(label="Character Name", placeholder="Enter your character's name")

                        gr.Markdown("**Allocate Stats** (each 1-3, total of 14 points)")
                        with gr.Row():
                            edge_stat = gr.Slider(1, 3, value=2, step=1, label="Edge")
                            heart_stat = gr.Slider(1, 3, value=2, step=1, label="Heart")
                            iron_stat = gr.Slider(1, 3, value=2, step=1, label="Iron")
                        with gr.Row():
                            shadow_stat = gr.Slider(1, 3, value=2, step=1, label="Shadow")
                            wits_stat = gr.Slider(1, 3, value=3, step=1, label="Wits")

                        create_btn = gr.Button("Begin Adventure", variant="primary")

            # Game Tab
            with gr.Tab("Adventure"):
                with gr.Row():
                    # Main chat area
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            elem_id="game-chat",
                            height=500,
                            show_label=False,
                        )

                        with gr.Row():
                            player_input = gr.Textbox(
                                placeholder="What do you do?",
                                show_label=False,
                                scale=4,
                            )
                            submit_btn = gr.Button("▶", scale=1, variant="primary")

                        with gr.Row():
                            accept_btn = gr.Button("✓ Accept", elem_id="accept-btn", elem_classes=["action-btn"])
                            retry_btn = gr.Button("🔄 Retry", elem_id="retry-btn", elem_classes=["action-btn"])
                            edit_btn = gr.Button("✏️ Edit", elem_id="edit-btn", elem_classes=["action-btn"])

                        edit_box = gr.Textbox(
                            label="Edit Narrative",
                            lines=4,
                            visible=False,
                        )
                        save_edit_btn = gr.Button("Save Edit", visible=False)

                    # Sidebar
                    with gr.Column(scale=1):
                        gr.Markdown("### Character", elem_classes=["section-header"])
                        stats_display = gr.Markdown("*Create a character to begin*")

                        gr.Markdown("### Momentum", elem_classes=["section-header"])
                        momentum_display = gr.Markdown("*—*")

                        gr.Markdown("### Condition", elem_classes=["section-header"])
                        condition_display = gr.Markdown("*—*")

                        gr.Markdown("### Vows", elem_classes=["section-header"])
                        vows_display = gr.Markdown("*—*")

                        gr.Markdown("### Director", elem_classes=["section-header"])
                        director_display = gr.Markdown("*Awaiting...*")

                        gr.Markdown("### Upcoming Events", elem_classes=["section-header"])
                        beats_display = gr.Markdown("*No delayed beats*")

                        gr.Markdown("### Quests", elem_classes=["section-header"])
                        quests_display = gr.Markdown("*No active quests*")

                        gr.Markdown("### Combat Status", elem_classes=["section-header"])
                        combat_display = gr.Markdown("*Safe*")

                        gr.Markdown("### Companions", elem_classes=["section-header"])
                        companion_display = gr.Markdown("*Solo*")

                        gr.Markdown("---")
                        with gr.Row():
                            save_btn = gr.Button("💾 Save", size="sm")
                            load_btn = gr.UploadButton("📂 Load", file_types=[".json"], size="sm")


        # Event handlers
        create_btn.click(
            create_character,
            inputs=[char_name, edge_stat, heart_stat, iron_stat, shadow_stat, wits_stat, session_state],
            outputs=[
                chatbot,
                stats_display,
                momentum_display,
                condition_display,
                vows_display,
                quests_display,
                combat_display,
                companion_display,
                session_state,
            ],
        )

        submit_btn.click(
            process_player_input,
            inputs=[player_input, chatbot, session_state],
            outputs=[
                chatbot,
                stats_display,
                momentum_display,
                condition_display,
                vows_display,
                quests_display,
                combat_display,
                companion_display,
                session_state,
            ],
        ).then(lambda: "", outputs=player_input)

        player_input.submit(
            process_player_input,
            inputs=[player_input, chatbot, session_state],
            outputs=[
                chatbot,
                stats_display,
                momentum_display,
                condition_display,
                vows_display,
                quests_display,
                combat_display,
                companion_display,
                session_state,
            ],
        ).then(lambda: "", outputs=player_input)

        accept_btn.click(accept_narrative, inputs=[session_state])
        retry_btn.click(retry_narrative, inputs=[session_state])

        def show_edit():
            return gr.update(visible=True), gr.update(visible=True)

        edit_btn.click(show_edit, outputs=[edit_box, save_edit_btn])
        save_edit_btn.click(edit_narrative, inputs=[edit_box, session_state], outputs=[chatbot])

        demo.load(
            restore_session,
            inputs=[session_state],
            outputs=[
                chatbot,
                stats_display,
                momentum_display,
                condition_display,
                vows_display,
                quests_display,
                combat_display,
                companion_display,
                session_state,
            ],
        )

    return demo


def launch_ui(share: bool = False, server_port: int = 7860):
    """Launch the Gradio interface."""
    demo = create_ui()
    demo.launch(share=share, server_port=server_port)


if __name__ == "__main__":
    launch_ui()
