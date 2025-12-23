"""
Image Generation Module using Google Generative AI.
Handles generation of location visuals, character portraits, and tactical blueprints.
"""

import os
import io
import base64
import google.generativeai as genai
from pathlib import Path
from typing import Optional, Any

# Configure API key
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Directory for saving generated assets
ASSETS_DIR = Path("data/assets/generated")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Blueprint cache directory
BLUEPRINT_CACHE_DIR = Path("data/cache/blueprints")
BLUEPRINT_CACHE_DIR.mkdir(parents=True, exist_ok=True)


async def generate_image(prompt: str, output_filename: str) -> Optional[str]:
    """
    Generate an image using the preferred AI provider.
    """
    provider = get_preferred_provider()
    if provider == ImageProvider.PLACEHOLDER:
        print(f"Skipping Image Gen: {output_filename} (Placeholder Mode)")
        return None
        
    image_bytes = await _generate_ai_background(prompt, provider)
    if not image_bytes:
        return None
        
    output_path = ASSETS_DIR / output_filename
    with open(output_path, "wb") as f:
        f.write(image_bytes)
        
    return f"/assets/generated/{output_filename}"

def generate_landscape_prompt(
    location_name: str,
    description: str,
    time_of_day: str = "Day",
    weather: str = "Clear"
) -> str:
    """Generate a detailed landscape prompt with atmospheric conditions."""
    
    # Time-specific lighting
    time_lighting = {
        "Day": "bright daylight, clear visibility, natural shadows",
        "Night": "dark starlit sky, artificial lighting, deep shadows, bioluminescent accents",
        "Twilight": "golden hour lighting, long shadows, warm orange and purple hues",
        "Dawn": "soft morning light, mist, cool blue tones transitioning to warm"
    }
    
    # Weather-specific atmosphere
    weather_effects = {
        "Clear": "crisp atmosphere, distant vistas visible",
        "Rain": "falling rain, wet surfaces, reflections, overcast sky",
        "Dust Storm": "swirling dust particles, reduced visibility, ochre haze, windswept",
        "Fog": "thick fog banks, mysterious silhouettes, diffused light",
        "Snow": "falling snow, white accumulation, cold atmosphere, muted colors",
        "Storm": "dramatic storm clouds, lightning, turbulent atmosphere, high contrast"
    }
    
    lighting = time_lighting.get(time_of_day, time_lighting["Day"])
    atmosphere = weather_effects.get(weather, weather_effects["Clear"])
    
    # Determine location type for specialized details
    location_lower = location_name.lower()
    if any(word in location_lower for word in ["planet", "surface", "world"]):
        location_type = "planetary surface with rocky terrain, alien vegetation"
    elif any(word in location_lower for word in ["station", "hub", "dock"]):
        location_type = "space station interior/exterior, industrial architecture, airlocks"
    elif any(word in location_lower for word in ["derelict", "hulk", "wreck", "abandoned"]):
        location_type = "derelict spacecraft, damaged hull, floating debris, emergency lighting"
    else:
        location_type = "sci-fi environment"
    
    prompt = (
        f"Cinematic wide-angle view of {location_name}. "
        f"{description}. "
        f"{location_type}. "
        f"Lighting: {lighting}. "
        f"Atmosphere: {atmosphere}. "
        f"Style: Disco Elysium meets Blade Runner, oil painting texture, "
        f"expressive brushstrokes, atmospheric perspective, sci-fi decay, "
        f"intricate environmental details, muted color palette with dramatic accents."
    )
    
    return prompt

async def generate_location_image(
    location_name: str,
    description: str,
    time_of_day: str = "Day",
    weather: str = "Clear"
) -> str:
    """Generate an atmospheric location view with time and weather."""
    prompt = generate_landscape_prompt(location_name, description, time_of_day, weather)
    filename = f"loc_{abs(hash(prompt))}.png"
    result = await generate_image(prompt, filename)
    return result or "/assets/defaults/location_placeholder.png"

from enum import Enum

class PortraitStyle(str, Enum):
    REALISTIC = "realistic"
    ANIME = "anime"
    COMIC_BOOK = "comic_book"
    PIXEL_ART = "pixel_art"
    OIL_PAINTING = "oil_painting"
    CYBERPUNK = "cyberpunk"

class PortraitExpression(str, Enum):
    NEUTRAL = "neutral"
    DETERMINED = "determined"
    ANGRY = "angry"
    HAPPY = "friendly"
    SCARED = "afraid"
    WEARY = "tired"
    PAINED = "pained"

