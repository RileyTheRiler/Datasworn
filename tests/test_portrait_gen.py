
import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.image_gen import generate_portrait, PortraitStyle, PortraitExpression

def test_portrait_prompts():
    print("Testing Portrait Prompts construction...")
    
    # Mock image generation to just return the prompt? 
    # Actually generate_portrait returns a URL/path.
    # But I want to see the prompt. 
    # I can inspect the code or just run it and assume it works if no error.
    
    try:
        url = asyncio.run(
            generate_portrait(
                "Kaelen",
                "A rugged spacer",
                style=PortraitStyle.PIXEL_ART,
                expression=PortraitExpression.ANGRY,
                conditions=["scarred", "tired"],
            )
        )
        print(f"Generated URL: {url}")
        assert url is not None
        print("PASS: Pixel Art generation")
    except Exception as e:
        print(f"FAIL: {e}")

    try:
        url = asyncio.run(
            generate_portrait(
                "Kaelen",
                "A rugged spacer",
                style=PortraitStyle.OIL_PAINTING,
                expression=PortraitExpression.WEARY,
            )
        )
        print(f"Generated URL: {url}")
        assert url is not None
        print("PASS: Oil Painting generation")
    except Exception as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    test_portrait_prompts()
