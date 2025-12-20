import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { Howl } from 'howler';

/**
 * SoundEffectsContext - Provides sound effect playback throughout the app
 * 
 * Uses howler.js for reliable cross-browser audio playback
 * Manages volume, muting, and sound library
 */

const SoundEffectsContext = createContext(null);

export const useSoundEffects = () => {
    const context = useContext(SoundEffectsContext);
    if (!context) {
        throw new Error('useSoundEffects must be used within SoundEffectsProvider');
    }
    return context;
};

export const SoundEffectsProvider = ({ children }) => {
    const [isMuted, setIsMuted] = useState(() => {
        const saved = localStorage.getItem('soundEffectsMuted');
        return saved ? JSON.parse(saved) : false;
    });

    const [volume, setVolume] = useState(() => {
        const saved = localStorage.getItem('soundEffectsVolume');
        return saved ? parseFloat(saved) : 0.5;
    });

    const soundsRef = useRef({});

    // Initialize sound library
    useEffect(() => {
        // Define all sound effects with fallback to simple beeps if files don't exist
        const soundDefinitions = {
            dice_roll: {
                src: ['/sounds/dice_roll.mp3', '/sounds/dice_roll.ogg'],
                volume: 0.6,
                fallback: () => playBeep(200, 0.1, 'sine')
            },
            dice_hit: {
                src: ['/sounds/dice_hit.mp3', '/sounds/dice_hit.ogg'],
                volume: 0.7,
                fallback: () => playBeep(440, 0.2, 'sine')
            },
            dice_miss: {
                src: ['/sounds/dice_miss.mp3', '/sounds/dice_miss.ogg'],
                volume: 0.6,
                fallback: () => playBeep(110, 0.3, 'sawtooth')
            },
            momentum_up: {
                src: ['/sounds/momentum_up.mp3', '/sounds/momentum_up.ogg'],
                volume: 0.5,
                fallback: () => playBeep(523, 0.15, 'sine')
            },
            momentum_down: {
                src: ['/sounds/momentum_down.mp3', '/sounds/momentum_down.ogg'],
                volume: 0.5,
                fallback: () => playBeep(196, 0.15, 'sine')
            },
            button_click: {
                src: ['/sounds/button_click.mp3', '/sounds/button_click.ogg'],
                volume: 0.3,
                fallback: () => playBeep(800, 0.05, 'square')
            },
            whoosh: {
                src: ['/sounds/whoosh.mp3', '/sounds/whoosh.ogg'],
                volume: 0.4,
                fallback: () => playBeep(300, 0.2, 'sine')
            }
        };

        // Load sounds with error handling
        Object.entries(soundDefinitions).forEach(([name, config]) => {
            try {
                soundsRef.current[name] = new Howl({
                    src: config.src,
                    volume: config.volume * volume,
                    onloaderror: () => {
                        console.warn(`Failed to load sound: ${name}, using fallback`);
                        soundsRef.current[name] = { fallback: config.fallback };
                    }
                });
            } catch (err) {
                console.warn(`Error creating sound ${name}:`, err);
                soundsRef.current[name] = { fallback: config.fallback };
            }
        });

        return () => {
            // Cleanup: unload all sounds
            Object.values(soundsRef.current).forEach(sound => {
                if (sound.unload) sound.unload();
            });
        };
    }, []);

    // Update volume when it changes
    useEffect(() => {
        Object.values(soundsRef.current).forEach(sound => {
            if (sound.volume) {
                sound.volume(volume);
            }
        });
        localStorage.setItem('soundEffectsVolume', volume.toString());
    }, [volume]);

    // Save mute state
    useEffect(() => {
        localStorage.setItem('soundEffectsMuted', JSON.stringify(isMuted));
    }, [isMuted]);

    /**
     * Play a sound effect by name
     * @param {string} soundName - Name of the sound to play
     * @param {object} options - Optional settings (volume override, etc.)
     */
    const playSound = (soundName, options = {}) => {
        if (isMuted) return;

        const sound = soundsRef.current[soundName];
        if (!sound) {
            console.warn(`Sound not found: ${soundName}`);
            return;
        }

        try {
            if (sound.fallback) {
                // Use fallback beep
                sound.fallback();
            } else {
                // Play howler sound
                if (options.volume !== undefined) {
                    sound.volume(options.volume * volume);
                }
                sound.play();
            }
        } catch (err) {
            console.warn(`Error playing sound ${soundName}:`, err);
        }
    };

    /**
     * Fallback beep generator using Web Audio API
     */
    const playBeep = (frequency, duration, type = 'sine') => {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.value = frequency;
            oscillator.type = type;
            gainNode.gain.value = volume * 0.3; // Quieter for beeps

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        } catch (err) {
            console.warn('Error playing fallback beep:', err);
        }
    };

    const toggleMute = () => setIsMuted(prev => !prev);

    const value = {
        playSound,
        isMuted,
        setIsMuted,
        toggleMute,
        volume,
        setVolume
    };

    return (
        <SoundEffectsContext.Provider value={value}>
            {children}
        </SoundEffectsContext.Provider>
    );
};

export default SoundEffectsProvider;