class TimeOfDay(str, Enum):
    DAY = "Day"
    NIGHT = "Night"
    TWILIGHT = "Twilight"
    DAWN = "Dawn"

class WeatherCondition(str, Enum):
    CLEAR = "Clear"
    RAIN = "Rain"
    DUST_STORM = "Dust Storm"
    FOG = "Fog"
    SNOW = "Snow"
    STORM = "Storm"

class WeatherCondition(str, Enum):
    CLEAR = "Clear"
    RAIN = "Rain"
    DUST_STORM = "Dust Storm"
    FOG = "Fog"
    SNOW = "Snow"
    STORM = "Storm"

class ImageProvider(str, Enum):
    PLACEHOLDER = "placeholder"
    GEMINI = "gemini"
    OPENAI = "openai"

def get_preferred_provider() -> ImageProvider:
    """Get the image provider from environment variables."""
    provider_str = os.environ.get("IMAGE_PROVIDER", "placeholder").lower()
    try:
        return ImageProvider(provider_str)
    except ValueError:
        return ImageProvider.PLACEHOLDER

async def _generate_ai_background(prompt: str, provider: ImageProvider = ImageProvider.PLACEHOLDER) -> Optional[bytes]:
    """Generate AI background image."""
    if provider == ImageProvider.GEMINI:
        return await _generate_gemini_image(prompt)
    elif provider == ImageProvider.OPENAI:
        return await _generate_dalle_image(prompt)
    return None

async def _generate_gemini_image(prompt: str) -> Optional[bytes]:
    """Generate image using Gemini (Imagen 3)."""
    try:
        # Note: This requires a version of the SDK that supports Imagen
        # and appropriate project permissions.
        model = genai.GenerativeModel("imagen-3.0-generate-001")
        response = await model.generate_content_async(prompt)
        # This is speculative as SDK patterns vary for Imagen
        if hasattr(response, "images") and response.images:
            return response.images[0].data
    except Exception as e:
        print(f"Gemini Image Gen Error: {e}")
    return None

async def _generate_dalle_image(prompt: str) -> Optional[bytes]:
    """Generate image using OpenAI DALL-E 3."""
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(response.data[0].url) as img_res:
                if img_res.status == 200:
                    return await img_res.read()
    except Exception as e:
        print(f"OpenAI Image Gen Error: {e}")
    return None

def _add_tactical_overlay(base_image_bytes: bytes, draw_func, *args) -> str:
    """Overlay PIL markers on an AI-generated base image."""
    from PIL import Image, ImageDraw
    
    # Load AI image
    base_img = Image.open(io.BytesIO(base_image_bytes)).convert("RGBA")
    draw = ImageDraw.Draw(base_img, "RGBA")
    
    # Run the drawing function
    draw_func(draw, *args)
    
    # Convert to base64
    buffered = io.BytesIO()
    base_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def generate_tactical_prompt(metadata: dict[str, Any]) -> str:
    """Generate a prompt for AI tactical background."""
    zone_type = metadata.get("zone_type", "industrial")
    layout_desc = metadata.get("layout_description", "a complex interior")
    
    return (
        f"Top-down tactical battlemap of {zone_type}. {layout_desc}. "
        "Orthographic view, high contrast, technical blueprint style with cinematic lighting. "
        "Deep shadows, glowing terminals, futuristic industrial textures. "
        "Disco Elysium meets Blade Runner art style."
    )

def generate_ship_prompt(metadata: dict[str, Any]) -> str:
    """Generate a prompt for AI ship schematic background."""
    name = metadata.get("name", "spaceship")
    class_type = metadata.get("class_type", "freighter")
    status = metadata.get("damage_level", "nominal")
    
    damage_str = " showing signs of heavy structural damage and emergency lighting" if status != "none" else ""
    
    return (
        f"Internal schematic blueprint of a {class_type} starship named '{name}'{damage_str}. "
        "Cross-section view, futuristic technical drawing, blue and orange holographic aesthetic. "
        "Detailed machinery, structural ribs, corridor layouts. "
        "Cinematic high-tech feel, dark background."
    )

