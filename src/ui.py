"""
Gradio UI for Starforged AI Game Master.
Dark sci-fi themed interface with chat, sidebar, and action buttons.
"""

from __future__ import annotations
import gradio as gr
from typing import Generator

from src.game_state import Character, create_initial_state
from src.narrator import generate_narrative_stream, NarratorConfig


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

    def __init__(self):
        self.character: Character | None = None
        self.session_id: str = ""
        self.pending_narrative: str = ""
        self.last_roll: str = ""
        self.awaiting_approval: bool = False
        self.chat_history: list[tuple[str, str]] = []

    def reset(self):
        """Reset session state."""
        self.__init__()


# Global session (will be replaced with proper state management)
_session = GameSession()


# ============================================================================
# UI Functions
# ============================================================================

def create_character(name: str, edge: int, heart: int, iron: int, shadow: int, wits: int):
    """Create a new character and start the game."""
    from src.game_state import Character, CharacterStats, CharacterCondition, MomentumState, VowState

    _session.reset()
    _session.session_id = f"session_{hash(name)}"

    _session.character = Character(
        name=name,
        stats=CharacterStats(edge=edge, heart=heart, iron=iron, shadow=shadow, wits=wits),
        condition=CharacterCondition(),
        momentum=MomentumState(),
        vows=[VowState(name="Background Vow", rank="epic")],
    )

    intro = f"Welcome, {name}. Your journey through the Forge begins..."
    _session.chat_history.append(("System", intro))

    return (
        _session.chat_history,
        format_stats(_session.character),
        format_momentum(_session.character.momentum.value),
        format_condition(_session.character.condition),
        format_vows(_session.character.vows),
    )


def format_stats(character: Character) -> str:
    """Format character stats for display."""
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
    health_bar = "●" * condition.health + "○" * (5 - condition.health)
    spirit_bar = "●" * condition.spirit + "○" * (5 - condition.spirit)
    supply_bar = "●" * condition.supply + "○" * (5 - condition.supply)
    return f"""
**Health:** [{health_bar}] {condition.health}/5
**Spirit:** [{spirit_bar}] {condition.spirit}/5
**Supply:** [{supply_bar}] {condition.supply}/5
    """.strip()


def format_vows(vows: list) -> str:
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


def process_player_input(message: str, history: list) -> Generator:
    """Process player input and generate narrative response."""
    if not _session.character:
        yield history + [("System", "Please create a character first.")], "", "", "", ""
        return

    # Add player message to history
    history = history + [(message, None)]
    yield history, "", "", "", ""

    # Generate narrative response
    config = NarratorConfig()
    narrative = ""

    for chunk in generate_narrative_stream(
        player_input=message,
        roll_result=_session.last_roll,
        outcome="",
        character_name=_session.character.name,
        location="the Forge",
    ):
        narrative += chunk
        history[-1] = (message, narrative)
        yield history, format_stats(_session.character), format_momentum(_session.character.momentum.value), format_condition(_session.character.condition), format_vows(_session.character.vows)

    _session.pending_narrative = narrative
    _session.awaiting_approval = True
    _session.chat_history = history


def accept_narrative():
    """Accept the pending narrative."""
    _session.awaiting_approval = False
    _session.pending_narrative = ""
    return "✓ Narrative accepted"


def retry_narrative():
    """Request a new narrative."""
    if _session.chat_history:
        last_input = _session.chat_history[-1][0]
        _session.chat_history = _session.chat_history[:-1]
        # This would trigger regeneration
    return "Regenerating..."


def edit_narrative(edited_text: str):
    """Apply edited narrative."""
    if _session.chat_history:
        msg, _ = _session.chat_history[-1]
        _session.chat_history[-1] = (msg, edited_text)
    _session.awaiting_approval = False
    return _session.chat_history


# ============================================================================
# Main UI
# ============================================================================

def create_ui() -> gr.Blocks:
    """Create the complete Gradio interface."""

    with gr.Blocks(css=CUSTOM_CSS, title="Starforged AI Game Master", theme=gr.themes.Base()) as demo:
        gr.Markdown("# ⚔️ Starforged AI Game Master", elem_classes=["section-header"])

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

                        gr.Markdown("---")
                        with gr.Row():
                            save_btn = gr.Button("💾 Save", size="sm")
                            load_btn = gr.UploadButton("📂 Load", file_types=[".json"], size="sm")

        # Event handlers
        create_btn.click(
            create_character,
            inputs=[char_name, edge_stat, heart_stat, iron_stat, shadow_stat, wits_stat],
            outputs=[chatbot, stats_display, momentum_display, condition_display, vows_display],
        )

        submit_btn.click(
            process_player_input,
            inputs=[player_input, chatbot],
            outputs=[chatbot, stats_display, momentum_display, condition_display, vows_display],
        ).then(lambda: "", outputs=player_input)

        player_input.submit(
            process_player_input,
            inputs=[player_input, chatbot],
            outputs=[chatbot, stats_display, momentum_display, condition_display, vows_display],
        ).then(lambda: "", outputs=player_input)

        accept_btn.click(accept_narrative)
        retry_btn.click(retry_narrative)

        def show_edit():
            return gr.update(visible=True), gr.update(visible=True)

        edit_btn.click(show_edit, outputs=[edit_box, save_edit_btn])
        save_edit_btn.click(edit_narrative, inputs=[edit_box], outputs=[chatbot])

    return demo


def launch_ui(share: bool = False, server_port: int = 7860):
    """Launch the Gradio interface."""
    demo = create_ui()
    demo.launch(share=share, server_port=server_port)


if __name__ == "__main__":
    launch_ui()
