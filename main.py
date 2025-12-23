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


def check_llm_provider() -> bool:
    """Check if the configured LLM provider is available."""
    from src.narrator import NarratorConfig, check_provider_availability, get_llm_provider_for_config

    try:
        config = NarratorConfig()
    except ValueError as exc:
        print(f"✗ {exc}")
        return False

    try:
        provider = get_llm_provider_for_config(config)
        available, status_message = check_provider_availability(config, provider)
    except Exception as exc:  # pragma: no cover - defensive guard for onboarding
        print(f"✗ Unable to initialize provider: {exc}")
        return False

    print(status_message)
    return available


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
    allowed_providers = {"ollama", "gemini"}
    default_provider = os.environ.get("LLM_PROVIDER", "ollama").lower()

    while True:
        provider_prompt = f"Choose provider (ollama/gemini) [{default_provider}]: "
        provider = input(provider_prompt).strip().lower() or default_provider
        if provider not in allowed_providers:
            print("✗ Unsupported provider. Please choose 'ollama' or 'gemini'.")
            continue

        default_model = os.environ.get("GEMINI_MODEL" if provider == "gemini" else "OLLAMA_MODEL", "")
        default_model = default_model or ("gemini-2.0-flash" if provider == "gemini" else "llama3.1")
        model_prompt = "Gemini model" if provider == "gemini" else "Ollama model"
        model = input(f"Preferred {model_prompt} [{default_model}]: ").strip() or default_model
        voice = input("Enable voice features? (y/n) [n]: ").strip().lower() or "n"
        enable_voice = voice.startswith("y")

        from src.narrator import NarratorConfig, check_provider_availability, get_llm_provider_for_config

        try:
            config = NarratorConfig(backend=provider, model=model)
        except ValueError as exc:
            print(f"✗ {exc}")
            continue

        provider_instance = get_llm_provider_for_config(config)
        available, status_message = check_provider_availability(config, provider_instance)
        print(status_message)

        if not available:
            retry = input("Provider check failed. Try again? (y/N): ").strip().lower()
            if retry.startswith("y"):
                continue
            print("⚠ Preferences were not saved because the provider is unavailable.")
            return {}

        env_values = {"LLM_PROVIDER": config.backend, "VOICE_ENABLED": "true" if enable_voice else "false"}
        if config.backend == "gemini":
            env_values["GEMINI_MODEL"] = config.model
        else:
            env_values["OLLAMA_MODEL"] = config.model

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


def run_tactical_debug(dump_rationale: bool = False) -> list[str]:
    """Run a lightweight combat AI simulation and optionally dump rationales."""

    from src.combat.encounter_manager import (
        CombatantState,
        EncounterManager,
        EncounterState,
        summarize_decisions,
    )

    manager = EncounterManager()
    enemies = [
        CombatantState(id="e1", name="Raider", health=0.8, threat=0.7, position=(5, 5)),
        CombatantState(id="e2", name="Sharpshooter", health=1.0, threat=0.9, position=(8, 2), in_cover=True, cover_quality=0.7),
    ]
    party = [
        CombatantState(
            id="p1",
            name="Vanguard",
            health=0.55,
            ammo=0.6,
            threat=0.6,
            position=(0, 0),
            cover_quality=0.1,
            allies_nearby=1,
        ),
        CombatantState(
            id="p2",
            name="Sniper",
            health=0.9,
            ammo=0.9,
            threat=0.4,
            position=(1, 2),
            in_cover=True,
            cover_quality=0.8,
            allies_nearby=1,
        ),
    ]

    encounter = EncounterState(
        enemies=enemies,
        party=party,
        map_control=0.4,
        cover_density=0.6,
        objective_pressure=0.7,
    )

    decisions = [manager.evaluate_turn(actor, encounter, dump_debug=dump_rationale) for actor in party]
    print("\n[Tactical AI Demo]")
    print(summarize_decisions(decisions))

    if dump_rationale:
        print("\n[Per-turn rationale]")
        for line in manager.debug_log():
            print(f" • {line}")

    return manager.debug_log()