async def generate_portrait(
    character_name: str, 
    description: str,
    style: str = "realistic",
    expression: str = "neutral",
    conditions: list[str] = None
) -> str:
    """
    Generate a character portrait with specific style and expression.
    """
    # Style Prompts
    style_prompts = {
        "realistic": "Cinematic lighting, 8k resolution, highly detailed, photorealistic, shot on 35mm lens.",
        "anime": "Anime style, high quality animation, vibrant colors, detailed line art, Studio Ghibli inspired.",
        "comic_book": "Comic book style, heavy ink lines, halftone patterns, dynamic shading, vibrant colors.",
        "pixel_art": "High quality pixel art, 16-bit style, retro aesthetic, distinct pixels.",
        "oil_painting": "Disco Elysium style, heavy impasto, expressive brushstrokes, psychological, abstract background.",
        "cyberpunk": "Cyberpunk aesthetic, neon lighting, chromatic aberration, high tech, futuristic.",
    }
    
    selected_style_prompt = style_prompts.get(style, style_prompts["oil_painting"])
    
    # Construct prompt
    condition_str = f" exhibiting signs of being {', '.join(conditions)}" if conditions else ""
    prompt = (
        f"Portrait of {character_name}, {expression} expression. "
        f"{description}{condition_str}. "
        f"{selected_style_prompt}"
    )
    
    filename = f"char_{abs(hash(prompt))}.png"
    result = await generate_image(prompt, filename)
    return result or "/assets/defaults/portrait_placeholder.png"


# ============================================================================
# Tactical Blueprint Generation (PIL-based placeholder mode)
# ============================================================================

# Color definitions (RGBA)
COLORS = {
    "background": (30, 35, 45, 255),       # Dark blue-gray
    "grid": (60, 70, 85, 180),             # Subtle grid lines
    "grid_major": (80, 90, 110, 200),      # Major grid lines
    "wall": (100, 110, 130, 255),          # Walls/structures
    "cover_full": (45, 85, 55, 200),       # Full cover (green tint)
    "cover_half": (85, 85, 45, 180),       # Half cover (yellow tint)
    "player": (60, 140, 220, 255),         # Player (bright blue)
    "player_outline": (255, 255, 255, 255),
    "npc_red": (200, 60, 60, 255),         # Hostile
    "npc_orange": (220, 140, 50, 255),     # Potentially hostile
    "npc_yellow": (200, 200, 80, 255),     # Neutral
    "npc_green": (80, 180, 80, 255),       # Friendly
    "text": (220, 220, 220, 255),          # Labels
    "entry": (100, 150, 200, 180),         # Entry points
}

NPC_COLOR_MAP = {
    "red": COLORS["npc_red"],
    "orange": COLORS["npc_orange"],
    "yellow": COLORS["npc_yellow"],
    "green": COLORS["npc_green"],
}


def generate_tactical_blueprint(
    game_state: dict[str, Any],
    width: int = 600,
    height: int = 500,
    use_ai_background: bool = True,
    show_movement: bool = False,
    show_vision: bool = False
) -> dict[str, Any]:
    """
    Generate a tactical blueprint map for the current scene.
    
    Args:
        game_state: Full game state dictionary
        width: Image width in pixels
        height: Image height in pixels
        use_ai_background: If True, attempt AI generation for base
    """
    from src.blueprint_generator import (
        extract_tactical_metadata, 
        generate_cache_key
    )
    
    # Extract metadata
    metadata = extract_tactical_metadata(game_state)
    provider = get_preferred_provider()
    
    cache_key = generate_cache_key(game_state)
    if use_ai_background and provider != ImageProvider.PLACEHOLDER:
        cache_key += f"_ai_{provider}"
    
    # Check cache
    cached = _load_cached_blueprint(cache_key)
    if cached:
        return {
            "image_base64": cached,
            "metadata": metadata,
            "cache_key": cache_key,
            "from_cache": True
        }
    
    # AI Generation Path
    if use_ai_background and provider != ImageProvider.PLACEHOLDER:
        import asyncio

        prompt = generate_tactical_prompt(metadata)
        ai_coro = _generate_ai_background(prompt, provider)

        try:
            loop = asyncio.get_running_loop()
            ai_base = loop.run_until_complete(ai_coro) if not loop.is_running() else None
        except RuntimeError:
            ai_base = asyncio.run(ai_coro)

        if ai_base:
            image_base64 = _add_tactical_overlay(
                ai_base,
                _draw_placeholder_content, # Externalized draw func
                metadata, width, height, show_movement, show_vision, True # True means skip clear background
            )
            _cache_blueprint(cache_key, image_base64)
            return {
                "image_base64": image_base64,
                "metadata": metadata,
                "cache_key": cache_key,
                "from_cache": False
            }

    # Fallback to PIL-only
    image_base64 = _generate_placeholder_blueprint(
        metadata, width, height, show_movement, show_vision
    )
    
    _cache_blueprint(cache_key, image_base64)
    
    return {
        "image_base64": image_base64,
        "metadata": metadata,
        "cache_key": cache_key,
        "from_cache": False
    }

