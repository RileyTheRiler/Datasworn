# Audio Asset Placeholders

This directory contains audio files for the psychological immersion system.

## Required Files

Create or add the following audio files:

### Core Ambience
- `ship_ambient.mp3` - Constant ship hum/drone (looping)

### Stress Audio
- `heartbeat.mp3` - Heartbeat sound (looping, triggered at stress > 70%)
- `breathing_heavy.mp3` - Heavy breathing (optional, for extreme stress)

### Sanity Audio
- `whisper.mp3` - Distant whispers (triggered at sanity < 30%)
- `static.mp3` - Radio static/interference (triggered at sanity < 15%)

### Stingers (One-shots)
- `stinger_fear.mp3` - Fear emotion trigger
- `stinger_anger.mp3` - Anger emotion trigger

## Audio Specifications

**Recommended Format**: MP3 or OGG
**Sample Rate**: 44.1kHz
**Bit Rate**: 128-192 kbps
**Looping Files**: Ensure seamless loops (no clicks/pops)

## Placeholder Generation

If you don't have audio files, you can:
1. Use royalty-free sound libraries (freesound.org, zapsplat.com)
2. Generate with AI (elevenlabs.io for whispers, suno.ai for ambient)
3. Use silence placeholders (the system will gracefully degrade)

## Integration

The `SoundscapeEngine.jsx` component automatically loads these files from `/sounds/` and triggers them based on psychological state.
