# Starforged AI Game Master

A professional-grade AI Game Master for **Ironsworn: Starforged** TTRPG, featuring 48+ interconnected narrative intelligence systems.

## Features

### 🎭 Master-Level Storytelling
- **Prose Craft Engine** — Sentence rhythm, sensory details, dialogue compression
- **Narrative Architecture** — Tension arcs, foreshadowing, thematic echoes
- **Character Systems** — Hero's Journey tracking, relationship dynamics
- **Voice Integration** — Real-time Speech-to-Text and immersive AI narration (`🎙️`)
- **World Simulation** — Faction politics, weather, economy, NPC schedules

### 🧠 Self-Improving AI
The system learns from your preferences over time:
- Accept/reject feedback builds your personal style profile
- Few-shot examples from paragraphs you loved
- Automatic prompt modifications based on your patterns
- The more you play, the better it gets *for you specifically*

### 🎲 Full Starforged Rules
- Complete move resolution with oracle tables
- Vow and progress track management
- Asset and ability integration
- Datasworn-compatible game data

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Ollama (local) or Gemini (API) |
| Orchestration | LangGraph |
| UI | Gradio |
| Game Data | Datasworn JSON |
| Persistence | SQLite |

## Installation

```bash
git clone https://github.com/RileyTheRiler/Datasworn.git
cd Datasworn
pip install -r requirements.txt
```

**Prerequisites:**
- Python 3.10+
- **Either** Ollama (local) **or** a Gemini API key

> **Note on Gemini SDK:**
> The legacy `google-generativeai` package now emits a deprecation warning during the test suite. Google recommends migrating to `google.genai`; this repository will switch once downstream tooling finishes validating the new SDK. In the meantime the warning is harmless and tests still pass.

## LLM Configuration

### Option 1: Ollama (Local, Free)
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.1

# Run the game (Ollama is default)
python main.py
```

### Option 2: Gemini API (Cloud)
```bash
# Install Gemini SDK
pip install google-generativeai

# Set your API key
export GEMINI_API_KEY="your-api-key-here"
export LLM_PROVIDER="gemini"

# Or in Python:
from src.llm_provider import configure_gemini
configure_gemini("your-api-key-here")
```

**🔒 Security Best Practices:**

Your API key should **ONLY** be stored in the `.env` file, which is already in `.gitignore` and will not be committed to git.

1. **Copy the template**: `cp .env.example .env`
2. **Add your new key**: Edit `.env` and replace `your-new-api-key-here` with your actual Gemini API key
3. **Never commit `.env`**: The `.gitignore` file already protects this file from being committed
4. **Use `.env.example` for documentation only**: This file should only contain placeholder values

**Environment Variables:**
| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `ollama` or `gemini` | `ollama` |
| `GEMINI_API_KEY` | Your Gemini API key | - |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.0-flash` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.1` |


## Quick Start

```bash
# CLI Mode (recommended for testing)
python main.py --cli

# Run the onboarding wizard and save defaults
python main.py --onboard

# Launch a ready-to-play demo session
python main.py --demo

# Resume with web UI (default)
# Web UI
python main.py
```

Running `--onboard` saves your LLM provider, model, and audio preferences so future `--cli` sessions start with your defaults. If an autosave is found, the CLI will offer a one-step resume before you begin a new scene, keeping pacing and vows intact.

During CLI play, the Director and autosave systems stay in sync: `!status` reports the current tension/pacing heartbeat, and each turn is automatically saved so you can safely exit and resume later without losing your rhythm.

### Test warnings to expect
- The legacy `google-generativeai` SDK currently emits a deprecation warning; migration to `google.genai` is planned once tooling stabilizes.
- A Pydantic v2 notice surfaces in `src/server.py` when invoking director psyche APIs; the warning is harmless and slated for cleanup during the SDK migration.
- Some integration paths may log a coroutine-not-awaited runtime warning when exercising hazard generation fixtures; current behavior does not impact results and will be addressed with upcoming async refactors.
### Gameplay improvement ideas
Looking for ways to tune pacing, onboarding, and move clarity? See [Gameplay Improvement Recommendations](docs/gameplay_improvements.md) for actionable tweaks to sharpen session flow.

### Commands
| Command | Action |
|---------|--------|
| `!status` | View tension and Director state |
| `!vows` | View active vows with progress |
| `!save` | Save current game |
| `!load` | Load saved game |
| `resume` | Automatically offered if autosaves are present |

## Architecture

```
src/
├── nodes.py              # LangGraph workflow
├── rules_engine.py       # Dice and move resolution
├── datasworn.py          # Oracle tables and game data
├── director.py           # Pacing and tension management
│
├── prose_craft.py        # 8 prose quality systems
├── prose_enhancement.py  # 5 enhancement systems
├── narrative_systems.py  # 5 narrative systems
├── character_arcs.py     # 4 character systems
├── world_coherence.py    # 4 world tracking systems
├── specialized_scenes.py # 5 scene-type systems
├── advanced_simulation.py# 5 simulation systems
├── quest_lore.py         # 4 quest/lore systems
├── faction_environment.py# 4 world systems
├── final_systems.py      # 3 capstone systems
│
├── feedback_learning.py  # Self-improving feedback loop
└── ship_campaign_template.py # Ready-to-play scenario
```

## The Feedback Loop

Every accept/reject decision teaches the AI your preferences:

```python
from src.feedback_learning import FeedbackLearningEngine

engine = FeedbackLearningEngine("my_preferences.db")

# Record feedback
engine.record_feedback(paragraph, accepted=True, context={
    "pacing": "fast",
    "tone": "tense",
    "npcs_present": ["Torres"]
})

# See what it learned
print(engine.get_improvement_report())
```

**What gets tracked:**
- Sentence length preferences
- Forbidden words (e.g., "suddenly")
- Preferred paragraph endings
- NPC voice accuracy
- Tone execution quality

## Ship Campaign Template

A ready-to-play murder mystery scenario:

```python
from src.ship_campaign_template import initialize_ship_campaign, get_opening_scene

state = initialize_ship_campaign({})
print(get_opening_scene())
```

- 6 crew members with secrets
- 8 ship zones
- Pre-configured relationships and tensions
- One killer. Eight days to port.

## License

MIT

## Acknowledgments

- [Ironsworn: Starforged](https://www.ironswornrpg.com/) by Shawn Tomkin
- [Datasworn](https://github.com/rsek/datasworn) game data format
- Built with [LangGraph](https://github.com/langchain-ai/langgraph) and [Gradio](https://gradio.app/)