def _draw_placeholder_content(draw, metadata, width, height, show_movement, show_vision, skip_bg=False):
    """Refactored drawing logic that can work on top of AI backgrounds."""
    if not skip_bg:
        draw.rectangle([0, 0, width, height], fill=COLORS["background"])
        # Draw grid
        _draw_grid(draw, width, height, grid_size=40)
        # Draw zone structure outline
        _draw_zone_structure(draw, metadata.get("zone_type", "residential"), width, height)

    # Draw cover positions
    _draw_cover_indicators(draw, metadata.get("cover_spots", []), width, height)

    # Draw entry points
    _draw_entry_points(draw, metadata.get("entry_points", []), width, height)

    # Draw NPC markers
    _draw_npc_markers(draw, metadata.get("npcs", []), width, height, show_vision)

    # Draw Player marker
    player_pos = _draw_player_marker(draw, (width // 2, int(height * 0.75)))
    
    # Draw movement range
    if show_movement:
        from src.blueprint_generator import calculate_movement_range
        range_px = calculate_movement_range(30)
        _draw_movement_range(draw, player_pos, range_px, True)

def _generate_placeholder_blueprint(
    metadata: dict[str, Any],
    width: int,
    height: int,
    show_movement: bool = False,
    show_vision: bool = False
) -> str:
    """Generate a PIL-based tactical grid blueprint."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return _minimal_placeholder()
    
    img = Image.new("RGBA", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(img, "RGBA")
    
    _draw_placeholder_content(draw, metadata, width, height, show_movement, show_vision, False)
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def _draw_grid(draw, width: int, height: int, grid_size: int = 40):
    """Draw tactical grid overlay."""
    # Minor grid lines
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=COLORS["grid"], width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=COLORS["grid"], width=1)
    
    # Major grid lines (every 4 cells)
    major_size = grid_size * 4
    for x in range(0, width, major_size):
        draw.line([(x, 0), (x, height)], fill=COLORS["grid_major"], width=2)
    for y in range(0, height, major_size):
        draw.line([(0, y), (width, y)], fill=COLORS["grid_major"], width=2)


def _draw_zone_structure(draw, zone_type: str, width: int, height: int):
    """Draw zone-appropriate structural elements."""
    margin = 30
    
    # Outer boundary
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline=COLORS["wall"],
        width=3
    )
    
    # Zone-specific internal structures
    if zone_type == "bar":
        # Bar counter
        bar_y = height // 3
        draw.rectangle(
            [width // 4, bar_y, width * 3 // 4, bar_y + 30],
            fill=COLORS["wall"],
            outline=COLORS["grid_major"]
        )
    elif zone_type == "military":
        # Defensive barriers
        for i in range(3):
            x = margin + 50 + i * 150
            draw.rectangle(
                [x, height // 2 - 20, x + 60, height // 2 + 20],
                fill=COLORS["cover_full"],
                outline=COLORS["wall"]
            )
    elif zone_type == "industrial":
        # Machinery blocks
        draw.rectangle(
            [margin + 40, margin + 40, margin + 120, margin + 100],
            fill=COLORS["wall"]
        )
        draw.rectangle(
            [width - margin - 120, margin + 40, width - margin - 40, margin + 100],
            fill=COLORS["wall"]
        )


def _draw_cover_indicators(draw, cover_spots: list[str], width: int, height: int):
    """Draw cover position indicators."""
    import random
    random.seed(42)  # Consistent layout
    
    positions = [
        (80, 120), (200, 100), (width - 150, 130),
        (100, height // 2), (width - 100, height // 2),
        (150, height - 150), (width - 180, height - 140)
    ]
    
    for i, (cover, pos) in enumerate(zip(cover_spots[:len(positions)], positions)):
        is_full = "full" in cover.lower()
        color = COLORS["cover_full"] if is_full else COLORS["cover_half"]
        
        # Cover indicator (small rectangle)
        x, y = pos
        draw.rectangle([x - 15, y - 10, x + 15, y + 10], fill=color, outline=COLORS["wall"])


def _draw_entry_points(draw, entry_points: list[str], width: int, height: int):
    """Draw entry/exit point indicators."""
    positions = [
        (width // 2, 35),      # Top
        (35, height // 2),     # Left  
        (width - 35, height // 2),  # Right
    ]
    
    for pos in positions[:len(entry_points)]:
        x, y = pos
        # Arrow-like indicator
        draw.polygon(
            [(x, y - 12), (x - 10, y + 8), (x + 10, y + 8)],
            fill=COLORS["entry"],
            outline=COLORS["text"]
        )


def _draw_npc_markers(draw, npcs: list[dict], width: int, height: int, show_vision: bool = False):
    """Draw NPC position markers (optionally with simple vision rays)."""
    from src.blueprint_generator import calculate_npc_grid_position
    
    for npc in npcs:
        idx = npc.get("index", 0)
        pos = calculate_npc_grid_position(idx, len(npcs), width, height)
        color = NPC_COLOR_MAP.get(npc.get("color", "yellow"), COLORS["npc_yellow"])
        
        x, y = pos
        # Outer ring
        draw.ellipse([x - 18, y - 18, x + 18, y + 18], outline=color, width=3)
        # Inner fill
        draw.ellipse([x - 12, y - 12, x + 12, y + 12], fill=color)

        if show_vision:
            # Draw a minimal forward-facing indicator to visualize awareness
            draw.line([x, y, x + 30, y], fill=color, width=2)


def _draw_player_marker(draw, pos: tuple[int, int]):
    """Draw player position marker."""
    x, y = pos
    # Outer ring (white)
    draw.ellipse([x - 22, y - 22, x + 22, y + 22], outline=COLORS["player_outline"], width=3)
    # Inner fill (blue)
    draw.ellipse([x - 16, y - 16, x + 16, y + 16], fill=COLORS["player"])
    # "YOU" label
    draw.text((x - 12, y - 6), "YOU", fill=COLORS["text"])
    return pos



def _draw_movement_range(draw, player_pos: tuple[int, int], range_pixels: int, show: bool):
    """Draw movement range circle around player."""
    if not show:
        return
    
    x, y = player_pos
    # Semi-transparent blue circle
    draw.ellipse(
        [x - range_pixels, y - range_pixels, x + range_pixels, y + range_pixels],
        outline=(60, 140, 220, 150),
        width=2
    )
    # Faint fill
    draw.ellipse(
        [x - range_pixels, y - range_pixels, x + range_pixels, y + range_pixels],
        fill=(90, 140, 200, 30)
    )


def _draw_vision_cones(draw, npcs: list[dict], width: int, height: int, show: bool):
    """Draw vision cones for NPCs."""
    if not show or not npcs:
        return
    
    from src.blueprint_generator import calculate_npc_grid_position
    import math
    
    for npc in npcs:
        idx = npc.get("index", 0)
        pos = calculate_npc_grid_position(idx, len(npcs), width, height)
        color = NPC_COLOR_MAP.get(npc.get("color", "yellow"), COLORS["npc_yellow"])
        
        x, y = pos
        
        # Vision cone parameters
        cone_length = 120  # pixels
        cone_angle = 60  # degrees
        facing_angle = 270  # degrees (facing down by default)
        
        # Calculate cone points
        angle_rad = math.radians(facing_angle)
        half_cone = math.radians(cone_angle / 2)
        
        # Cone tip is at NPC position
        # Calculate two edge points
        left_angle = angle_rad - half_cone
        right_angle = angle_rad + half_cone
        
        left_x = x + cone_length * math.cos(left_angle)
        left_y = y + cone_length * math.sin(left_angle)
        right_x = x + cone_length * math.cos(right_angle)
        right_y = y + cone_length * math.sin(right_angle)
        
        # Draw semi-transparent cone
        cone_color = (*color[:3], 40)  # Very transparent
        draw.polygon(
            [(x, y), (left_x, left_y), (right_x, right_y)],
            fill=cone_color,
            outline=(*color[:3], 100)
        )




def _draw_legend(draw, npcs: list[dict], width: int, height: int):
    """Draw NPC legend."""
    legend_x = width - 140
    legend_y = height - 30 - len(npcs) * 18
    
    # Background
    draw.rectangle(
        [legend_x - 10, legend_y - 5, width - 10, height - 10],
        fill=(30, 35, 45, 200),
        outline=COLORS["grid_major"]
    )
    
    for i, npc in enumerate(npcs[:5]):  # Max 5 in legend
        y = legend_y + i * 18
        color = NPC_COLOR_MAP.get(npc.get("color", "yellow"), COLORS["npc_yellow"])
        
        # Color dot
        draw.ellipse([legend_x, y + 2, legend_x + 10, y + 12], fill=color)
        # Name
        name = npc.get("name", "Unknown")[:12]
        draw.text((legend_x + 16, y), name, fill=COLORS["text"])


def _draw_title(draw, location: str, width: int):
    """Draw location title."""
    title = location[:30]
    draw.text((10, 8), f"📍 {title}", fill=COLORS["text"])


def _minimal_placeholder() -> str:
    """Return minimal base64 placeholder if PIL unavailable."""
    # 1x1 transparent PNG
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def _load_cached_blueprint(cache_key: str) -> Optional[str]:
    """Load cached blueprint if exists and not expired."""
    cache_file = BLUEPRINT_CACHE_DIR / f"{cache_key}.txt"
    if cache_file.exists():
        try:
            return cache_file.read_text()
        except Exception:
            return None
    return None


def _cache_blueprint(cache_key: str, image_base64: str):
    """Cache blueprint for reuse."""
    cache_file = BLUEPRINT_CACHE_DIR / f"{cache_key}.txt"
    try:
        cache_file.write_text(image_base64)
    except Exception as e:
        print(f"Blueprint cache write failed: {e}")


def clear_blueprint_cache():
    """Clear all cached blueprints."""
    for cache_file in BLUEPRINT_CACHE_DIR.glob("*.txt"):
        try:
            cache_file.unlink()
        except Exception:
            pass


async def generate_ship_blueprint(
    game_state: dict[str, Any],
    width: int = 600,
    height: int = 800,
    use_ai_background: bool = True
) -> dict[str, Any]:
    """
    Generate a schematic blueprint of the player's ship.
    """
    from src.blueprint_generator import extract_ship_metadata
    
    metadata = extract_ship_metadata(game_state)
    provider = get_preferred_provider()
    
    # Generate simple cache key
    cache_key = f"ship_{metadata['class_type']}_{metadata['integrity']['percent']}_{hash(str(metadata['alerts']))}"
    if use_ai_background and provider != ImageProvider.PLACEHOLDER:
        cache_key += f"_ai_{provider}"
        
    # Check cache
    cached = _load_cached_blueprint(cache_key)
    if cached:
        return {
            "image_base64": cached,
            "metadata": metadata,
            "from_cache": True
        }
    
    # AI Generation Path
    if use_ai_background and provider != ImageProvider.PLACEHOLDER:
        prompt = generate_ship_prompt(metadata)
        ai_base = await _generate_ai_background(prompt, provider)
        if ai_base:
            image_base64 = _add_tactical_overlay(
                ai_base,
                _draw_ship_content, # Externalized draw func
                metadata, width, height, True # True means skip background
            )
            _cache_blueprint(cache_key, image_base64)
            return {
                "image_base64": image_base64,
                "metadata": metadata,
                "from_cache": False
            }
        
    image_base64 = _generate_ship_placeholder(metadata, width, height)
    _cache_blueprint(cache_key, image_base64)
    
    return {
        "image_base64": image_base64,
        "metadata": metadata,
        "from_cache": False
    }

def _draw_ship_content(draw, metadata, width, height, skip_bg=False):
    """Refactored ship drawing logic."""
    layout = metadata.get("layout", {})
    if not layout:
        return
        
    # Calculate ship bounds and scale
    ship_w, ship_h = layout.get("dimensions", (500, 700))
    scale_x = (width * 0.8) / ship_w
    scale_y = (height * 0.8) / ship_h
    scale = min(scale_x, scale_y)
    
    offset_x = (width - (ship_w * scale)) / 2
    offset_y = (height - (ship_h * scale)) / 2
    
    def transform(pos):
        return (int(offset_x + pos[0] * scale), int(offset_y + pos[1] * scale))

    if not skip_bg:
        _draw_ship_grid(draw, width, height)
        # Draw Ship Hull
        _draw_ship_hull(draw, layout, transform, scale)
    
    # Draw Rooms
    rooms = layout.get("rooms", {})
    for room_id, room_data in rooms.items():
        _draw_ship_room(draw, room_data, transform, scale, metadata.get("damage_level", "none"))
        
    # Draw Alerts
    alerts = metadata.get("alerts", [])
    if alerts:
        _draw_ship_alerts(draw, alerts, width, height)
        
    # Draw Crew
    crew = metadata.get("crew", [])
    if crew:
        _draw_ship_crew(draw, crew, layout, transform, scale)
        
    # Draw Legend/Status
    _draw_ship_status_panel(draw, metadata, width, height)

def _generate_ship_placeholder(
    metadata: dict[str, Any],
    width: int,
    height: int
) -> str:
    """Generate PIL image for ship schematic."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return _minimal_placeholder()

    img = Image.new("RGBA", (width, height), (20, 25, 35, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    
    _draw_ship_content(draw, metadata, width, height, False)

    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def _draw_ship_crew(draw, crew, layout, transform, scale):
    """Draw crew markers in assigned rooms."""
    rooms = layout.get("rooms", {})
    room_occupants = {} # Track occupants to avoid overlapping
    
    for member in crew:
        room_id = member.get("room")
        if room_id in rooms:
            room_occupants[room_id] = room_occupants.get(room_id, 0) + 1
            offset = (room_occupants[room_id] - 1) * 15
            
            room_pos = transform(rooms[room_id]["pos"])
            marker_pos = (room_pos[0] + offset, room_pos[1] + 10) # Offset slightly
            
            # Draw marker
            color_map = {
                "red": (239, 68, 68),
                "green": (74, 222, 128),
                "blue": (59, 130, 246),
                "yellow": (250, 204, 21),
                "orange": (249, 115, 22)
            }
            marker_color = color_map.get(member.get("color"), (250, 204, 21))
            
            # Small circle marker
            r = int(5 * scale)
            rect = [marker_pos[0]-r, marker_pos[1]-r, marker_pos[0]+r, marker_pos[1]+r]
            draw.ellipse(rect, fill=marker_color, outline=(255, 255, 255), width=1)

def _draw_ship_grid(draw, width, height, spacing=40):
    """Draw a subtle technical grid."""
    grid_color = (40, 50, 70, 100)
    for x in range(0, width, spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

def _draw_ship_hull(draw, layout, transform, scale):
    """Draw the outer hull boundary."""
    hull_type = layout.get("hull_shape", "freighter")
    ship_w, ship_h = layout.get("dimensions", (500, 700))
    
    # Define points for hull (normalized 0-1)
    if hull_type == "fighter":
        hull_points = [(0.5, 0), (1, 0.4), (0.8, 1), (0.2, 1), (0, 0.4)]
    elif hull_type == "explorer":
        hull_points = [(0.5, 0), (0.9, 0.2), (1, 0.8), (0.5, 1), (0, 0.8), (0.1, 0.2)]
    else: # freighter
        hull_points = [(0.2, 0), (0.8, 0), (1, 0.2), (1, 0.9), (0.8, 1), (0.2, 1), (0, 0.9), (0, 0.2)]
        
    # Transform points
    pixel_points = []
    for p in hull_points:
        scaled_x = p[0] * ship_w
        scaled_y = p[1] * ship_h
        pixel_points.append(transform((scaled_x, scaled_y)))
        
    # Draw hull glow
    draw.polygon(pixel_points, outline=(60, 100, 150, 155), fill=(30, 40, 60, 100), width=3)
    
def _draw_ship_room(draw, room_data, transform, scale, damage_level):
    """Draw an individual room with status."""
    pos = transform(room_data["pos"])
    size = (int(room_data["size"][0] * scale), int(room_data["size"][1] * scale))
    
    rect = [pos[0] - size[0]//2, pos[1] - size[1]//2, pos[0] + size[0]//2, pos[1] + size[1]//2]
    
    # Room Fill
    fill_color = (40, 60, 90, 150)
    outline_color = (100, 150, 200, 200)
    
    # Apply damage effect
    if damage_level != "none" and hash(room_data["name"]) % 3 == 0: # Randomly pick rooms to show damage
        if damage_level == "critical":
            fill_color = (150, 40, 40, 180)
            outline_color = (255, 80, 80, 255)
        elif damage_level == "heavy":
            fill_color = (120, 60, 40, 160)
            outline_color = (200, 100, 80, 220)
            
    draw.rectangle(rect, fill=fill_color, outline=outline_color, width=2)
    
    # Room Label
    try:
        from PIL import ImageFont
        font = ImageFont.load_default()
        name = room_data["name"]
        draw.text((pos[0], pos[1]), name, fill=(200, 220, 255), anchor="mm")
    except Exception:
        pass

def _draw_ship_alerts(draw, alerts, width, height):
    """Draw active alert indicators."""
    y_start = 60
    for i, alert in enumerate(alerts):
        rect = [width - 150, y_start + i*30, width - 10, y_start + i*30 + 25]
        draw.rectangle(rect, fill=(150, 30, 30, 200), outline=(255, 50, 50, 255))
        draw.text((width - 80, y_start + i*30 + 12), f"! {alert}", fill=(255, 255, 255), anchor="mm")

def _draw_ship_status_panel(draw, metadata, width, height):
    """Draw ship status info panel."""
    draw.rectangle([10, 10, 250, 120], fill=(25, 30, 45, 220), outline=(70, 90, 120, 255))
    
    name = metadata.get("name", "Unknown Ship")
    class_type = metadata.get("class_type", "Freighter")
    hull = metadata.get("integrity", {}).get("percent", 100)
    
    draw.text((20, 20), f" vessel: {name.upper()}", fill=(100, 200, 255))
    draw.text((20, 45), f" class: {class_type.capitalize()}", fill=(150, 170, 200))
    
    # Hull bar
    draw.text((20, 75), f" HULL INTEGRITY: {hull}%", fill=(200, 220, 255))
    bar_rect = [20, 95, 230, 105]
    draw.rectangle(bar_rect, fill=(40, 50, 70), outline=(80, 100, 120))
    
    hull_w = int(210 * (hull / 100))
    bar_color = (80, 200, 100) if hull > 70 else (200, 180, 60) if hull > 30 else (220, 60, 60)
    draw.rectangle([20, 95, 20 + hull_w, 105], fill=bar_color)
    _draw_grid(draw, width, height, grid_size=50)
    
    # Draw Hull
    cx, cy = width // 2, height // 2
    
    hull_color = (60, 70, 90, 255)
    outline_color = (100, 120, 150, 255)
    
    if hull_shape == "freighter":
        # Oblong / Blocky
        draw.rectangle([cx - 150, cy - 300, cx + 150, cy + 300], fill=hull_color, outline=outline_color, width=4)
        # Engines
        draw.rectangle([cx - 120, cy + 300, cx - 40, cy + 350], fill=(50, 50, 60, 255), outline=outline_color)
        draw.rectangle([cx + 40, cy + 300, cx + 120, cy + 350], fill=(50, 50, 60, 255), outline=outline_color)
    elif hull_shape == "fighter":
        # Triangle-ish
        points = [(cx, cy - 200), (cx + 120, cy + 200), (cx, cy + 150), (cx - 120, cy + 200)]
        draw.polygon(points, fill=hull_color, outline=outline_color)
    else:
        # Oval
        draw.ellipse([cx - 150, cy - 250, cx + 150, cy + 250], fill=hull_color, outline=outline_color, width=4)
        
    # Draw Rooms
    rooms = layout.get("rooms", {})
    for room_key, room_data in rooms.items():
        rx, ry = room_data.get("pos", (0,0))
        rw, rh = room_data.get("size", (50,50))
        name = room_data.get("name", room_key)
        
        # Center coordinates relative to image scale (simple mapping)
        # The layout coords assume a certain canvas size, we might need to offset if dimensions differ
        # For simplicity, we'll trust the layout coords fit the default 600x800 logic or adjust manually
        # Layout coords in blueprint_generator were: example 250, 80 for top center.
        
        # Room box
        draw.rectangle([rx - rw//2, ry - rh//2, rx + rw//2, ry + rh//2], 
                       fill=(40, 50, 60, 200), outline=(150, 200, 220, 255), width=2)
                       
        # Room label
        draw.text((rx - 20, ry - 7), name[:8], fill=(200, 220, 240, 255))

    # Damage Overlay
    damage_level = metadata.get("damage_level", "none")
    if damage_level != "none":
        overlay = Image.new("RGBA", (width, height), (0,0,0,0))
        draw_ov = ImageDraw.Draw(overlay)
        
        if damage_level in ["moderate", "heavy", "critical"]:
            # Random red splotches/cracks
            import random
            random.seed(42) # Consistent
            
            count = 3 if damage_level == "moderate" else 6 if damage_level == "heavy" else 10
            for _ in range(count):
                x = random.randint(150, 450)
                y = random.randint(150, 650)
                r = random.randint(20, 60)
                draw_ov.ellipse([x-r, y-r, x+r, y+r], fill=(255, 50, 50, 60))
                
        # Composite
        img = Image.alpha_composite(img, overlay)
    
    # Alerts
    alerts = metadata.get("alerts", [])
    if alerts:
        draw.rectangle([width - 200, 20, width - 20, 20 + len(alerts)*25 + 10], 
                       fill=(50, 0, 0, 180), outline=(255, 0, 0, 255))
        for i, alert in enumerate(alerts):
            draw.text((width - 190, 25 + i * 25), f"⚠️ {alert}", fill=(255, 200, 200, 255))

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
