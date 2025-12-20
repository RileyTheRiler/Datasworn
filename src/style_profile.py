from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import os

class StyleProfile(BaseModel):
    """
    Defines a narrative writing style for the AI Narrator.
    """
    name: str
    description: str
    tone_directives: List[str] = Field(default_factory=list)
    sentence_patterns: List[str] = Field(default_factory=list)
    vocabulary_hints: List[str] = Field(default_factory=list)
    few_shot_examples: List[Dict[str, str]] = Field(default_factory=list)

    def to_json(self, file_path: str):
        """Save the profile to a JSON file."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=4))

    @classmethod
    def from_json(cls, file_path: str) -> "StyleProfile":
        """Load a profile from a JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Style profile not found: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls(**data)

def get_available_styles(styles_dir: str = "data/styles") -> List[str]:
    """Get a list of available style names."""
    if not os.path.exists(styles_dir):
        return []
    return [f.replace(".json", "") for f in os.listdir(styles_dir) if f.endswith(".json")]

def load_style_profile(name: str, styles_dir: str = "data/styles") -> Optional[StyleProfile]:
    """Load a style profile by name."""
    file_path = os.path.join(styles_dir, f"{name}.json")
    try:
        return StyleProfile.from_json(file_path)
    except Exception:
        return None
