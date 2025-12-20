import os
from pathlib import Path

# Minimal silent MP3 frame hex
SILENT_MP3_HEX = "fff344c40000000348000000004c414d45332e39392e3555555555555555"
silent_data = bytes.fromhex(SILENT_MP3_HEX)

# Define directories
ambient_dir = Path("data/assets/audio/ambient")
music_dir = Path("data/assets/music")
sfx_dir = Path("data/assets/audio/sfx")

# Create directories if they don't exist
ambient_dir.mkdir(parents=True, exist_ok=True)
music_dir.mkdir(parents=True, exist_ok=True)
sfx_dir.mkdir(parents=True, exist_ok=True)

# List of files to create
ambient_files = [
    "ambient_chatter.mp3", "glasses_clinking.mp3", "bar_music.mp3", 
    "creaking_metal.mp3", "distant_echoes.mp3", "alarm_distant.mp3", 
    "wind_howling.mp3", "alien_calls.mp3", "environmental_hum.mp3", 
    "ship_hum.mp3", "engine_rumble.mp3", "life_support.mp3", 
    "station_ambient.mp3", "crowd_distant.mp3", "announcements.mp3", 
    "void_silence.mp3", "suit_breathing.mp3", "radio_static.mp3", 
    "settlement_life.mp3", "machinery.mp3", "voices_distant.mp3"
]

music_files = [
    "exploration_calm.mp3", "exploration_tense.mp3", "tension_low.mp3", 
    "tension_high.mp3", "combat_light.mp3", "combat_intense.mp3", 
    "victory.mp3", "defeat.mp3", "mystery.mp3", "emotional.mp3"
]

sfx_files = [
    # UI
    "ui_click.mp3", "ui_hover.mp3", "ui_success.mp3", "ui_error.mp3", "ui_tab_switch.mp3",
    # Combat
    "combat_hit.mp3", "combat_miss.mp3", "weapon_fire.mp3", "weapon_reload.mp3", 
    "shield_impact.mp3", "shield_down.mp3", "explosion_small.mp3", "explosion_large.mp3",
    # Environmental/Misc
    "door_open.mp3", "door_close.mp3", "footsteps_metal.mp3", "footsteps_dirt.mp3", 
    "scanner_beep.mp3", "terminal_typing.mp3",
    # Psychological
    "ambient_ship_hum.mp3", "heartbeat_loop.mp3", "breathing_heavy.mp3", 
    "whispers_distant.mp3", "static_interference.mp3", "stinger_fear.mp3", "stinger_anger.mp3"
]

def generate_files(target_dir, files):
    print(f"Generating {len(files)} placeholders in {target_dir}...")
    for filename in files:
        with open(target_dir / filename, "wb") as f:
            f.write(silent_data)

generate_files(ambient_dir, ambient_files)
generate_files(music_dir, music_files)
generate_files(sfx_dir, sfx_files)

print("Done!")
