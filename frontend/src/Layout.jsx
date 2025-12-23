import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import SkillCheck from './components/SkillCheck';
import SceneDisplay from './components/SceneDisplay';
import TypewriterText from './components/TypewriterText';
import SaveManager from './components/SaveManager';
import SessionRecap from './components/SessionRecap';
import SessionTimer from './components/SessionTimer';
import SoundSettings from './components/SoundSettings';
import AutoSaveIndicator from './components/AutoSaveIndicator';
import RuleTooltip, { QuickReferencePanel } from './components/RuleTooltip';
import { useKeyboardShortcuts, KeyboardHelpOverlay } from './components/KeyboardShortcuts';
import { useAccessibility } from './contexts/AccessibilityContext';
import { useSoundEffects } from './contexts/SoundEffectsContext';
import { useVoice } from './contexts/VoiceContext';
import VoiceInput from './components/VoiceInput';
import TacticalBlueprint from './components/TacticalBlueprint';
import PortraitSettings from './components/PortraitSettings';
import PhotoAlbum from './components/PhotoAlbum';
import StarMap from './components/StarMap';
import RumorBoard from './components/RumorBoard';
import ShipBlueprintViewer from './components/ShipBlueprintViewer';
import CodexBrowser from './components/CodexBrowser';
import api from './utils/api';

// Atmospheric loading messages
const LOADING_MESSAGES = [
    "The stars align...",
    "Consulting the Forge...",
    "Fate deliberates...",
    "The Oracle speaks...",
    "Threads of destiny weave...",
    "The void whispers back...",
    "Calculating trajectories...",
    "Reading the cosmic static...",
];

const getRandomLoadingMessage = () =>
    LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)];

const MarkdownText = ({ text }) => {
    return <div className="font-serif text-lg leading-relaxed whitespace-pre-wrap">{text}</div>
}

// Icon map for stats
const STAT_ICONS = {
    'Health': '❤',
    'Spirit': '✦',
    'Supply': '▣',
    'Momentum': '⚡'
};

const StatBar = ({ label, value, max, color }) => {
    const percentage = (value / max) * 100;
    const icon = STAT_ICONS[label] || '●';

    return (
        <div className="mb-3 group">
            <div className="flex justify-between text-[10px] font-mono uppercase text-disco-cyan/70 mb-1.5">
                <span className="flex items-center gap-1">
                    <span className="text-xs">{icon}</span>
                    {label}
                </span>
                <span className="font-bold text-disco-paper/80">{value}/{max}</span>
            </div>
            <div className="h-1.5 bg-black/60 border border-disco-cyan/20 relative overflow-hidden">
                {/* Animated background grid */}
                <div className="absolute inset-0 opacity-20" style={{
                    backgroundImage: 'repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(107, 228, 227, 0.1) 2px, rgba(107, 228, 227, 0.1) 4px)'
                }} />
                {/* Progress bar with gradient */}
                <div
                    style={{ width: `${percentage}%` }}
                    className={`h-full ${color} transition-all duration-700 ease-out relative`}
                >
                    {/* Glow effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
                </div>
                {/* Danger indicator for low values */}
                {percentage < 30 && (
                    <div className="absolute right-0 top-0 w-1 h-full bg-disco-red animate-pulse" />
                )}
            </div>
        </div>
    );
}

