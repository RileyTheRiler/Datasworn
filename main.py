"""
Starforged AI Game Master - Main Entry Point.
Integrates all components and provides CLI/UI launch options.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Dict
import json
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def check_ollama() -> bool:
    """Check if Ollama is available."""
    try:
        import ollama
        client = ollama.Client()
        models = client.list()
        if models.get("models"):
            print(f"✓ Ollama is running. Available models: {[m['name'] for m in models['models']]}")
            return True
        else:
            print("⚠ Ollama is running but no models are available.")
            print("  Run: ollama pull llama3.1")
            return False
    except Exception as e:
        print(f"✗ Ollama is not available: {e}")
        print("  Please ensure Ollama is installed and running: ollama serve")
        return False


def check_datasworn() -> bool:
    """Check if Datasworn data is available."""
    data_path = Path("data/starforged/dataforged.json")
    if data_path.exists():
        from src.datasworn import load_starforged_data
        data = load_starforged_data(data_path)
        print(f"✓ Datasworn loaded: {len(data.get_all_moves())} moves, {len(data.get_all_assets())} assets")
        return True
    else:
        print(f"✗ Datasworn data not found at {data_path}")
        print("  Download from: https://github.com/rsek/dataforged")
        return False


def load_preferences(env_path: Path) -> Dict[str, str]:
    """Load simple KEY=VALUE preferences from the onboarding file."""

    if not env_path.exists():
        return {}

    prefs: Dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        prefs[key.strip()] = value.strip()

    # Apply to environment so downstream code can reuse
    for key, value in prefs.items():
        os.environ.setdefault(key, value)

    return prefs


def onboarding_wizard(env_path: Path) -> Dict[str, str]:
    """Interactive onboarding to capture user preferences.

    The wizard guides the player through selecting an LLM provider/model and
    audio preferences, then writes them to a simple ``.env`` style file so
    both the CLI and UI can reuse the configuration on the next launch.
    """

    print("\n[Onboarding Wizard]\n")
    provider = input("Choose provider (ollama/openai/none) [ollama]: ").strip() or "ollama"
    if provider not in {"ollama", "openai", "none"}:
        print("Unrecognized provider, defaulting to ollama")
        provider = "ollama"

    model = input("Preferred model (e.g., llama3.1, gpt-4o) [llama3.1]: ").strip() or "llama3.1"
    voice = input("Enable voice features? (y/n) [n]: ").strip().lower() or "n"
    enable_voice = voice.startswith("y")

    env_values = {
        "PROVIDER": provider,
        "MODEL": model,
        "VOICE_ENABLED": "true" if enable_voice else "false",
    }

    env_lines = [f"{key}={value}\n" for key, value in env_values.items()]
    env_path.write_text("".join(env_lines), encoding="utf-8")

    print(f"Saved onboarding preferences to {env_path}\n")
    return env_values


def run_demo_session():
    """Load a ready-to-play demo campaign and show a sample move."""

    from src.game_state import create_demo_state
    from src.rules_engine import action_roll

    state = create_demo_state()
    print("\n[Demo Campaign Loaded]")
    print(f"Ship: {state.world.current_location} | Character: {state.character.name}\n")

    print("Running a sample Action Roll (Edge +1 vs. base difficulty)...")
    roll = action_roll(stat=state.character.stats.edge, adds=1)
    print(roll)
    print("\nUse --cli to keep playing, or launch the UI to explore the full experience.")


def run_cli():
    """Run the game in CLI mode for testing."""
    print("\n" + "=" * 60)
    print("  STARFORGED AI GAME MASTER - CLI MODE")
    print("=" * 60 + "\n")

    from src.auto_save import AutoSaveSystem
    from src.narrator import generate_narrative, NarratorConfig

    env_file = Path(__file__).parent / ".env"
    prefs = load_preferences(env_file)
    if prefs:
        print("Loaded preferences: " + json.dumps(prefs))

    auto_save = AutoSaveSystem()
    recovery_info = auto_save.get_recovery_info()
    if recovery_info:
        print(f"\n⚠ {recovery_info}")

    # Load the latest save if available and the player wants to resume
    latest_saves = auto_save.list_saves()
    resume_state: dict | None = None
    if latest_saves:
        latest_slot = latest_saves[0].slot_name
        choice = input(f"Resume from latest save '{latest_slot}'? (y/N): ").strip().lower()
        if choice.startswith("y"):
            resume_state = auto_save.load_game(latest_slot)

    if resume_state:
        state = resume_state
        name = state.get("character", {}).get("name", "Traveler")
        print(f"\nWelcome back, {name}. Resuming your journey...\n")
    else:
        name = input("Enter your character's name: ").strip() or "Test Pilot"
        state = {
            "character": {"name": name},
            "world": {"current_location": "The Forge"},
            "session": {"turn_count": 0},
            "director": {"tension_level": 0.25, "last_pacing": "standard"},
        }
        print(f"\nWelcome, {name}. Your journey through the Forge begins...\n")

    config = NarratorConfig()
    auto_save.mark_session_start()

    def print_status(game_state: dict):
        world = game_state.get("world", {})
        session = game_state.get("session", {})
        director = game_state.get("director", {})
        tension = director.get("tension_level", 0.0) or 0.0
        try:
            tension = float(tension)
        except (TypeError, ValueError):
            tension = 0.0

        print("\n[Status]")
        print(f"Location: {world.get('current_location', 'Unknown')}")
        print(f"Turns: {session.get('turn_count', 0)}")
        print(
            f"Tension: {tension:.2f} | "
            f"Pacing: {director.get('last_pacing', 'standard')}"
        )

    while True:
        try:
            action = input("\n> What do you do? ").strip()
            if not action:
                continue
            if action.lower() in ["quit", "exit", "q"]:
                print("\nUntil next time, Ironsworn.")
                break
            if action.lower() in ["!status", "status"]:
                print_status(state)
                continue

            print("\n[Generating narrative...]\n")
            narrative = generate_narrative(
                player_input=action,
                character_name=name,
                location=state.get("world", {}).get("current_location", "the Forge"),
                config=config,
            )
            print(narrative)
            state.setdefault("session", {})
            state["session"]["turn_count"] = state["session"].get("turn_count", 0) + 1

            saved = auto_save.auto_save(state)
            if saved:
                print(f"\n💾 Auto-saved ({saved.slot_name} @ turn {saved.scene_number})")

            print("\n" + "-" * 40)

        except KeyboardInterrupt:
            print("\n\nFarewell, traveler.")
            break


def run_ui(share: bool = False, port: int = 7860):
    """Run the Gradio UI."""
    print("\n" + "=" * 60)
    print("  STARFORGED AI GAME MASTER - WEB UI")
    print("=" * 60)
    print(f"\n✓ Launching at http://localhost:{port}\n")

    from src.ui import launch_ui
    launch_ui(share=share, server_port=port)


def run_tests():
    """Run the test suite."""
    print("\n[Running tests...]\n")
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        cwd=Path(__file__).parent,
    )
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Starforged AI Game Master",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py           Launch the web UI (default)
  python main.py --cli     Run in CLI mode for testing
  python main.py --test    Run the test suite
  python main.py --check   Check system requirements
        """
    )
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--ui", action="store_true", help="Run web UI (default)")
    parser.add_argument("--demo", action="store_true", help="Load a ready-to-play demo campaign")
    parser.add_argument("--onboard", action="store_true", help="Run the onboarding wizard and save preferences")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--check", action="store_true", help="Check system requirements")
    parser.add_argument("--share", action="store_true", help="Create public Gradio share link")
    parser.add_argument("--port", type=int, default=7860, help="UI port (default: 7860)")

    args = parser.parse_args()

    print("\n🚀 Starforged AI Game Master")
    print("-" * 40)

    if args.check:
        print("\n[Checking system requirements...]\n")
        ollama_ok = check_ollama()
        datasworn_ok = check_datasworn()
        if ollama_ok and datasworn_ok:
            print("\n✓ All systems ready!")
        else:
            print("\n⚠ Some requirements are missing.")
        return

    if args.onboard:
        env_file = Path(__file__).parent / ".env"
        onboarding_wizard(env_file)

    if args.demo:
        run_demo_session()
        return

    if args.test:
        sys.exit(run_tests())

    # Default checks before running
    if not check_datasworn():
        print("\n⚠ Continuing without Datasworn data...")

    if args.cli:
        check_ollama()
        run_cli()
    else:
        check_ollama()
        run_ui(share=args.share, port=args.port)


if __name__ == "__main__":
    main()