def run_cli():
    """Run the game in CLI mode for testing."""
    print("\n" + "=" * 60)
    print("  STARFORGED AI GAME MASTER - CLI MODE")
    print("=" * 60 + "\n")
    from src.cli_runner import bootstrap_cli

    name = input("Enter your character's name: ").strip() or "Test Pilot"
    cli = bootstrap_cli(name)

    tab_completion_enabled = False
    try:
        import readline

        def _tab_complete(text: str, state_idx: int) -> str | None:
            commands = [
                "!status",
                "!assets",
                "!vows",
                "!help",
                "!help moves",
                "!oracle ",
            ]
            if cli.data:
                commands.extend([f"!oracle {key}" for key in sorted(cli.data.get_oracle_keys())])

            matches = [cmd for cmd in commands if cmd.startswith(text)]
            return matches[state_idx] if state_idx < len(matches) else None

        readline.set_completer(_tab_complete)
        readline.parse_and_bind("tab: complete")
        tab_completion_enabled = True
    except Exception:
        tab_completion_enabled = False

    help_text = (
        "\nCommands: !status, !assets, !vows, !oracle <name>, !help moves.\n"
        "Type actions and the rules engine will pick an Ironsworn move, roll it, and update your progress.\n"
    )
    if tab_completion_enabled:
        help_text += "Tab-completion enabled for commands and oracle paths.\n"
    print(help_text)

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
        name = state.get("character", {}).get("name", name)
        print(f"\nWelcome back, {name}. Resuming your journey...\n")
    else:
        state = {
            "character": {"name": name},
            "world": {"current_location": "The Forge"},
            "session": {"turn_count": 0},
            "director": {"tension_level": 0.25, "last_pacing": "standard"},
        }
        print(f"\nWelcome, {name}. Your journey through the Forge begins...\n")

    state.setdefault("world", {}).setdefault("current_location", "The Forge")
    state.setdefault("session", {}).setdefault("turn_count", 0)

    config = NarratorConfig()
    auto_save.mark_session_start()

    while True:
        try:
            action = input("\n> What do you do? ").strip()
            if not action:
                continue
            if action.lower() in ["quit", "exit", "q"]:
                print("\nUntil next time, Ironsworn.")
                break
            normalized_action = action
            lower_action = action.lower()
            if lower_action in {"status", "assets", "vows", "help"} or lower_action.startswith("help"):
                normalized_action = f"!{lower_action}"
            elif lower_action.startswith("oracle") and not lower_action.startswith("!"):
                normalized_action = f"!{action}"

            is_command = normalized_action.startswith("!")
            response = cli.handle_input(normalized_action)
            if response:
                print(f"\n{response}\n")
            if is_command:
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
    parser.add_argument("--tactical-debug", action="store_true", help="Run a tactical AI simulation")
    parser.add_argument(
        "--dump-ai-rationale",
        action="store_true",
        help="Print per-turn tactical decision rationales",
    )
    parser.add_argument("--port", type=int, default=7860, help="UI port (default: 7860)")

    args = parser.parse_args()

    env_file = Path(__file__).parent / ".env"
    prefs = load_preferences(env_file)
    if prefs:
        print("Loaded preferences: " + json.dumps(prefs))

    print("\n🚀 Starforged AI Game Master")
    print("-" * 40)

    if args.check:
        print("\n[Checking system requirements...]\n")
        provider_ok = check_llm_provider()
        datasworn_ok = check_datasworn()
        if provider_ok and datasworn_ok:
            print("\n✓ All systems ready!")
        else:
            print("\n⚠ Some requirements are missing.")
        return

    if args.onboard:
        onboarding_wizard(env_file)

    if args.demo:
        run_demo_session()
        return

    if args.tactical_debug:
        run_tactical_debug(args.dump_ai_rationale)
        return

    if args.test:
        sys.exit(run_tests())

    # Default checks before running
    if not check_datasworn():
        print("\n⚠ Continuing without Datasworn data...")

    if args.cli:
        provider_ok = check_llm_provider()
        if not provider_ok:
            print("\n✗ LLM provider unavailable. Run the onboarding wizard to reconfigure.")
            return
        run_cli()
    else:
        provider_ok = check_llm_provider()
        if not provider_ok:
            print("\n✗ LLM provider unavailable. Run the onboarding wizard to reconfigure.")
            return
        run_ui(share=args.share, port=args.port)


if __name__ == "__main__":
    main()