const Layout = ({ gameState, assets, onAssetsUpdate, onAction, onGameStateUpdate, isLoading }) => {
    const { character, narrative, world, session } = gameState;
    const scrollRef = useRef(null);
    const [input, setInput] = React.useState("");
    const [showSkillCheck, setShowSkillCheck] = useState(false);
    const [showHelp, setShowHelp] = useState(false);
    const [showSaveManager, setShowSaveManager] = useState(false);
    const [showRecap, setShowRecap] = useState(false);
    const [showTimer, setShowTimer] = useState(true);
    const [showSoundSettings, setShowSoundSettings] = useState(false);
    const [showQuickReference, setShowQuickReference] = useState(false);
    const [showBlueprint, setShowBlueprint] = useState(false);
    const [showPortraitSettings, setShowPortraitSettings] = useState(false);
    const [showAlbum, setShowAlbum] = useState(false);
    const [showStarMap, setShowStarMap] = useState(false);
    const [showRumorBoard, setShowRumorBoard] = useState(false);
    const [showShipBlueprint, setShowShipBlueprint] = useState(false);
    const [showCodex, setShowCodex] = useState(false);
    const [activeStat, setActiveStat] = useState({ name: 'Iron', value: character.stats.iron });

    // Accessibility and sound contexts
    const { highContrast, setHighContrast } = useAccessibility();
    const { toggleMute } = useSoundEffects();
    const { speak, voiceEnabled, isListening, startListening, stopListening, transcript, setTranscript, supported: voiceSupported } = useVoice();
    const [lastSpoken, setLastSpoken] = useState('');

    // Update input from voice transcript
    useEffect(() => {
        if (transcript) setInput(transcript);
    }, [transcript]);

    // Auto-narrate new text
    useEffect(() => {
        if (voiceEnabled && narrative.pending_narrative && !isLoading && narrative.pending_narrative !== lastSpoken) {
            speak(narrative.pending_narrative);
            setLastSpoken(narrative.pending_narrative);
        }
    }, [narrative.pending_narrative, voiceEnabled, isLoading, speak, lastSpoken]);

    // Stat selection handler for keyboard shortcuts
    const handleStatSelect = useCallback((statName) => {
        const statMap = {
            'edge': { name: 'Edge', value: character.stats.edge },
            'heart': { name: 'Heart', value: character.stats.heart },
            'iron': { name: 'Iron', value: character.stats.iron },
            'shadow': { name: 'Shadow', value: character.stats.shadow },
            'wits': { name: 'Wits', value: character.stats.wits },
        };
        if (statMap[statName]) {
            setActiveStat(statMap[statName]);
            setShowSkillCheck(true);
        }
    }, [character.stats]);

    // Keyboard shortcuts - expanded
    useKeyboardShortcuts({
        onToggleRoll: useCallback(() => setShowSkillCheck(prev => !prev), []),
        onCloseModal: useCallback(() => {
            setShowSkillCheck(false);
            setShowHelp(false);
            setShowSaveManager(false);
            setShowRecap(false);
            setShowSoundSettings(false);
            setShowQuickReference(false);
            setShowBlueprint(false);
            setShowAlbum(false);
            setShowShipBlueprint(false);
        }, []),
        onShowHelp: useCallback(() => setShowHelp(true), []),
        onToggleMute: toggleMute,
        onToggleSaves: useCallback(() => setShowSaveManager(prev => !prev), []),
        onToggleCharacter: null, // Could add character sheet overlay
        onTogglePsyche: null, // Handled by PsycheDashboard
        onToggleTimer: useCallback(() => setShowTimer(prev => !prev), []),
        onToggleHighContrast: useCallback(() => setHighContrast(prev => !prev), [setHighContrast]),
        onSelectStat: handleStatSelect,
    });

    // Quick save/load keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'F5') {
                e.preventDefault();
                // Quick save via API
                fetch(`${API_URL}/save/quicksave`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: 'default' })
                }).then(() => console.log('Quick saved'));
            }
            if (e.key === 'F9') {
                e.preventDefault();
                // Quick load via API
                fetch(`${API_URL}/save/quickload`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload(); // Simple reload for MVP
                        }
                    });
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [narrative.pending_narrative]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;
        onAction(input);
        setInput("");
        setTranscript("");
    };

    const handleManualCapture = async () => {
        if (!narrative.pending_narrative) return;

        try {
            const response = await fetch(`${API_URL}/album/capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: 'default',
                    image_url: assets.scene_image || '/assets/defaults/location_placeholder.png',
                    caption: `Manual Capture: ${world.current_location}`,
                    tags: ["Manual", world.current_location],
                    scene_id: world.current_location
                })
            });
            const data = await response.json();
            if (data.success) {
                // Flash effect or notification?
                console.log("Captured!");
                setShowAlbum(true); // Open album to show result
            }
        } catch (error) {
            console.error("Capture failed:", error);
        }
    };

    const handleRollComplete = async () => {
        try {
            const data = await api.post('/roll/commit', {
                session_id: session || "default",
                stat_name: activeStat.name,
                stat_val: activeStat.value,
                adds: 0,
                move_name: "Action Roll"
            });

            // Update game state if callback is provided
            if (onGameStateUpdate && data.state) {
                onGameStateUpdate(data.state);
            }

            // Update assets if returned
            if (onAssetsUpdate && data.assets) {
                onAssetsUpdate(prev => ({ ...prev, ...data.assets }));
            }

            return data;
        } catch (error) {
            console.error("Roll commit failed:", error);
            throw error;
        }
    }

    return (
        <div className="flex flex-col lg:flex-row h-screen w-full bg-disco-bg bg-grunge bg-blend-multiply overflow-hidden animate-[crtFlicker_0.15s_infinite]">
            {/* LEFT: Visual & Stats */}
            <div className="w-full lg:w-1/3 border-b lg:border-b-0 lg:border-r border-disco-cyan/10 flex flex-col relative bg-black/20">
                {/* HUD Corner Brackets - Top Left */}
                <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-disco-cyan/40 z-50" />
                <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-disco-cyan/40 z-50" />
                {/* Isometric Viewport */}
                <div className="viewport-container flex-1 bg-black/80 relative overflow-hidden group">
                    {/* Scene Display */}
                    <div className="absolute inset-0 z-0 group-hover:shadow-glow transition-shadow duration-300">
                        <SceneDisplay
                            imageUrl={assets?.scene_image}
                            locationName={world?.current_location}
                            isLoading={isLoading}
                            weather={world?.current_weather || 'Clear'}
                            timeOfDay={world?.current_time || 'Day'}
                        />
                    </div>

                    {/* Vignette - kept for style */}
                    <div className="absolute inset-0 bg-radial-gradient from-transparent to-black/80 pointer-events-none z-10 transition-opacity duration-500 opacity-60"></div>

                    {/* Location Overlay */}
                    <div className="absolute top-0 left-0 p-8 w-full z-20 pointer-events-none">
                        <h2 className="font-serif text-4xl text-disco-paper text-outline italic tracking-wider filter drop-shadow-lg">{world.current_location}</h2>
                        <div className="flex items-center gap-2 mt-2">
                            <span className="w-2 h-2 bg-disco-accent rounded-full animate-pulse"></span>
                            <div className="text-disco-paper/60 font-mono text-xs tracking-[0.2em] uppercase">Sector: The Forge</div>
                        </div>
                    </div>
                </div>

                {/* Character HUD */}
                <div className="stats-panel h-1/3 bg-disco-panel p-6 border-t border-disco-muted/20 flex flex-col relative overflow-hidden">
                    {/* Grunge Overlay for Panel */}
                    <div className="absolute inset-0 bg-grunge opacity-20 pointer-events-none"></div>

                    <div className="flex items-start gap-6 mb-6 relative z-10">
                        <div className="w-24 h-32 bg-disco-dark border-2 border-disco-paper/20 shadow-hard rotate-[-1deg] relative overflow-hidden group transition-transform hover:rotate-0">
                            {/* Portrait */}
                            <img
                                src={assets?.portrait || "/assets/defaults/avatar_wireframe.svg"}
                                alt="Character"
                                className="w-full h-full object-cover grayscale-[30%] contrast-125 hover:grayscale-0 transition-all duration-700"
                            />
                            {/* Edit Portrait Button via Overlay */}
                            <button
                                onClick={() => setShowPortraitSettings(true)}
                                className="absolute top-1 right-1 p-1 bg-black/50 hover:bg-disco-cyan/80 text-disco-cyan hover:text-black rounded opacity-0 group-hover:opacity-100 transition-opacity z-20"
                                title="Customize Appearance"
                            >
                                ✏️
                            </button>
                        </div>
                        <div className="flex-1 pt-2">
                            <h3 className="font-serif text-3xl font-bold text-disco-paper text-outline tracking-wider">{character.name}</h3>
                            <div className="flex gap-2 mt-3">
                                <span className="px-2 py-0.5 bg-disco-red/10 border border-disco-red text-disco-red text-[10px] font-mono uppercase tracking-wider font-bold">Iron Sworn</span>
                                <span className="px-2 py-0.5 bg-disco-cyan/10 border border-disco-cyan text-disco-cyan text-[10px] font-mono uppercase tracking-wider font-bold">Lvl 1</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-x-8 gap-y-4 relative z-10">
                        <StatBar label="Health" value={character.condition.health} max={5} color="bg-disco-red" />
                        <StatBar label="Spirit" value={character.condition.spirit} max={5} color="bg-disco-purple" />
                        <StatBar label="Supply" value={character.condition.supply} max={5} color="bg-disco-yellow" />
                        <StatBar label="Momentum" value={character.momentum.value} max={10} color="bg-disco-cyan" />
                    </div>
                </div>
            </div>

            {/* RIGHT: Narrative Flow */}
            <div className="w-full lg:w-2/3 flex flex-col relative bg-disco-panel/60">
                {/* HUD Corner Brackets - Top Right */}
                <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-disco-accent/40 z-50" />
                {/* Animated grid background */}
                <div className="absolute inset-0 opacity-[0.02] pointer-events-none" style={{
                    backgroundImage: 'linear-gradient(rgba(107, 228, 227, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(107, 228, 227, 0.1) 1px, transparent 1px)',
                    backgroundSize: '20px 20px',
                    animation: 'gridScroll 20s linear infinite'
                }} />
                {/* Log */}
                <div className="narrative-scroll flex-1 overflow-y-auto p-12 scroll-smooth" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto space-y-12">
                        <div className="prose prose-invert prose-lg text-disco-paper/90 fade-in leading-loose">
                            <TypewriterText
                                text={narrative.pending_narrative}
                                characters={gameState.relationships?.crew || {}}
                                baseSpeed={20}
                                className="font-mono text-base leading-relaxed tracking-wide"
                                onComplete={() => {
                                    // Auto-scroll after typewriter completes
                                    if (scrollRef.current) {
                                        scrollRef.current.scrollTo({
                                            top: scrollRef.current.scrollHeight,
                                            behavior: 'smooth'
                                        });
                                    }
                                }}
                            />
                        </div>

                        {isLoading && (
                            <div className="flex items-center gap-3 text-disco-cyan font-mono text-sm loading-text">
                                <span className="w-2 h-2 bg-disco-cyan rounded-full animate-pulse" />
                                <span className="italic">{getRandomLoadingMessage()}</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Input Area - Sticky to Bottom */}
                <div className="sticky bottom-0 p-8 pb-12 bg-disco-bg border-t border-disco-muted/30 backdrop-blur-sm">
                    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative group flex gap-2">
                        {/* Skill Check Toggle */}
                        <button
                            type="button"
                            onClick={() => setShowSkillCheck(true)}
                            className="px-4 py-2 border border-disco-muted text-disco-paper font-serif hover:bg-disco-accent hover:text-black transition-colors"
                            title="Make a Move"
                        >
                            🎲
                        </button>

                        <VoiceInput />

                        <input
                            type="text"
                            className="action-input flex-1 bg-black/40 border-b-2 border-disco-muted text-disco-paper font-serif text-xl p-4 focus:outline-none focus:border-disco-accent focus:ring-2 focus:ring-disco-accent/50 focus:animate-[inputPulse_2s_ease-in-out_infinite] transition-all placeholder:text-disco-muted/30"
                            placeholder="What do you do?"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={isLoading}
                        />
                        <button
                            type="button"
                            onClick={handleManualCapture}
                            className="absolute right-16 top-1/2 -translate-y-1/2 text-disco-purple hover:text-disco-paper transition-colors opacity-60 hover:opacity-100"
                            title="Capture Cinematic Moment"
                        >
                            📷
                        </button>
                        <button
                            type="submit"
                            className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-focus-within:opacity-100 transition-opacity text-disco-accent font-serif font-bold tracking-wider uppercase"
                        >
                            Execute
                        </button>
                    </form>

                    {/* Keyboard Shortcuts Hint */}
                    <div className="mt-2 text-center text-[10px] font-mono text-disco-muted/50 uppercase flex justify-center items-center gap-4 flex-wrap">
                        <span>Press <kbd className="px-1 bg-disco-dark/50 rounded">R</kbd> roll</span>
                        <span><kbd className="px-1 bg-disco-dark/50 rounded">1-5</kbd> stats</span>
                        <span><kbd className="px-1 bg-disco-dark/50 rounded">F5</kbd> save</span>
                        <span><kbd className="px-1 bg-disco-dark/50 rounded">?</kbd> help</span>
                        <button
                            onClick={() => setShowSaveManager(true)}
                            className="text-disco-cyan hover:text-disco-paper transition-colors"
                        >
                            💾 Saves
                        </button>
                        <button
                            onClick={() => setShowRecap(true)}
                            className="text-disco-accent hover:text-disco-paper transition-colors"
                        >
                            📜 Recap
                        </button>
                        <button
                            onClick={() => setShowQuickReference(true)}
                            className="text-disco-purple hover:text-disco-paper transition-colors"
                            title="Quick Reference (rules)"
                        >
                            📖 Rules
                        </button>
                        <button
                            onClick={() => setShowSoundSettings(true)}
                            className="text-disco-muted hover:text-disco-paper transition-colors"
                            title="Sound Settings"
                        >
                            🔊 Sound
                        </button>
                        <button
                            onClick={() => setShowBlueprint(true)}
                            className="text-disco-green hover:text-disco-paper transition-colors"
                            title="Tactical Blueprint (M)"
                        >
                            🗺️ Map
                        </button>
                        <a
                            href={`${API_URL}/export/story/default`}
                            download
                            className="text-disco-yellow hover:text-disco-paper transition-colors"
                            title="Export your story as Markdown"
                        >
                            📤 Export
                        </a>
                        <button
                            onClick={() => setShowAlbum(true)}
                            className="text-disco-purple hover:text-disco-paper transition-colors"
                            title="Photo Album - Captured Moments"
                        >
                            📸 Album
                        </button>
                        <button
                            onClick={() => setShowCodex(true)}
                            className="text-disco-cyan hover:text-disco-paper transition-colors"
                            title="Lore Codex"
                        >
                            📘 Codex
                        </button>
                        <button
                            onClick={() => setShowStarMap(true)}
                            className="text-disco-cyan hover:text-disco-paper transition-colors"
                            title="Star Map Navigation"
                        >
                            🌌 Star Map
                        </button>
                        <button
                            onClick={() => setShowRumorBoard(true)}
                            className="text-disco-orange hover:text-disco-paper transition-colors"
                            title="Rumor Network"
                        >
                            📡 Rumors
                        </button>
                        <button
                            onClick={() => setShowShipBlueprint(true)}
                            className="text-disco-red hover:text-disco-paper transition-colors"
                            title="Ship Schematic & Condition"
                        >
                            🚀 Ship
                        </button>
                    </div>

                    {/* Dice/Skill Check Overlay */}
                    {showSkillCheck && (
                        <SkillCheck
                            stat={character.stats.iron}
                            statName="Iron"
                            character={character}
                            onRollComplete={handleRollComplete}
                            onClose={() => setShowSkillCheck(false)}
                        />
                    )}

                    {/* Keyboard Help Overlay */}
                    <KeyboardHelpOverlay
                        isOpen={showHelp}
                        onClose={() => setShowHelp(false)}
                    />

                    {/* Save Manager Modal */}
                    <SaveManager
                        isOpen={showSaveManager}
                        onClose={() => setShowSaveManager(false)}
                        sessionId="default"
                        onLoadComplete={(loadedState) => {
                            // For MVP, reload the page to refresh state
                            window.location.reload();
                        }}
                    />

                    {/* Session Recap Modal */}
                    <SessionRecap
                        isOpen={showRecap}
                        onClose={() => setShowRecap(false)}
                        sessionId="default"
                    />

                    {/* Sound Settings Modal */}
                    <SoundSettings
                        isOpen={showSoundSettings}
                        onClose={() => setShowSoundSettings(false)}
                    />

                    {/* Quick Reference Panel */}
                    <QuickReferencePanel
                        isOpen={showQuickReference}
                        onClose={() => setShowQuickReference(false)}
                    />

                    {/* Tactical Blueprint Modal */}
                    <TacticalBlueprint
                        sessionId="default"
                        visible={showBlueprint}
                        onClose={() => setShowBlueprint(false)}
                    />

                    {/* Portrait Settings Modal */}
                    <PortraitSettings
                        isOpen={showPortraitSettings}
                        onClose={() => setShowPortraitSettings(false)}
                        characterName={character.name}
                        onUpdate={(newAssets) => {
                            if (onAssetsUpdate) onAssetsUpdate(prev => ({ ...prev, ...newAssets }));
                        }}
                    />

                    {/* Star Map Modal */}
                    <StarMap
                        sessionId="default"
                        visible={showStarMap}
                        onClose={() => setShowStarMap(false)}
                    />

                    {/* Rumor Board Modal */}
                    <RumorBoard
                        sessionId="default"
                        visible={showRumorBoard}
                        onClose={() => setShowRumorBoard(false)}
                    />

                    {/* Ship Blueprint Modal */}
                    <ShipBlueprintViewer
                        sessionId="default"
                        visible={showShipBlueprint}
                        onClose={() => setShowShipBlueprint(false)}
                    />

                    {/* Photo Album Modal */}
                    <PhotoAlbum
                        sessionId="default"
                        visible={showAlbum}
                        onClose={() => setShowAlbum(false)}
                    />

                    <CodexBrowser
                        visible={showCodex}
                        onClose={() => setShowCodex(false)}
                    />
                </div>
            </div>

            {/* Session Timer - Fixed position */}
            <SessionTimer
                isVisible={showTimer}
                onToggle={() => setShowTimer(false)}
                breakReminderInterval={60}
            />

            {/* Auto-Save Indicator - Fixed position */}
            <AutoSaveIndicator
                sessionId="default"
                saveInterval={120000}
            />
        </div>
    )
}

export default Layout;
