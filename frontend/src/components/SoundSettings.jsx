import React from 'react';
import { useSoundEffects } from '../contexts/SoundEffectsContext';

/**
 * SoundSettings - Panel for controlling sound effects and volume
 *
 * Features:
 * - Master volume slider
 * - Mute toggle
 * - Sound effect test buttons
 * - Persistent settings via localStorage
 */

const SoundSettings = ({ isOpen, onClose }) => {
    const { playSound, isMuted, toggleMute, volume, setVolume } = useSoundEffects();

    if (!isOpen) return null;

    const testSounds = [
        { id: 'dice_roll', label: 'Dice Roll' },
        { id: 'dice_hit', label: 'Strong Hit' },
        { id: 'dice_miss', label: 'Miss' },
        { id: 'momentum_up', label: 'Momentum Up' },
        { id: 'momentum_down', label: 'Momentum Down' },
        { id: 'button_click', label: 'Button Click' },
    ];

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm"
            onClick={onClose}
        >
            <div
                className="bg-disco-panel border-2 border-disco-muted p-8 rounded-lg max-w-md w-full mx-4 shadow-2xl"
                onClick={e => e.stopPropagation()}
            >
                <h2 className="font-serif text-2xl text-disco-paper mb-6 text-center uppercase tracking-widest">
                    Sound Settings
                </h2>

                {/* Mute Toggle */}
                <div className="flex items-center justify-between mb-6 p-4 bg-disco-dark/50 rounded-lg">
                    <span className="text-disco-paper font-serif">Sound Effects</span>
                    <button
                        onClick={toggleMute}
                        className={`
                            px-4 py-2 rounded font-mono text-sm transition-colors
                            ${isMuted
                                ? 'bg-disco-red/20 border border-disco-red text-disco-red'
                                : 'bg-disco-cyan/20 border border-disco-cyan text-disco-cyan'
                            }
                        `}
                    >
                        {isMuted ? '🔇 Muted' : '🔊 On'}
                    </button>
                </div>

                {/* Volume Slider */}
                <div className="mb-6">
                    <div className="flex justify-between text-sm font-mono text-disco-muted mb-2">
                        <span>Volume</span>
                        <span>{Math.round(volume * 100)}%</span>
                    </div>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={volume}
                        onChange={(e) => setVolume(parseFloat(e.target.value))}
                        className="w-full h-2 bg-disco-dark rounded-lg appearance-none cursor-pointer
                            [&::-webkit-slider-thumb]:appearance-none
                            [&::-webkit-slider-thumb]:w-4
                            [&::-webkit-slider-thumb]:h-4
                            [&::-webkit-slider-thumb]:bg-disco-cyan
                            [&::-webkit-slider-thumb]:rounded-full
                            [&::-webkit-slider-thumb]:cursor-pointer
                            [&::-webkit-slider-thumb]:shadow-lg
                        "
                        disabled={isMuted}
                    />
                    <div className="flex justify-between text-xs text-disco-muted mt-1">
                        <span>Quiet</span>
                        <span>Loud</span>
                    </div>
                </div>

                {/* Test Sounds */}
                <div className="mb-6">
                    <h3 className="text-disco-muted font-mono text-xs uppercase mb-3">Test Sounds</h3>
                    <div className="grid grid-cols-2 gap-2">
                        {testSounds.map(sound => (
                            <button
                                key={sound.id}
                                onClick={() => playSound(sound.id)}
                                disabled={isMuted}
                                className={`
                                    px-3 py-2 text-sm font-mono rounded border transition-colors
                                    ${isMuted
                                        ? 'border-disco-muted/30 text-disco-muted/50 cursor-not-allowed'
                                        : 'border-disco-muted hover:border-disco-cyan hover:text-disco-cyan text-disco-paper'
                                    }
                                `}
                            >
                                {sound.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Close Button */}
                <div className="text-center">
                    <button
                        onClick={onClose}
                        className="btn-disco px-6 py-2"
                    >
                        Close
                    </button>
                </div>

                <div className="mt-4 text-center text-[10px] text-disco-muted uppercase">
                    Press M to toggle mute anytime
                </div>
            </div>
        </div>
    );
};

export default SoundSettings;
