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
import InterrogationModal from './components/InterrogationModal';
import { ReactiveStatic, ScanlineTransition, Starfield } from './components/UXEffects';
import TextScramble from './components/TextScramble';


const API_URL = 'http://localhost:8000/api';

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
    const [showInterrogation, setShowInterrogation] = useState(false);
    const [interrogationNPC, setInterrogationNPC] = useState({ id: '', name: '' });
    const [revelationStage, setRevelationStage] = useState(null);
    const [revelationData, setRevelationData] = useState(null);
    const [revelationQuestion, setRevelationQuestion] = useState('');
    const [playerWound, setPlayerWound] = useState('');
    const [activeStat, setActiveStat] = useState({ name: 'Iron', value: character.stats.iron });
    const [activeDrawer, setActiveDrawer] = useState(null); // 'sys' or 'codex'

    // Neuro-Status Logic (Derived from Spirit/Health)
    const isStabilityCritical = character.condition.spirit <= 2 || character.condition.health <= 1;

    // Visual Cortex: Determine Dominant Psyche Mode
    const psycheMode = useMemo(() => {
        const dominance = gameState.psyche?.voice_dominance || {};
        // Find aspect with highest dominance
        let maxKey = null;
        let maxVal = 0;

        for (const [key, val] of Object.entries(dominance)) {
            if (val > maxVal) {
                maxVal = val;
                maxKey = key;
            }
        }

        // Threshold for visual takeover (e.g. 0.6)
        if (maxVal > 0.6 && maxKey) {
            // Convert snake_case (brain_stem) to kebab-case (mode-brain-stem)
            const mode = maxKey.replace('_', '-');
            return `mode-${mode}`;
        }

        return '';
    }, [gameState.psyche?.voice_dominance]);

    // Accessibility and sound contexts
    const { highContrast, setHighContrast } = useAccessibility();
    const { toggleMute, playRandomGlitch } = useSoundEffects();
    const { speak, voiceEnabled, selectedVoice, isListening, startListening, stopListening, transcript, setTranscript, supported: voiceSupported } = useVoice();
    const [lastSpoken, setLastSpoken] = useState('');

    // Update input from voice transcript
    useEffect(() => {
        if (transcript) setInput(transcript);
    }, [transcript]);

    // Psyche Voice Mapping (Matches src/inner_voice.py)
    const PSYCHE_VOICE_MAP = useMemo(() => ({
        amygdala: {
            id: "21m00Tcm4TlvDq8ikWAM", // Rachel (Fear/Aggression)
            settings: { stability: 0.3, similarity_boost: 0.9 }
        },
        cortex: {
            id: "AZnzlk1XvdvUeBnXmlld", // Domi (Logic/Order)
            settings: { stability: 0.9, similarity_boost: 0.7 }
        },
        hippocampus: {
            id: "EXAVITQu4vr4xnSDxMaL", // Bella (Memory)
            settings: { stability: 0.5, similarity_boost: 0.5 }
        },
        brain_stem: {
            id: "ErXwobaYiN019PkySvjV", // Antoni (Survival/Pain)
            settings: { stability: 0.4, similarity_boost: 0.95 }
        },
        temporal: {
            id: "MF3mGyEYCl7XYWbV9V6O", // Distinct (Empathy/Social)
            settings: { stability: 0.8, similarity_boost: 0.8 }
        }
    }), []);

    // Auto-narrate new text with Psyche Voice
    useEffect(() => {
        if (voiceEnabled && selectedVoice && narrative.pending_narrative && !isLoading && narrative.pending_narrative !== lastSpoken) {

            // Determine voice override based on psyche dominance
            let voiceOverride = null;
            let settingsOverride = null;

            const dominance = gameState.psyche?.voice_dominance || {};
            let maxKey = null;
            let maxVal = 0;

            for (const [key, val] of Object.entries(dominance)) {
                if (val > maxVal) {
                    maxVal = val;
                    maxKey = key;
                }
            }

            // If dominance is strong enough, override the voice
            if (maxVal > 0.6 && maxKey && PSYCHE_VOICE_MAP[maxKey]) {
                voiceOverride = PSYCHE_VOICE_MAP[maxKey].id;
                settingsOverride = PSYCHE_VOICE_MAP[maxKey].settings;
                console.log(`[Layout] Psyche Dominance: ${maxKey} (${maxVal}). Switching voice.`);
            }

            speak(narrative.pending_narrative, {
                voiceId: voiceOverride,
                voiceSettings: settingsOverride
            });
            setLastSpoken(narrative.pending_narrative);
        }
    }, [narrative.pending_narrative, voiceEnabled, selectedVoice, isLoading, speak, lastSpoken, gameState.psyche?.voice_dominance, PSYCHE_VOICE_MAP]);

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

    // Jitter effect for Mission Log on progress update
    const prevProgressRef = useRef(chapterState.progress);
    const [logJitter, setLogJitter] = useState(false);

    useEffect(() => {
        if (chapterState.progress !== prevProgressRef.current) {
            setLogJitter(true);
            setTimeout(() => setLogJitter(false), 500);
            prevProgressRef.current = chapterState.progress;
        }
    }, [chapterState.progress]);


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

    // Helper for diegetic click effects
    const triggerRgbSplit = (e) => {
        if (playRandomGlitch) playRandomGlitch();
        const target = e.currentTarget;
        // Don't override if already animating or if it's an icon-only button without text might need handling
        const text = target.innerText || target.title || "CMD";
        target.setAttribute('data-text', text);
        target.classList.add('animate-rgb-split');
        setTimeout(() => target.classList.remove('animate-rgb-split'), 150);
    };

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
        <>
            <div className={`flex h-screen w-full bg-disco-bg bg-grunge bg-blend-multiply overflow-hidden relative psyche-transition ${psycheMode} transition-all duration-1000 ${isStabilityCritical ? 'neuro-critical' : 'animate-[crtFlicker_0.15s_infinite]'}`}>
                <Starfield count={150} speed={0.5} />
                <ReactiveStatic
                    health={character.condition.health}
                    spirit={character.condition.spirit}
                />
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
                    <div className="flex-1 overflow-y-auto p-12 scroll-smooth flex justify-center" ref={scrollRef}>
                        <div className="w-full max-w-prose space-y-12">
                            <div className="prose prose-invert prose-lg text-disco-paper/90 fade-in leading-loose">
                                <TypewriterText
                                    text={narrative.pending_narrative}
                                    characters={gameState.relationships?.crew || {}}
                                    baseSpeed={20}
                                    className="font-mono text-base leading-relaxed tracking-wide"
                                    onInterrogate={handleInterrogate}
                                    onComplete={() => {
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

                    {/* Command Deck - Stick Footer */}
                    <div className={`sticky bottom-0 bg-disco-bg border-t backdrop-blur-md transition-colors duration-500 z-50 ${conversationMode ? 'border-disco-cyan/60 bg-disco-cyan/5' : 'border-disco-muted/30'}`}>

                        {/* Drawer: System (Left) */}
                        <div className={`absolute bottom-full left-0 w-64 bg-black/90 border-r border-t border-disco-muted/40 p-4 transform transition-transform duration-300 ${activeDrawer === 'sys' ? 'translate-y-0' : 'translate-y-full opacity-0 pointer-events-none'}`}>
                            <ScanlineTransition trigger={activeDrawer === 'sys'}>
                                <div className="flex flex-col gap-2">
                                    <div className="text-xs font-mono text-disco-muted uppercase tracking-widest mb-2 border-b border-disco-muted/20 pb-1">
                                        <TextScramble text="SYSTEM CONTROLS" />
                                    </div>
                                    <button onClick={(e) => { triggerRgbSplit(e); setShowSaveManager(true); }} className="hover-jitter text-left px-3 py-2 text-disco-cyan hover:bg-white/10 text-sm font-mono">💾 Save/Load</button>
                                    <a href={`${API_URL}/export/story/default`} download className="hover-jitter text-left px-3 py-2 text-disco-yellow hover:bg-white/10 text-sm font-mono block">📤 Export Data</a>
                                    <div className="h-px bg-disco-muted/20 my-1"></div>
                                    <button
                                        onClick={async (e) => {
                                            triggerRgbSplit(e);
                                            if (confirm('Terminate uplink?')) {
                                                try { await fetch('http://localhost:8000/api/shutdown', { method: 'POST' }); } catch (e) { }
                                                window.close();
                                            }
                                        }}
                                        className="hover-jitter text-left px-3 py-2 text-disco-red hover:bg-red-900/20 text-sm font-mono font-bold">🛑 TERMINATE</button>
                                </div>
                            </ScanlineTransition>
                        </div>

                        {/* Drawer: Codex (Right) */}
                        <div className={`absolute bottom-full right-0 w-64 bg-black/90 hologram-panel border-l border-t border-disco-muted/40 p-4 transform transition-transform duration-300 ${activeDrawer === 'codex' ? 'translate-y-0' : 'translate-y-full opacity-0 pointer-events-none'}`}>
                            <ScanlineTransition trigger={activeDrawer === 'codex'}>
                                <div className="flex flex-col gap-2">
                                    <div className="text-xs font-mono text-disco-muted uppercase tracking-widest mb-2 border-b border-disco-muted/20 pb-1">
                                        <TextScramble text="DATABASE ACCESS" />
                                    </div>
                                    <button onClick={(e) => { triggerRgbSplit(e); setShowQuestJournal(true); }} className="hover-jitter text-left px-3 py-2 text-amber-500 hover:bg-white/10 text-sm font-mono">⚔️ Active Missions</button>
                                    <button onClick={(e) => { triggerRgbSplit(e); setShowStoryThreads(true); }} className="hover-jitter text-left px-3 py-2 text-cyan-400 hover:bg-white/10 text-sm font-mono">🧶 Narrative Threads</button>
                                    <button onClick={(e) => { triggerRgbSplit(e); setShowRumorBoard(true); }} className="hover-jitter text-left px-3 py-2 text-disco-orange hover:bg-white/10 text-sm font-mono">📡 Rumor Network</button>
                                    <button onClick={(e) => { triggerRgbSplit(e); setShowWorldEvents(true); }} className="hover-jitter text-left px-3 py-2 text-emerald-400 hover:bg-white/10 text-sm font-mono">🌍 Sector News</button>
                                    <button onClick={(e) => { triggerRgbSplit(e); setShowAlbum(true); }} className="hover-jitter text-left px-3 py-2 text-disco-purple hover:bg-white/10 text-sm font-mono">📸 Visual Records</button>
                                    <div className="h-px bg-disco-muted/20 my-1"></div>
                                    <button onClick={(e) => { triggerRgbSplit(e); setShowSensorRadar(true); }} className="hover-jitter text-left px-3 py-2 text-cyan-400 hover:bg-white/10 text-sm font-mono">🛰️ Sensor Array</button>
                                </div>
                            </ScanlineTransition>
                        </div>

                        <div className="max-w-7xl mx-auto px-6 py-4 flex items-end justify-between gap-6">

                            {/* LEFT GRID [SYS, INV, TAC, LOG] */}
                            <div className="grid grid-cols-2 gap-2 w-48 shrink-0">
                                {/* [SYS] */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setActiveDrawer(prev => prev === 'sys' ? null : 'sys'); }}
                                    className={`h-10 border text-xs font-mono font-bold tracking-wider hover-jitter transition-colors ${activeDrawer === 'sys' ? 'bg-disco-cyan text-black border-disco-cyan' : 'border-disco-muted/50 text-disco-muted hover:border-disco-cyan hover:text-disco-cyan'}`}
                                >
                                    [ SYS ]
                                </button>
                                {/* [INV] -> Camp */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setShowCamp(prev => !prev); }}
                                    className={`h-10 border text-xs font-mono font-bold tracking-wider hover-jitter transition-colors ${showCamp ? 'bg-disco-green text-black border-disco-green' : 'border-disco-muted/50 text-disco-muted hover:border-disco-green hover:text-disco-green'}`}
                                >
                                    [ INV ]
                                </button>
                                {/* [TAC] */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setShowCombatDashboard(true); }}
                                    className="h-10 border border-disco-muted/50 text-disco-muted/80 text-xs font-mono font-bold tracking-wider hover:border-disco-red hover:text-disco-red hover-jitter transition-colors"
                                >
                                    [ TAC ]
                                </button>
                                {/* [LOG] */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setShowRecap(true); }}
                                    className={`h-10 border border-disco-muted/50 text-disco-muted/80 text-xs font-mono font-bold tracking-wider hover:border-disco-accent hover:text-disco-accent hover-jitter transition-colors ${logJitter ? 'animate-quantum-jitter border-disco-cyan text-disco-cyan' : ''}`}
                                >
                                    [ LOG ]
                                </button>

                            </div>

                            {/* CENTER ANCHOR: INPUT */}
                            <div className="flex-1 relative max-w-2xl">
                                {/* Brackets around input */}
                                <div className="absolute -left-2 top-0 bottom-0 w-2 border-l border-t border-b border-disco-muted/30"></div>
                                <div className="absolute -right-2 top-0 bottom-0 w-2 border-r border-t border-b border-disco-muted/30"></div>

                                <form onSubmit={handleSubmit} className="relative group w-full">
                                    <VoiceInput />

                                    <div className="relative flex items-center">
                                        <div className={`absolute left-0 pl-4 font-mono text-xs pointer-events-none transition-colors ${conversationMode ? 'text-disco-cyan' : 'text-disco-accent'}`}>
                                            {conversationMode ? 'MSG_OUT >>' : 'CMD_IN >>'}
                                        </div>
                                        <input
                                            type="text"
                                            className={`w-full bg-black/80 border-2 font-serif text-xl py-4 pl-24 pr-16 focus:outline-none transition-all placeholder:text-disco-muted/20 ${conversationMode
                                                ? 'border-disco-cyan text-disco-cyan focus:shadow-[0_0_20px_rgba(34,211,238,0.2)]'
                                                : 'border-disco-muted text-disco-paper focus:border-disco-accent focus:shadow-[0_0_20px_rgba(253,224,71,0.1)]'
                                                }`}
                                            placeholder={conversationMode ? "Speak to them..." : "What do you do?"}
                                            value={input}
                                            onChange={(e) => setInput(e.target.value)}
                                            disabled={isLoading}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setConversationMode(prev => !prev)}
                                            className={`absolute right-2 p-2 rounded hover:bg-white/10 transition-colors ${conversationMode ? 'text-disco-cyan' : 'text-disco-muted'}`}
                                            title={conversationMode ? "Switch to Narrative Mode" : "Switch to Conversation Mode"}
                                        >
                                            {conversationMode ? "💬" : "📜"}
                                        </button>
                                    </div>
                                </form>

                                {/* Context Action Bar (Below Input) */}
                                <div className="flex justify-between mt-2 px-1">
                                    <div className="flex gap-2">
                                        <button onClick={(e) => { triggerRgbSplit(e); setShowSkillCheck(true); }} className="hover-jitter text-[10px] font-mono text-disco-muted hover:text-disco-accent uppercase tracking-wider">[R]oll</button>
                                        <button onClick={(e) => { triggerRgbSplit(e); setShowPractice(prev => !prev); }} className="hover-jitter text-[10px] font-mono text-disco-muted hover:text-disco-cyan uppercase tracking-wider">[P]ractice</button>
                                    </div>
                                    <div className="flex gap-2">
                                        <button onClick={(e) => { triggerRgbSplit(e); handleManualCapture(); }} className="hover-jitter text-[10px] font-mono text-disco-muted hover:text-disco-purple uppercase tracking-wider">[C]apture Frame</button>
                                    </div>
                                </div>
                            </div>

                            {/* RIGHT GRID [MAP, CODEX, CFG, ?] */}
                            <div className="grid grid-cols-2 gap-2 w-48 shrink-0">
                                {/* [MAP] */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setShowStarMap(true); }}
                                    className="h-10 border border-disco-muted/50 text-disco-muted/80 text-xs font-mono font-bold tracking-wider hover:border-disco-cyan hover:text-disco-cyan hover-jitter transition-colors"
                                >
                                    [ MAP ]
                                </button>
                                {/* [CODEX] */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setActiveDrawer(prev => prev === 'codex' ? null : 'codex'); }}
                                    className={`h-10 border text-xs font-mono font-bold tracking-wider hover-jitter transition-colors ${activeDrawer === 'codex' ? 'bg-amber-500 text-black border-amber-500' : 'border-disco-muted/50 text-disco-muted hover:border-amber-500 hover:text-amber-500'}`}
                                >
                                    [ CODEX ]
                                </button>
                                {/* [CFG] */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setShowSettings(true); }}
                                    className="h-10 border border-disco-muted/50 text-disco-muted/80 text-xs font-mono font-bold tracking-wider hover:border-white hover:text-white hover-jitter transition-colors"
                                >
                                    [ CFG ]
                                </button>
                                {/* [ ? ] */}
                                <button
                                    onClick={(e) => { triggerRgbSplit(e); setShowHelp(true); }}
                                    className="h-10 border border-disco-muted/50 text-disco-muted/80 text-xs font-mono font-bold tracking-wider hover:border-white hover:text-white hover-jitter transition-colors"
                                >
                                    [ ? ]
                                </button>
                            </div>

                        </div>
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
            {
                showSkillCheck && (
                    <SkillCheck
                        stat={character.stats.iron}
                        statName="Iron"
                        character={character}
                        onRollComplete={handleRollComplete}
                        onClose={() => setShowSkillCheck(false)}
                    />
                )
            }

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
            {
                showStoryThreads && (
                    <StoryThreads
                        onClose={() => setShowStoryThreads(false)}
                    />
                )
            }

            {/* Quest Journal Modal */}
            {
                showQuestJournal && (
                    <QuestJournal
                        onClose={() => setShowQuestJournal(false)}
                        sessionId="default"
                    />
                )
            }

            {/* World Events Modal */}
            {
                showWorldEvents && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" onClick={() => setShowWorldEvents(false)}>
                        <div className="bg-gray-900 border border-amber-900/50 rounded-lg shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden" onClick={e => e.stopPropagation()}>
                            <WorldEvents sessionId="default" />
                            <div className="p-2 text-center border-t border-gray-800">
                                <button onClick={() => setShowWorldEvents(false)} className="text-gray-500 hover:text-white text-sm">Close Log</button>
                            </div>
                        </div>
                    </div>
                )
            }

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
            {
                showPractice && (
                    <div className="fixed inset-0 z-[150] overflow-hidden">
                        <PracticeCards onClose={() => setShowPractice(false)} />
                        <button
                            onClick={() => setShowPractice(false)}
                            className="fixed top-8 right-8 z-[160] text-white/40 hover:text-white text-2xl"
                        >
                            ✕
                        </button>
                    </div>
                )
            }

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
        </>
    );
}

export default Layout;
