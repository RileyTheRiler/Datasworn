import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import SkillCheck from './components/SkillCheck';
import SceneDisplay from './components/SceneDisplay';
import TypewriterText from './components/TypewriterText';
import SaveManager from './components/SaveManager';
import SessionRecap from './components/SessionRecap';
import SessionTimer from './components/SessionTimer';
import SettingsModal from './components/SettingsModal';
import AutoSaveIndicator from './components/AutoSaveIndicator';
import RuleTooltip, { QuickReferencePanel } from './components/RuleTooltip';
import { useKeyboardShortcuts, KeyboardHelpOverlay } from './components/KeyboardShortcuts';
import { useAccessibility } from './contexts/AccessibilityContext';
import { useSoundEffects } from './contexts/SoundEffectsContext';
import MusicPlayer from './components/MusicPlayer';
import { useVoice } from './contexts/VoiceContext';
import VoiceInput from './components/VoiceInput';
import TacticalBlueprint from './components/TacticalBlueprint';
import PortraitSettings from './components/PortraitSettings';
import PhotoAlbum from './components/PhotoAlbum';
import StarMap from './components/StarMap';
import RumorBoard from './components/RumorBoard';
import ShipBlueprintViewer from './components/ShipBlueprintViewer';
import CharacterHUD from './components/CharacterHUD';
import CombatDashboard from './components/CombatDashboard';
import StoryThreads from './components/StoryThreads';
import QuestJournal from './components/QuestJournal';
import QuestTracker from './components/QuestTracker';
import PsycheDashboard from './components/PsycheDashboard';
import WorldEvents from './components/WorldEvents';
import NPCDebugger from './components/NPCDebugger';
import MurderRevelationModal from './components/MurderRevelationModal';
import HeroTragedyChoice from './components/HeroTragedyChoice';
import ChoiceCrystallizedModal from './components/ChoiceCrystallizedModal';
import JournalModal from './components/JournalModal';
import RevelationModal from './components/RevelationModal';
import PracticeCards from './components/PracticeCards';
import PortArrivalModal from './components/PortArrivalModal';
import ChapterIndicator from './components/ChapterIndicator';
import AreaInfoOverlay from './components/AreaInfoOverlay';
import CampView from './components/CampView';
import WorldDashboard from './components/WorldDashboard';
import SensorRadar from './components/SensorRadar';
import PauseMenu from './components/PauseMenu';


const API_URL = 'http://localhost:8001/api';

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
    "Awaiting tactical uplink...",
];

const getRandomLoadingMessage = () =>
    LOADING_MESSAGES[Math.floor(Math.random() * LOADING_MESSAGES.length)];

const MarkdownText = ({ text }) => {
    return <div className="font-serif text-lg leading-relaxed whitespace-pre-wrap">{text}</div>
}

