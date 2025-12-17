# Starforged AI Game Master

A professional-grade AI Game Master for **Ironsworn: Starforged** TTRPG, featuring 48+ interconnected narrative intelligence systems.

## Features

### 🎭 Master-Level Storytelling
- **Prose Craft Engine** — Sentence rhythm, sensory details, dialogue compression
- **Narrative Architecture** — Tension arcs, foreshadowing, thematic echoes
- **Character Systems** — Hero's Journey tracking, relationship dynamics
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
git clone https://github.com/your-username/starforged-ai-gm.git
cd starforged-ai-gm
pip install -r requirements.txt
```

**Prerequisites:**
- Python 3.10+
- **Either** Ollama (local) **or** a Gemini API key

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

# Web UI
python main.py
```

### Commands
| Command | Action |
|---------|--------|
| `!status` | View tension and Director state |
| `!vows` | View active vows with progress |
| `!save` | Save current game |
| `!load` | Load saved game |

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
