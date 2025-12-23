"""
Generate silent MP3 placeholder files for sound effects.
This creates minimal silent audio files so the browser doesn't throw 404 errors.
The actual fallback beeps will still be used since these are silent.
"""

import os
import subprocess
import sys

# Directory where sound effects should be placed
SFX_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'assets', 'audio', 'sfx')

# List of required sound effect files
REQUIRED_SOUNDS = [
    'dice_roll.mp3',
    'dice_hit.mp3',
    'dice_miss.mp3',
    'momentum_up.mp3',
    'momentum_down.mp3',
    'ui_click.mp3',
    'whoosh.mp3'
]

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_silent_mp3_with_ffmpeg(filepath, duration=0.1):
    """Create a silent MP3 file using ffmpeg"""
    try:
        subprocess.run([
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'anullsrc=r=44100:cl=mono',
            '-t', str(duration),
            '-q:a', '9',
            '-acodec', 'libmp3lame',
            '-y',
            filepath
        ], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating {filepath}: {e}")
        return False

def create_placeholder_file(filepath):
    """Create a minimal placeholder file"""
    # Create a minimal valid MP3 file header (silent frame)
    # This is a minimal MP3 frame that represents silence
    mp3_header = bytes([
        0xFF, 0xFB, 0x90, 0x00,  # MP3 sync word and header
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
    ])
    
    with open(filepath, 'wb') as f:
        # Write multiple frames to make it a valid file
        for _ in range(10):
            f.write(mp3_header)
    
    return True

def main():
    # Ensure directory exists
    os.makedirs(SFX_DIR, exist_ok=True)
    
    has_ffmpeg = check_ffmpeg()
    
    if has_ffmpeg:
        print("✓ ffmpeg found - creating proper silent MP3 files")
    else:
        print("⚠ ffmpeg not found - creating minimal placeholder files")
        print("  Install ffmpeg for proper audio files: https://ffmpeg.org/download.html")
    
    created = []
    skipped = []
    
    for sound_file in REQUIRED_SOUNDS:
        filepath = os.path.join(SFX_DIR, sound_file)
        
        if os.path.exists(filepath):
            skipped.append(sound_file)
            continue
        
        if has_ffmpeg:
            success = create_silent_mp3_with_ffmpeg(filepath, duration=0.1)
        else:
            success = create_placeholder_file(filepath)
        
        if success:
            created.append(sound_file)
            print(f"  ✓ Created {sound_file}")
        else:
            print(f"  ✗ Failed to create {sound_file}")
    
    print(f"\n{'='*60}")
    print(f"Created: {len(created)} files")
    print(f"Skipped: {len(skipped)} files (already exist)")
    
    if created:
        print(f"\n✓ Sound effect placeholders created successfully!")
        print(f"  Location: {SFX_DIR}")
        print(f"\n  These are silent placeholders to prevent 404 errors.")
        print(f"  The app will use fallback beeps for actual sound effects.")
        print(f"  Replace with real audio files for better experience.")
    
    if skipped:
        print(f"\n  Existing files were preserved:")
        for f in skipped:
            print(f"    - {f}")

if __name__ == '__main__':
    main()
