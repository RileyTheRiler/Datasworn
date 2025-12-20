import React, { useEffect } from 'react';
import { useSoundEffects } from '../contexts/SoundEffectsContext';
import { useAudio } from '../contexts/AudioContext';
import api from '../utils/api';

/**
 * SoundSettings - Panel for controlling all game audio systems
 * Unified controls for SFX, Ambient, Music, and Voice
 */

const SoundSettings = ({ isOpen, onClose }) => {
    const { playSound, isMuted: sfxMuted, toggleMute: toggleSfxMute, volume: sfxVolume, setVolume: setSfxVolume } = useSoundEffects();
    const { volumes, setVolume, muted, toggleMute } = useAudio();
    const sessionId = "default";

    // Push updates to backend volumes
    const updateBackendVolume = (channel, value) => {
        api.post('/api/audio/volume', {
            session_id: sessionId,
            channel: channel,
            volume: value
        }).catch(err => console.error(`Failed to sync ${channel} volume:`, err));
    };

    const handleMasterVolumeChange = (newVolume) => {
        setVolume('master', newVolume);
        setSfxVolume(newVolume); // Keep UI SFX in sync with master
        updateBackendVolume('master', newVolume);
    };

    const handleChannelVolumeChange = (channel, newVolume) => {
        setVolume(channel, newVolume);
        updateBackendVolume(channel, newVolume);
    };

    const handleToggleMute = () => {
        toggleMute();
        toggleSfxMute();
        api.post(`/api/audio/mute/${sessionId}`).catch(err => console.error("Failed to sync mute state:", err));
    };

    if (!isOpen) return null;

    const testSounds = [
        { id: 'dice_roll', label: 'Dice Roll' },
        { id: 'dice_hit', label: 'Strong Hit' },
        { id: 'momentum_up', label: 'Momentum Up' },
        { id: 'button_click', label: 'Interface' },
    ];

    const VolumeSlider = ({ label, value, onChange, disabled }) => (
        <div className="mb-4">
            <div className="flex justify-between text-xs font-mono text-disco-muted mb-1">
                <span>{label}</span>
                <span className="text-disco-cyan">{Math.round(value * 100)}%</span>
            </div>
            <div className="relative h-1.5 bg-black/50 rounded-lg border border-disco-muted/20">
                <div
                    className="absolute top-0 left-0 h-full bg-disco-cyan rounded-lg transition-all duration-300"
                    style={{ width: `${value * 100}%`, opacity: disabled ? 0.3 : 1 }}
                />
                <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={value}
                    onChange={(e) => onChange(parseFloat(e.target.value))}
                    className="absolute top-0 left-0 w-full h-full opacity-0 cursor-pointer"
                    disabled={disabled}
                />
            </div>
        </div>
    );

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md animate-fadeIn"
            onClick={onClose}
        >
            <div
                className="bg-disco-panel border-2 border-disco-muted/50 p-8 rounded-lg max-w-lg w-full mx-4 shadow-[0_0_50px_rgba(0,0,0,0.8)] relative overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                {/* Background Decor */}
                <div className="absolute -top-24 -left-24 w-48 h-48 bg-disco-cyan/5 rounded-full blur-3xl" />
                <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-disco-red/5 rounded-full blur-3xl" />

                <div className="absolute top-0 right-0 p-4">
                    <button onClick={onClose} className="text-disco-muted hover:text-disco-paper transition-colors font-mono text-xl">
                        [ ESC ]
                    </button>
                </div>

                <h2 className="font-serif text-3xl text-disco-paper mb-8 text-center uppercase tracking-[0.2em] border-b border-disco-muted/20 pb-6 shadow-text">
                    Audio Configurations
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    {/* Primary Controls */}
                    <div className="space-y-6">
                        <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Master Systems</h3>

                        <div className="p-4 bg-disco-dark/40 rounded border border-disco-muted/20">
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-disco-paper font-serif text-sm">Output Status</span>
                                <button
                                    onClick={handleToggleMute}
                                    className={`
                                        px-3 py-1 rounded font-mono text-[10px] transition-all
                                        ${muted
                                            ? 'bg-disco-red/20 border border-disco-red/50 text-disco-red'
                                            : 'bg-disco-cyan/20 border border-disco-cyan/50 text-disco-cyan'
                                        }
                                    `}
                                >
                                    {muted ? 'OFFLINE' : 'ONLINE'}
                                </button>
                            </div>
                            <VolumeSlider
                                label="Master Gain"
                                value={volumes.master}
                                onChange={handleMasterVolumeChange}
                                disabled={muted}
                            />
                        </div>

                        <div>
                            <h3 className="text-disco-muted font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Diagnostic Tones</h3>
                            <div className="grid grid-cols-2 gap-2">
                                {testSounds.map(sound => (
                                    <button
                                        key={sound.id}
                                        onClick={() => playSound(sound.id)}
                                        disabled={muted}
                                        className={`
                                            px-3 py-2 text-[10px] font-mono rounded border transition-all text-left
                                            ${muted
                                                ? 'border-disco-muted/20 text-disco-muted/30 cursor-not-allowed bg-transparent'
                                                : 'border-disco-muted/30 hover:border-disco-cyan/50 hover:text-disco-cyan hover:bg-disco-cyan/5 text-disco-muted bg-black/20'
                                            }
                                        `}
                                    >
                                        {'>'} {sound.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Channel Mixing */}
                    <div className="space-y-4 p-4 bg-disco-dark/20 rounded border border-disco-muted/10">
                        <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Channel Mixer</h3>

                        <VolumeSlider
                            label="Atmospheric Environment"
                            value={volumes.ambient}
                            onChange={(v) => handleChannelVolumeChange('ambient', v)}
                            disabled={muted}
                        />

                        <VolumeSlider
                            label="Narrative Score"
                            value={volumes.music}
                            onChange={(v) => handleChannelVolumeChange('music', v)}
                            disabled={muted}
                        />

                        <VolumeSlider
                            label="Vocal Interface"
                            value={volumes.voice}
                            onChange={(v) => handleChannelVolumeChange('voice', v)}
                            disabled={muted}
                        />

                        <div className="mt-8 pt-4 border-t border-disco-muted/10 text-[9px] font-mono text-disco-muted leading-relaxed uppercase">
                            Operational status: optimal<br />
                            Processing multi-channel binaural stream...<br />
                            ElevenLabs Neural Voice Active.
                        </div>
                    </div>
                </div>

                <div className="flex gap-4">
                    <button
                        onClick={onClose}
                        className="flex-1 bg-disco-paper text-disco-panel font-serif uppercase tracking-widest py-3 hover:bg-white transition-all shadow-hard"
                    >
                        Commit Settings
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SoundSettings;
