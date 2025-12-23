"""
Starforged AI Game Master - Main Entry Point.
Integrates all components and provides CLI/UI launch options.
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

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


def run_cli():
    """Run the game in CLI mode for testing."""
    print("\n" + "=" * 60)
    print("  STARFORGED AI GAME MASTER - CLI MODE")
    print("=" * 60 + "\n")
    from src.cli_runner import bootstrap_cli

    name = input("Enter your character's name: ").strip() or "Test Pilot"
    cli = bootstrap_cli(name)

    print(
        "\nCommands: !status, !vows, !help.  Type actions and the rules engine will\n"
        "pick an Ironsworn move, roll it, and update your progress.\n",
    )

    while True:
        try:
            action = input("\n> What do you do? ").strip()
            if not action:
                continue
            if action.lower() in ["quit", "exit", "q"]:
                print("\nUntil next time, Ironsworn.")
                break

            response = cli.handle_input(action)
            if response:
                print(f"\n{response}\n")

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
