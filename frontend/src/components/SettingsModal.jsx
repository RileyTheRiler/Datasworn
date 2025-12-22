import React, { useState } from 'react';
import DraggableModal from './DraggableModal';
import { useSoundEffects } from '../contexts/SoundEffectsContext';
import { useAudio } from '../contexts/AudioContext';
import { useVoice } from '../contexts/VoiceContext';
import { useAccessibility } from '../contexts/AccessibilityContext';
import api from '../utils/api';

/**
 * SettingsModal - Unified settings interface with tabbed navigation
 * Consolidates Sound Settings, Portrait Settings, and other configurations
 */
const SettingsModal = ({ isOpen, onClose, sessionId = 'default' }) => {
    const [activeTab, setActiveTab] = useState('audio');

    const tabs = [
        { id: 'audio', label: 'Audio', icon: '🔊' },
        { id: 'accessibility', label: 'Accessibility', icon: '♿' },
        { id: 'game', label: 'Game', icon: '⚙️' }
    ];

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={onClose}
            title="Settings"
            defaultWidth={700}
            defaultHeight={500}
        >
            <div className="flex h-full">
                {/* Tab Navigation */}
                <div className="w-48 bg-disco-dark/40 border-r border-disco-muted/20 p-4">
                    <nav className="space-y-2">
                        {tabs.map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`w-full text-left px-4 py-3 rounded font-mono text-sm transition-all flex items-center gap-3 ${activeTab === tab.id
                                        ? 'bg-disco-cyan/20 border border-disco-cyan/50 text-disco-cyan'
                                        : 'text-disco-muted hover:bg-disco-muted/10 hover:text-disco-paper'
                                    }`}
                            >
                                <span className="text-lg">{tab.icon}</span>
                                <span>{tab.label}</span>
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Tab Content */}
                <div className="flex-1 p-6 overflow-y-auto">
                    {activeTab === 'audio' && <AudioTab sessionId={sessionId} />}
                    {activeTab === 'accessibility' && <AccessibilityTab />}
                    {activeTab === 'game' && <GameTab />}
                </div>
            </div>
        </DraggableModal>
    );
};

