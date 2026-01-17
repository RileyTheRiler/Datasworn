import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.cli_runner import CLIRunner
from src.persistence import PersistenceLayer


class TestCLIRunnerCommands(unittest.TestCase):
    def test_rest_and_memory_commands(self):
        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            runner = CLIRunner("Nova", persistence=PersistenceLayer(db_path))

            # Seed memory
            runner.state["memory"].scene_summaries.append("Mapped the derelict halls")
            runner.state["memory"].decisions_made.append("Trusted the sentinel drone")
            runner.state["memory"].npcs_encountered["Sentinel"] = "Guarded the archive"

            rest_output = runner._handle_command("rest")
            self.assertIn("Rested and regrouped", rest_output)

            memory_output = runner._handle_command("memory")
            self.assertIn("Mapped the derelict halls", memory_output)
            self.assertIn("Trusted the sentinel drone", memory_output)

            recap_output = runner._handle_command("recap")
            self.assertIn("What happened", recap_output)
            self.assertIn("Vows:", recap_output)


if __name__ == "__main__":
    unittest.main()
