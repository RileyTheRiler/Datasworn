"""
Image Generation Module using Google Generative AI.
Handles generation of location visuals and character portraits.
"""

import os
import google.generativeai as genai
from pathlib import Path
from typing import Optional

# Configure API key
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Directory for saving generated assets
ASSETS_DIR = Path("data/assets/generated")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

def generate_image(prompt: str, output_filename: str) -> Optional[str]:
    """
    Generate an image. 
    NOTE: The standard Gemini API does not yet expose Imagen 3 stably via Python SDK.
    This is a placeholder that returns None so the UI falls back to default.
    """
    print(f"Skipping Image Gen: {output_filename} (SDK limitation)")
    
    # In a real implementation with Vertex AI or stable Imagen endpoint:
    # model = genai.ImageGenerationModel("imagen-3.0-generate-001")
    # ...
    
    return None
    
    # Mocking for demo (uncomment to test file flow)
    # output_path = ASSETS_DIR / output_filename
    # import shutil
    # shutil.copy("data/assets/defaults/location_placeholder.png", output_path)
    # return f"/assets/generated/{output_filename}"

def generate_location_image(location_name: str, description: str) -> str:
    """Generate an isometric location view."""
    prompt = (
        f"Isometric digital painting of {location_name}. {description}. "
        "Style: Disco Elysium, oil painting texture, expressive brushstrokes, "
        "atmospheric lighting, sci-fi decay, intricate details, muted color palette."
    )
    filename = f"loc_{hash(location_name)}.png"
    return generate_image(prompt, filename) or "/assets/defaults/location_placeholder.png"

def generate_portrait(character_name: str, description: str) -> str:
    """Generate a character portrait."""
    prompt = (
        f"Expressionist portrait of {character_name}. {description}. "
        "Style: Disco Elysium portrait, heavy impasto, psychological, "
        "dramatic lighting, abstract background, intense gaze."
    )
    filename = f"char_{hash(character_name)}.png"
    return generate_image(prompt, filename) or "/assets/defaults/portrait_placeholder.png"