// Audio Settings Tab
const AudioTab = ({ sessionId }) => {
    const { playSound, isMuted: sfxMuted, toggleMute: toggleSfxMute, volume: sfxVolume, setVolume: setSfxVolume } = useSoundEffects();
    const { volumes, setVolume, muted, toggleMute } = useAudio();
    const { availableVoices, selectedVoice, setSelectedVoice, speak } = useVoice();

    const updateBackendVolume = (channel, value) => {
        api.post('/api/audio/volume', {
            session_id: sessionId,
            channel: channel,
            volume: value
        }).catch(err => console.error(`Failed to sync ${channel} volume:`, err));
    };

    const handleMasterVolumeChange = (newVolume) => {
        setVolume('master', newVolume);
        setSfxVolume(newVolume);
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

    const handleVoiceChange = (e) => {
        const voiceName = e.target.value;
        const voice = availableVoices.find(v => v.name === voiceName);
        if (voice) {
            setSelectedVoice(voice);
        }
    };

    const testVoice = () => {
        speak("This is a test of the text-to-speech voice. Your journey through the Forge continues.");
    };

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
        <div className="space-y-6">
            <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Master Systems</h3>

            {/* Master Controls */}
            <div className="p-4 bg-disco-dark/40 rounded border border-disco-muted/20">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-disco-paper font-serif text-sm">Output Status</span>
                    <button
                        onClick={handleToggleMute}
                        className={`px-3 py-1 rounded font-mono text-[10px] transition-all ${muted
                                ? 'bg-disco-red/20 border border-disco-red/50 text-disco-red'
                                : 'bg-disco-cyan/20 border border-disco-cyan/50 text-disco-cyan'
                            }`}
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

            {/* Channel Mixer */}
            <div className="p-4 bg-disco-dark/20 rounded border border-disco-muted/10">
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
            </div>

            {/* TTS Voice Selection */}
            <div className="p-4 bg-disco-dark/20 rounded border border-disco-muted/10">
                <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Text-to-Speech Voice</h3>

                <div className="mb-3">
                    <label className="block text-xs font-mono text-disco-muted uppercase mb-2">Narrator Voice</label>
                    <select
                        value={selectedVoice?.name || ''}
                        onChange={handleVoiceChange}
                        className="w-full bg-black/50 border border-disco-muted p-2 text-disco-paper rounded focus:border-disco-cyan focus:outline-none font-mono text-sm"
                    >
                        {availableVoices.map(voice => (
                            <option key={voice.name} value={voice.name}>
                                {voice.name} ({voice.lang})
                            </option>
                        ))}
                    </select>
                </div>

                <button
                    onClick={testVoice}
                    disabled={muted}
                    className={`w-full px-4 py-2 rounded font-mono text-sm transition-all ${muted
                            ? 'bg-disco-muted/10 text-disco-muted/30 cursor-not-allowed'
                            : 'bg-disco-cyan/20 border border-disco-cyan/50 text-disco-cyan hover:bg-disco-cyan/30'
                        }`}
                >
                    {'>'} Test Voice
                </button>
            </div>

            {/* Diagnostic Tones */}
            <div>
                <h3 className="text-disco-muted font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Diagnostic Tones</h3>
                <div className="grid grid-cols-2 gap-2">
                    {testSounds.map(sound => (
                        <button
                            key={sound.id}
                            onClick={() => playSound(sound.id)}
                            disabled={muted}
                            className={`px-3 py-2 text-[10px] font-mono rounded border transition-all text-left ${muted
                                    ? 'border-disco-muted/20 text-disco-muted/30 cursor-not-allowed bg-transparent'
                                    : 'border-disco-muted/30 hover:border-disco-cyan/50 hover:text-disco-cyan hover:bg-disco-cyan/5 text-disco-muted bg-black/20'
                                }`}
                        >
                            {'>'} {sound.label}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Accessibility Settings Tab
const AccessibilityTab = () => {
    const { highContrast, setHighContrast } = useAccessibility();

    return (
        <div className="space-y-6">
            <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Display Options</h3>

            <div className="p-4 bg-disco-dark/40 rounded border border-disco-muted/20">
                <div className="flex items-center justify-between mb-2">
                    <div>
                        <div className="text-disco-paper font-serif text-sm">High Contrast Mode</div>
                        <div className="text-disco-muted text-xs font-mono mt-1">Increases text visibility</div>
                    </div>
                    <button
                        onClick={() => setHighContrast(!highContrast)}
                        className={`px-3 py-1 rounded font-mono text-[10px] transition-all ${highContrast
                                ? 'bg-disco-cyan/20 border border-disco-cyan/50 text-disco-cyan'
                                : 'bg-disco-muted/20 border border-disco-muted/50 text-disco-muted'
                            }`}
                    >
                        {highContrast ? 'ON' : 'OFF'}
                    </button>
                </div>
            </div>

            <div className="p-4 bg-disco-dark/20 rounded border border-disco-muted/10">
                <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Keyboard Shortcuts</h3>
                <div className="space-y-2 text-sm font-mono text-disco-muted">
                    <div className="flex justify-between">
                        <span>Roll Dice</span>
                        <kbd className="px-2 py-1 bg-disco-dark/50 rounded text-disco-cyan">R</kbd>
                    </div>
                    <div className="flex justify-between">
                        <span>Select Stats</span>
                        <kbd className="px-2 py-1 bg-disco-dark/50 rounded text-disco-cyan">1-5</kbd>
                    </div>
                    <div className="flex justify-between">
                        <span>Quick Save</span>
                        <kbd className="px-2 py-1 bg-disco-dark/50 rounded text-disco-cyan">F5</kbd>
                    </div>
                    <div className="flex justify-between">
                        <span>Quick Load</span>
                        <kbd className="px-2 py-1 bg-disco-dark/50 rounded text-disco-cyan">F9</kbd>
                    </div>
                    <div className="flex justify-between">
                        <span>Help</span>
                        <kbd className="px-2 py-1 bg-disco-dark/50 rounded text-disco-cyan">?</kbd>
                    </div>
                    <div className="flex justify-between">
                        <span>Close Modal</span>
                        <kbd className="px-2 py-1 bg-disco-dark/50 rounded text-disco-cyan">ESC</kbd>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Game Settings Tab
const GameTab = () => {
    const [showTimer, setShowTimer] = useState(true);
    const [autoSaveInterval, setAutoSaveInterval] = useState(120);

    return (
        <div className="space-y-6">
            <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">Session Options</h3>

            <div className="p-4 bg-disco-dark/40 rounded border border-disco-muted/20">
                <div className="flex items-center justify-between mb-2">
                    <div>
                        <div className="text-disco-paper font-serif text-sm">Session Timer</div>
                        <div className="text-disco-muted text-xs font-mono mt-1">Display play time counter</div>
                    </div>
                    <button
                        onClick={() => setShowTimer(!showTimer)}
                        className={`px-3 py-1 rounded font-mono text-[10px] transition-all ${showTimer
                                ? 'bg-disco-cyan/20 border border-disco-cyan/50 text-disco-cyan'
                                : 'bg-disco-muted/20 border border-disco-muted/50 text-disco-muted'
                            }`}
                    >
                        {showTimer ? 'ON' : 'OFF'}
                    </button>
                </div>
            </div>

            <div className="p-4 bg-disco-dark/20 rounded border border-disco-muted/10">
                <div className="mb-3">
                    <label className="block text-xs font-mono text-disco-muted uppercase mb-2">
                        Auto-Save Interval (seconds)
                    </label>
                    <div className="flex items-center gap-4">
                        <input
                            type="range"
                            min="30"
                            max="300"
                            step="30"
                            value={autoSaveInterval}
                            onChange={(e) => setAutoSaveInterval(parseInt(e.target.value))}
                            className="flex-1"
                        />
                        <span className="text-disco-cyan font-mono text-sm w-16 text-right">
                            {autoSaveInterval}s
                        </span>
                    </div>
                </div>
            </div>

            <div className="p-4 bg-disco-dark/20 rounded border border-disco-muted/10">
                <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4 opacity-70">About</h3>
                <div className="text-[9px] font-mono text-disco-muted leading-relaxed uppercase space-y-1">
                    <div>Starforged AI Game Master</div>
                    <div>Version 1.0.0</div>
                    <div className="pt-2 border-t border-disco-muted/10 mt-2">
                        Powered by Ollama + LangGraph
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