const Layout = ({ gameState, assets, onAssetsUpdate, onAction, isLoading }) => {
    const { character, narrative, world, session } = gameState;
    const scrollRef = useRef(null);
    const [conversationMode, setConversationMode] = useState(false);
    const [input, setInput] = React.useState("");
    const [showSkillCheck, setShowSkillCheck] = useState(false);
    const [showHelp, setShowHelp] = useState(false);
    const [showSaveManager, setShowSaveManager] = useState(false);
    const [showRecap, setShowRecap] = useState(false);
    const [showTimer, setShowTimer] = useState(true);
    const [showSettings, setShowSettings] = useState(false);
    const [showQuickReference, setShowQuickReference] = useState(false);
    const [showBlueprint, setShowBlueprint] = useState(false);
    const [showPortraitSettings, setShowPortraitSettings] = useState(false);
    const [showAlbum, setShowAlbum] = useState(false);
    const [showStarMap, setShowStarMap] = useState(false);
    const [showRumorBoard, setShowRumorBoard] = useState(false);
    const [showShipBlueprint, setShowShipBlueprint] = useState(false);
    const [showCombatDashboard, setShowCombatDashboard] = useState(false);
    const [showStoryThreads, setShowStoryThreads] = useState(false);
    const [showQuestJournal, setShowQuestJournal] = useState(false);
    const [showWorldEvents, setShowWorldEvents] = useState(false);
    const [showDebugger, setShowDebugger] = useState(false);
    const [showMurderRevelation, setShowMurderRevelation] = useState(false);
    const [showHeroTragedyChoice, setShowHeroTragedyChoice] = useState(false);
    const [showChoiceCrystallized, setShowChoiceCrystallized] = useState(false);
    const [showJournal, setShowJournal] = useState(false);
    const [showRevelation, setShowRevelation] = useState(false);
    const [showPractice, setShowPractice] = useState(false);
    const [showPortArrival, setShowPortArrival] = useState(false);
    const [showCamp, setShowCamp] = useState(false);
    const [showSensorRadar, setShowSensorRadar] = useState(false);
    const [showWorldDashboard, setShowWorldDashboard] = useState(false);
    const [showPauseMenu, setShowPauseMenu] = useState(false);
    const [revelationStage, setRevelationStage] = useState(null);
    const [revelationData, setRevelationData] = useState(null);
    const [revelationQuestion, setRevelationQuestion] = useState('');
    const [playerWound, setPlayerWound] = useState('');
    const [activeStat, setActiveStat] = useState({ name: 'Iron', value: character.stats.iron });

    // Accessibility and sound contexts
    const { highContrast, setHighContrast } = useAccessibility();
    const { toggleMute } = useSoundEffects();
    const { speak, voiceEnabled, selectedVoice, isListening, startListening, stopListening, transcript, setTranscript, supported: voiceSupported } = useVoice();
    const [lastSpoken, setLastSpoken] = useState('');

    // Update input from voice transcript
    useEffect(() => {
        if (transcript) setInput(transcript);
    }, [transcript]);

    // Auto-narrate new text
    useEffect(() => {
        if (voiceEnabled && selectedVoice && narrative.pending_narrative && !isLoading && narrative.pending_narrative !== lastSpoken) {
            speak(narrative.pending_narrative);
            setLastSpoken(narrative.pending_narrative);
        }
    }, [narrative.pending_narrative, voiceEnabled, selectedVoice, isLoading, speak, lastSpoken]);

    // Check for pending revelations
    useEffect(() => {
        const checkRevelations = async () => {
            // Only check if no other major narrative modal is open
            if (showMurderRevelation || showHeroTragedyChoice || showChoiceCrystallized || showRevelation) return;

            try {
                const response = await fetch(`${API_URL}/narrative/revelation/check?session_id=default`);
                if (response.ok) {
                    const data = await response.json();
                    if (data && data.stage) {
                        // Fetch the full scene data for the stage
                        let sceneData = null;

                        if (data.stage === 'choice_crystallized') {
                            setShowChoiceCrystallized(true);
                        } else if (data.stage === 'mirror_moment') {
                            const sceneResponse = await fetch(`${API_URL}/narrative/revelation/mirror-moment?session_id=default`, {
                                method: 'POST'
                            });
                            if (sceneResponse.ok) {
                                sceneData = await sceneResponse.json();
                                setRevelationStage('mirror_moment');
                                setRevelationData(sceneData);
                                setShowRevelation(true);
                            }
                        } else if (data.stage === 'cost_revealed') {
                            const sceneResponse = await fetch(`${API_URL}/narrative/revelation/cost-revealed?session_id=default`, {
                                method: 'POST'
                            });
                            if (sceneResponse.ok) {
                                sceneData = await sceneResponse.json();
                                setRevelationStage('cost_revealed');
                                setRevelationData(sceneData);
                                setShowRevelation(true);
                            }
                        } else if (data.stage === 'origin_glimpsed') {
                            const sceneResponse = await fetch(`${API_URL}/narrative/revelation/origin-glimpsed?session_id=default`, {
                                method: 'POST'
                            });
                            if (sceneResponse.ok) {
                                sceneData = await sceneResponse.json();
                                setRevelationStage('origin_glimpsed');
                                setRevelationData(sceneData);
                                setShowRevelation(true);
                            }
                        }
                    }
                }
            } catch (err) {
                console.error("Failed to check for revelations:", err);
            }
        };

        const interval = setInterval(checkRevelations, 30000); // Check every 30s
        return () => clearInterval(interval);
    }, [showMurderRevelation, showHeroTragedyChoice, showChoiceCrystallized, showRevelation]);

    // Auto-trigger ending sequence
    const [hasTriggeredEnding, setHasTriggeredEnding] = useState(false);
    useEffect(() => {
        if (narrative.ending_triggered && !narrative.ending_choice && !hasTriggeredEnding) {
            setShowMurderRevelation(true);
            setHasTriggeredEnding(true);
        }
    }, [narrative.ending_triggered, narrative.ending_choice, hasTriggeredEnding]);

    // Chapter State Management
    const [chapterState, setChapterState] = useState({
        name: "Loading...",
        number: "1",
        season: "Winter",
        progress: 0,
        total: 1,
        missions: []
    });

    useEffect(() => {
        const fetchChapterState = async () => {
            try {
                const response = await fetch(`${API_URL}/chapter/progress?session_id=default`);
                if (response.ok) {
                    const data = await response.json();

                    // Format missions for indicator
                    const missions = data.critical_missions.map(m => ({
                        name: m,
                        completed: data.completed_missions.includes(m)
                    }));

                    // Extract number from ID (e.g. "chapter_1" -> "1")
                    const num = data.chapter_id.split('_')[1] || "1";

                    setChapterState({
                        name: data.chapter_name,
                        number: num,
                        season: "Winter", // Backend should send this in progress endpoint ideally, or fetch from /chapter/current
                        progress: data.completed_missions.length,
                        total: data.critical_missions.length,
                        missions: missions
                    });

                    // Also update season more accurately if needed via separate call or just trust default
                    // Let's do a quick lazy fetch for details if we want season correct
                    // For MVP optimization, could merge these endpoints
                }

                // Fetch season detailed info
                const stateResponse = await fetch(`${API_URL}/chapter/current?session_id=default`);
                if (stateResponse.ok) {
                    const stateData = await stateResponse.json();
                    setChapterState(prev => ({
                        ...prev,
                        season: stateData.chapter.season
                    }));
                }
            } catch (err) {
                console.error("Chapter fetch error", err);
            }
        };

        fetchChapterState();
        const interval = setInterval(fetchChapterState, 15000); // Poll every 15s
        return () => clearInterval(interval);
    }, []);

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
            setShowSettings(false);
            setShowQuickReference(false);
            setShowBlueprint(false);
            setShowAlbum(false);
            setShowShipBlueprint(false);
            setShowShipBlueprint(false);
            setShowCombatDashboard(false);
            setShowDebugger(false);
            setShowCombatDashboard(false);
            setShowDebugger(false);
            setShowPractice(false);
            setShowCamp(false);
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

    // Quick save/load keyboard shortcuts + ESC for pause menu
    useEffect(() => {
        const handleKeyDown = (e) => {
            // ESC - Toggle Pause Menu
            if (e.key === 'Escape') {
                e.preventDefault();
                setShowPauseMenu(prev => !prev);
            }

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

        // Debug command for Port Arrival
        if (input.trim().toLowerCase() === '/port') {
            setShowPortArrival(true);
            setInput("");
            return;
        }

        // Check for debug command to open combat dashboard
        if (input.trim().toLowerCase() === '/combat') {
            setShowCombatDashboard(true);
            setInput("");
            return;
        }

        // Check for murder resolution trigger
        if (input.trim().toLowerCase() === '/murder') {
            setShowMurderRevelation(true);
            setInput("");
            return;
        }

        // Debug commands for revelation stages
        if (input.trim().toLowerCase() === '/mirror') {
            fetch(`${API_URL}/narrative/revelation/mirror-moment?session_id=default`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    setRevelationStage('mirror_moment');
                    setRevelationData(data);
                    setShowRevelation(true);
                });
            setInput("");
            return;
        }
        if (input.trim().toLowerCase() === '/cost') {
            fetch(`${API_URL}/narrative/revelation/cost-revealed?session_id=default`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    setRevelationStage('cost_revealed');
                    setRevelationData(data);
                    setShowRevelation(true);
                });
            setInput("");
            return;
        }
        if (input.trim().toLowerCase() === '/origin') {
            fetch(`${API_URL}/narrative/revelation/origin-glimpsed?session_id=default`, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    setRevelationStage('origin_glimpsed');
                    setRevelationData(data);
                    setShowRevelation(true);
                });
            setInput("");
            return;
        }
        if (input.trim().toLowerCase() === '/choice') {
            setShowChoiceCrystallized(true);
            setInput("");
            return;
        }

        // Pass conversation mode type
        onAction(input, conversationMode ? 'cognitive' : 'narrative');
        setInput("");
        setTranscript("");
    };

    const handleRevelationComplete = () => {
        // Revelation complete, show choice modal
        // HeroTragedyChoice component will fetch its own prompt data
        setShowMurderRevelation(false);
        setShowHeroTragedyChoice(true);
    };

    const handleChoiceMade = (choice) => {
        console.log('Player chose:', choice);
        // Choice is handled by the HeroTragedyChoice component
        // After ending narration, player can close the modal
    };

    const handleInterrogate = (npcData) => {
        // Map NPC name to ID for interrogation
        const npcIdMap = {
            'Torres': 'torres',
            'Vasquez': 'vasquez',
            'Kai': 'kai',
            'Dr. Okonkwo': 'okonkwo',
            'Ember': 'ember',
            'Yuki': 'yuki'
        };

        const npcId = npcIdMap[npcData.name] || npcData.id || npcData.name.toLowerCase();
        setInterrogationNPC({ id: npcId, name: npcData.name });
        setShowInterrogation(true);
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
        const sessionId = "default"; // Hardcoded in server.py MVP

        const res = await fetch(`${API_URL}/roll/commit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                stat_name: activeStat.name,
                stat_val: activeStat.value,
                adds: 0,
                move_name: "Action Roll"
            })
        });
        const data = await res.json();
        return data;
    }

    return (
        <div className="flex h-screen w-full bg-disco-bg bg-grunge bg-blend-multiply overflow-hidden animate-[crtFlicker_0.15s_infinite]">
            {/* LEFT: Visual & Stats */}
            <div className={`w-1/3 border-r border-disco-cyan/10 flex flex-col relative bg-black/20 transition-all duration-300 ${isLoading ? 'opacity-80' : 'opacity-100'}`}>
                {/* HUD Corner Brackets - Top Left */}
                <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-disco-cyan/40 z-50" />
                <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-disco-cyan/40 z-50" />
                {/* Isometric Viewport */}
                <div className="flex-1 bg-black/80 relative overflow-hidden group">
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
                        {/* Area Info Overlay (Rumors/Events) */}
                        <AreaInfoOverlay
                            areaId={world.current_location_id || world.current_location?.toLowerCase().replace(/ /g, '_')}
                            visible={!isLoading}
                        />
                    </div>
                </div>

                {/* Character HUD (Replacing hardcoded version) */}
                <CharacterHUD
                    character={character}
                    assets={assets}
                    onAssetsUpdate={onAssetsUpdate}
                    className="h-1/3"
                />
            </div>

            {/* RIGHT: Narrative Flow */}
            <div className="w-2/3 flex flex-col relative bg-disco-panel/60">
                {/* HUD Corner Brackets - Top Right */}
                <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-disco-accent/40 z-50" />

                {/* Chapter Indicator */}
                <div className="absolute top-4 right-12 z-40">
                    <ChapterIndicator
                        title={chapterState.name}
                        number={chapterState.number}
                        season={chapterState.season}
                        progress={chapterState.progress}
                        total={chapterState.total}
                        missions={chapterState.missions}
                    />
                </div>

                {/* Quest Tracker Overlay */}
                <QuestTracker sessionId="default" />

                {/* Animated grid background */}
                <div className="absolute inset-0 opacity-[0.02] pointer-events-none" style={{
                    backgroundImage: 'linear-gradient(rgba(107, 228, 227, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(107, 228, 227, 0.1) 1px, transparent 1px)',
                    backgroundSize: '20px 20px',
                    animation: 'gridScroll 20s linear infinite'
                }} />
                {/* Log */}
                <div className="flex-1 overflow-y-auto p-12 scroll-smooth" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto space-y-12">
                        <div className="prose prose-invert prose-lg text-disco-paper/90 fade-in leading-loose">
                            <TypewriterText
                                text={narrative.pending_narrative}
                                characters={gameState.relationships?.crew || {}}
                                baseSpeed={20}
                                className="font-mono text-base leading-relaxed tracking-wide"
                                onInterrogate={handleInterrogate}
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
                <div className={`sticky bottom-0 p-8 pb-12 bg-disco-bg border-t backdrop-blur-sm transition-colors duration-500 ${conversationMode ? 'border-disco-cyan/60 bg-disco-cyan/5' : 'border-disco-muted/30'}`}>
                    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative group flex gap-2">
                        {/* Conversation Mode Toggle */}
                        <button
                            type="button"
                            onClick={() => setConversationMode(prev => !prev)}
                            className={`px-4 py-2 border font-serif transition-all duration-300 flex items-center gap-2 ${conversationMode
                                ? 'bg-disco-cyan text-black border-disco-cyan font-bold shadow-[0_0_15px_rgba(34,211,238,0.4)]'
                                : 'border-disco-muted text-disco-paper hover:bg-disco-accent hover:text-black'
                                }`}
                            title={conversationMode ? "Switch to Narrative Mode" : "Switch to Conversation Mode"}
                        >
                            {conversationMode ? "💬 NPC" : "📜 Story"}
                        </button>

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
                            className={`flex-1 bg-black/40 border-b-2 font-serif text-xl p-4 focus:outline-none transition-all placeholder:text-disco-muted/30 ${conversationMode
                                ? 'border-disco-cyan text-disco-cyan focus:border-disco-cyan focus:ring-2 focus:ring-disco-cyan/50'
                                : 'border-disco-muted text-disco-paper focus:border-disco-accent focus:ring-2 focus:ring-disco-accent/50 focus:animate-[inputPulse_2s_ease-in-out_infinite]'
                                }`}
                            placeholder={conversationMode ? "Say something to the NPC..." : "What do you do?"}
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
                        <button
                            type="button"
                            onClick={handleManualCapture}
                            className="absolute right-24 top-1/2 -translate-y-1/2 text-disco-purple hover:text-disco-paper transition-colors opacity-60 hover:opacity-100"
                            title="Capture Cinematic Moment"
                        >
                            📷
                        </button>
                    </form>

                    {/* Keyboard Shortcuts Hint */}
                    <div className="mt-2 text-center text-[10px] font-mono text-disco-muted/50 uppercase flex justify-center items-center gap-4 flex-wrap">
                        <span>Press <kbd className="px-1 bg-disco-dark/50 rounded">R</kbd> roll</span>
                        <span><kbd className="px-1 bg-disco-dark/50 rounded">1-5</kbd> stats</span>
                        <span><kbd className="px-1 bg-disco-dark/50 rounded">F5</kbd> save</span>
                        <span><kbd className="px-1 bg-disco-dark/50 rounded">?</kbd> help</span>

                        <div className="h-4 w-px bg-disco-muted/30 mx-2"></div>

                        <button
                            onClick={() => setShowCombatDashboard(true)}
                            className="text-disco-red hover:text-disco-paper transition-colors font-bold flex items-center gap-1"
                            title="Combat Dashboard"
                        >
                            ⚔️ TACTICAL
                        </button>

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
                            onClick={() => setShowSettings(true)}
                            className="text-disco-accent hover:text-disco-paper transition-colors"
                            title="Settings"
                        >
                            ⚙️ Settings
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
                            onClick={() => setShowPractice(prev => !prev)}
                            className={`transition-colors flex items-center gap-1 ${showPractice ? 'text-white font-bold' : 'text-disco-cyan hover:text-white'}`}
                            title="Practice Cards - Master Your Voice"
                        >
                            🎤 Practice
                        </button>
                        <div className="w-px h-4 bg-disco-muted/30 mx-2"></div>
                        <MusicPlayer />
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
                        <button
                            onClick={() => setShowWorldEvents(true)}
                            className="text-amber-500 hover:text-white transition-colors"
                            title="Sector Intelligence & Events"
                        >
                            🌍 Log
                        </button>
                        <button
                            onClick={() => setShowStoryThreads(true)}
                            className="text-cyan-400 hover:text-white transition-colors"
                            title="Narrative Threads & Tension"
                        >
                            🧶 Story
                        </button>
                        <button
                            onClick={() => setShowQuestJournal(true)}
                            className="text-amber-500 hover:text-white transition-colors"
                            title="Quest Journal"
                        >
                            ⚔️ Quests
                        </button>
                        <button
                            onClick={() => setShowSensorRadar(true)}
                            className="text-cyan-400 hover:text-white transition-colors"
                            title="Sensor Radar"
                        >
                            🛰️ SENSORS
                        </button>
                        <button
                            onClick={() => setShowDebugger(true)}
                            className="text-pink-500 hover:text-white transition-colors"
                            title="NPC Cognitive Debugger"
                        >
                            🧠 Brain
                        </button>
                        <button
                            onClick={() => setShowWorldDashboard(true)}
                            className="text-emerald-400 hover:text-white transition-colors"
                            title="World Simulation Control"
                        >
                            🌍 SIM
                        </button>
                        <div className="w-px h-4 bg-disco-muted/30 mx-2"></div>
                        <button
                            onClick={() => setShowCamp(prev => !prev)}
                            className={`transition-colors font-bold ${showCamp ? 'text-white' : 'text-green-400 hover:text-white'}`}
                            title="Living Hub / Camp"
                        >
                            🏕️ CAMP
                        </button>
                        <div className="w-px h-4 bg-disco-muted/30 mx-2"></div>
                        <button
                            onClick={async () => {
                                if (confirm('Exit game and stop all servers?')) {
                                    try {
                                        await fetch('http://localhost:8000/api/shutdown', { method: 'POST' });
                                    } catch (e) {
                                        console.log('Server already stopped');
                                    }
                                    window.close();
                                }
                            }}
                            className="text-red-500 hover:text-white transition-colors font-bold"
                            title="Exit Game"
                        >
                            🚪 EXIT
                        </button>
                    </div>

                </div>
            </div>

            {/* World Dashboard Overlay */}
            <WorldDashboard
                visible={showWorldDashboard}
                onClose={() => setShowWorldDashboard(false)}
                sessionId="default"
            />

            {/* Sensor Radar Overlay */}
            <SensorRadar
                visible={showSensorRadar}
                onClose={() => setShowSensorRadar(false)}
                sessionId="default"
                playerLocation={{ x: 100, y: 100 }} // Mocked starting location near Engine Room
            />

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

            {/* Settings Modal */}
            <SettingsModal
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
                sessionId="default"
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

            {/* Camp View Overlay */}
            <CampView
                visible={showCamp}
                onClose={() => setShowCamp(false)}
                gameState={gameState}
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

            {/* Combat Dashboard Modal */}
            <CombatDashboard
                sessionId="default"
                visible={showCombatDashboard}
                onClose={() => setShowCombatDashboard(false)}
            />

            {/* Narrative Threads Modal */}
            {showStoryThreads && (
                <StoryThreads
                    onClose={() => setShowStoryThreads(false)}
                />
            )}

            {/* Quest Journal Modal */}
            {showQuestJournal && (
                <QuestJournal
                    onClose={() => setShowQuestJournal(false)}
                    sessionId="default"
                />
            )}

            {/* World Events Modal */}
            {showWorldEvents && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" onClick={() => setShowWorldEvents(false)}>
                    <div className="bg-gray-900 border border-amber-900/50 rounded-lg shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden" onClick={e => e.stopPropagation()}>
                        <WorldEvents sessionId="default" />
                        <div className="p-2 text-center border-t border-gray-800">
                            <button onClick={() => setShowWorldEvents(false)} className="text-gray-500 hover:text-white text-sm">Close Log</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Psyche Dashboard (Always On Widget) */}
            <PsycheDashboard />

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

            {/* NPC Debugger Modal */}
            <NPCDebugger
                sessionId="default"
                visible={showDebugger}
                onClose={() => setShowDebugger(false)}
            />

            {/* Murder Revelation Modal */}
            <MurderRevelationModal
                isOpen={showMurderRevelation}
                onClose={() => setShowMurderRevelation(false)}
                sessionId="default"
                onComplete={handleRevelationComplete}
            />

            {/* Hero/Tragedy Choice Modal */}
            <HeroTragedyChoice
                isOpen={showHeroTragedyChoice}
                onClose={() => setShowHeroTragedyChoice(false)}
                question={revelationQuestion}
                playerWound={playerWound}
                sessionId="default"
                onChoiceMade={handleChoiceMade}
                onComplete={() => setShowPortArrival(true)}
            />

            {/* Practice Cards View */}
            {showPractice && (
                <div className="fixed inset-0 z-[150] overflow-hidden">
                    <PracticeCards onClose={() => setShowPractice(false)} />
                    <button
                        onClick={() => setShowPractice(false)}
                        className="fixed top-8 right-8 z-[160] text-white/40 hover:text-white text-2xl"
                    >
                        ✕
                    </button>
                </div>
            )}

            {/* Interrogation Modal */}
            <InterrogationModal
                isOpen={showInterrogation}
                onClose={() => setShowInterrogation(false)}
                npcId={interrogationNPC.id}
                npcName={interrogationNPC.name}
                sessionId="default"
            />

            {/* Choice Crystallized Modal */}
            <ChoiceCrystallizedModal
                isOpen={showChoiceCrystallized}
                onClose={() => setShowChoiceCrystallized(false)}
                sessionId="default"
                onComplete={() => setShowChoiceCrystallized(false)}
            />

            {/* Generic Revelation Modal (Stages 1-3) */}
            <RevelationModal
                isOpen={showRevelation}
                onClose={() => {
                    setShowRevelation(false);
                    setRevelationStage(null);
                    setRevelationData(null);
                }}
                sessionId="default"
                stage={revelationStage}
                data={revelationData}
                onComplete={() => {
                    setShowRevelation(false);
                    setRevelationStage(null);
                    setRevelationData(null);
                }}
            />

            {/* Captain's Journal Modal */}
            <JournalModal
                isOpen={showJournal}
                onClose={() => setShowJournal(false)}
                sessionId="default"
            />

            {/* Port Arrival Modal */}
            <PortArrivalModal
                isOpen={showPortArrival}
                onClose={() => setShowPortArrival(false)}
                sessionId="default"
            />

            {/* Pause Menu (ESC) */}
            <PauseMenu
                isOpen={showPauseMenu}
                onClose={() => setShowPauseMenu(false)}
                onResume={() => setShowPauseMenu(false)}
                sessionId="default"
            />
        </div>
    )
}

export default Layout;
