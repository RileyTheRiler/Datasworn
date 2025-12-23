# Sound Effects Directory

This directory contains sound effect files for the game's audio feedback system.

## Required Files

The following sound effects are loaded by `SoundEffectsContext.jsx`:

### Dice Rolling Sounds
- **dice_roll.mp3** - Sound played when dice are being rolled
- **dice_hit.mp3** - Sound played when dice roll succeeds (hit)
- **dice_miss.mp3** - Sound played when dice roll fails (miss)

### Momentum Sounds
- **momentum_up.mp3** - Sound played when momentum increases
- **momentum_down.mp3** - Sound played when momentum decreases

### UI Sounds
- **ui_click.mp3** - Sound played for button clicks (mapped to `button_click`)
- **whoosh.mp3** - Transition/swoosh sound effect

## Audio Specifications

**Recommended Format**: MP3, OGG, or WAV
**Sample Rate**: 44.1kHz
**Bit Rate**: 128-192 kbps (for MP3/OGG)
**Duration**: 0.1-0.5 seconds for most effects

## Fallback System

If sound files are missing, the `SoundEffectsContext` will automatically use synthesized beeps generated with the Web Audio API:
- dice_roll: 200Hz sine wave
- dice_hit: 440Hz sine wave
- dice_miss: 110Hz sawtooth wave
- momentum_up: 523Hz sine wave
- momentum_down: 196Hz sine wave
- button_click: 800Hz square wave
- whoosh: 300Hz sine wave

## Finding Sound Effects

You can source sound effects from:
1. **Freesound.org** - Free sound library (CC licenses)
2. **Zapsplat.com** - Free sound effects
3. **Pixabay** - Royalty-free sounds
4. **Generate with AI** - Use tools like ElevenLabs or Suno
5. **Record your own** - Use Audacity or similar tools

## Current Status

Currently using fallback beeps. Replace these placeholder files with actual sound effects for better audio experience.
