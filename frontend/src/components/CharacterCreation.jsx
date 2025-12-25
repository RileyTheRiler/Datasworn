import React, { useState, useEffect } from 'react';
import CalibrationStep from './CalibrationStep';
import { useVoice } from '../contexts/VoiceContext';
import TTSButton from './TTSButton';
import VoiceSelector from './VoiceSelector';
import MusicPlayer from './MusicPlayer';

const API_URL = 'http://localhost:8000/api';

/**
 * CharacterCreation - Multi-step wizard for new character creation
 * Steps: 1) Identity (Name, Archetype, Look) 2) Stats 3) Assets 4) Vow 5) Review
 */

const ARCHETYPES = {
    "Bounty Hunter": {
        description: "A relentless pursuer of targets across the sector.",
        visual: "Scarred armor, tactical visor, heavy weapons, determined gaze.",
        stats: { edge: 2, heart: 1, iron: 3, shadow: 1, wits: 2 },
        assets: ["Slayer", "Ironclad", "Combat Bot"]
    },
    "Courier": {
        description: "Delivering cargo and data to the most dangerous corners of the Forge.",
        visual: "Flight jacket, worn leather equipment, confident smirk, goggles.",
        stats: { edge: 3, heart: 1, iron: 1, shadow: 2, wits: 2 },
        assets: ["Navigator", "Overdrive", "Starship"]
    },
    "Mystic": {
        description: "Wielding strange powers and unearthing ancient secrets.",
        visual: "Robes or tattered cloaks, glowing artifacts, haunted eyes, mysterious symbols.",
        stats: { edge: 1, heart: 2, iron: 1, shadow: 2, wits: 3 },
        assets: ["Sighted", "Communion", "Sprite"]
    },
    "Mercenary": {
        description: "Fighting for coin, honor, or the thrill of battle.",
        visual: "Battle-worn power armor, scars, military haircut, imposing stance.",
        stats: { edge: 1, heart: 2, iron: 3, shadow: 1, wits: 2 },
        assets: ["Blade-Bound", "Skirmisher", "Hound"]
    },
    "Scavenger": {
        description: "Finding value in the refuse of the precursors and the lost.",
        visual: "Patchwork tech gear, multi-tool belt, grease stains, wary expression.",
        stats: { edge: 2, heart: 1, iron: 1, shadow: 3, wits: 2 },
        assets: ["Scavenger", "Grappler", "Drone"]
    }
};

const STAT_CONFIG = {
    edge: { label: "KINETICS", desc: "Speed, agility, reflex", code: "K" },
    heart: { label: "PSYCHE", desc: "Willpower, empathy, spirit", code: "P" },
    iron: { label: "FORCE", desc: "Strength, endurance, combat", code: "F" },
    shadow: { label: "VEIL", desc: "Stealth, trickery, subterfuge", code: "V" },
    wits: { label: "LOGIC", desc: "Knowledge, perception, tech", code: "L" }
};

const CharacterCreation = ({ onComplete, onCancel }) => {
    const [step, setStep] = useState(0);  // Start at 0 for story template selection
    const [loading, setLoading] = useState(false);
    const [availableAssets, setAvailableAssets] = useState({});
    const [createdSessionId, setCreatedSessionId] = useState(null); // For calibration step
    const [quickstartCharacters, setQuickstartCharacters] = useState([]);
    const [storyTemplates, setStoryTemplates] = useState([]);
    const [selectedQuickstart, setSelectedQuickstart] = useState(null);
    const [selectedStoryTemplate, setSelectedStoryTemplate] = useState(null);

    // Character data
    const [name, setName] = useState('');
    const [archetype, setArchetype] = useState('');
    const [visualDescription, setVisualDescription] = useState('');
    const [background, setBackground] = useState(''); // Narrative background
    const [stats, setStats] = useState({
        edge: 1,
        heart: 2,
        iron: 1,
        shadow: 1,
        wits: 2
    });
    const [selectedAssets, setSelectedAssets] = useState([]);
    const [vow, setVow] = useState('');

    // Stat points remaining (9 total: must sum to 9)
    const totalPoints = 9;
    const usedPoints = Object.values(stats).reduce((a, b) => a + b, 0);
    const remaining = totalPoints - usedPoints;

    // Load available assets, quick-start characters, and story templates on mount
    useEffect(() => {
        fetch(`${API_URL}/assets/available`)
            .then(res => res.json())
            .then(data => setAvailableAssets(data.assets || {}))
            .catch(console.error);

        fetch(`${API_URL}/quickstart/characters`)
            .then(res => res.json())
            .then(data => setQuickstartCharacters(data.characters || []))
            .catch(console.error);

        fetch(`${API_URL}/story/templates`)
            .then(res => res.json())
            .then(data => setStoryTemplates(data.templates || []))
            .catch(console.error);
    }, []);

    const handleArchetypeSelect = (role) => {
        setArchetype(role);
        const data = ARCHETYPES[role];
        if (data) {
            setVisualDescription(data.visual);
            setStats(data.stats);
            // Pre-select assets if we can match them to IDs? 
            // For now, we'll just set them as strings, assuming the backend can handle loose matching or we'll filter later
            // The backend expects IDs, but the current UI just sends names.
            // We should ideally verify these against availableAssets, but for MVP just setting them is fine.
            // The user can modify them in step 3.
            setSelectedAssets(data.assets);
        }
    };

    const handleStatChange = (stat, delta) => {
        const newVal = stats[stat] + delta;
        if (newVal >= 1 && newVal <= 3) {
            const newUsed = usedPoints + delta;
            if (newUsed <= totalPoints) {
                setStats({ ...stats, [stat]: newVal });
            }
        }
    };

    const toggleAsset = (assetName) => {
        if (selectedAssets.includes(assetName)) {
            setSelectedAssets(selectedAssets.filter(a => a !== assetName));
        } else if (selectedAssets.length < 3) {
            setSelectedAssets([...selectedAssets, assetName]);
        }
    };

    const handleCreate = async () => {
        setLoading(true);
        try {
            const payload = selectedQuickstart
                ? {
                    quickstart_id: selectedQuickstart.id,
                    story_template_id: selectedStoryTemplate?.id
                }
                : {
                    character_name: name,
                    background_vow: vow || "Find my place among the stars",
                    stats: stats,
                    asset_ids: selectedAssets,
                    background: background || visualDescription,
                    story_template_id: selectedStoryTemplate?.id
                };

            const res = await fetch(`${API_URL}/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.session_id) {
                // Instead of completing, trigger calibration
                setCreatedSessionId(data.session_id);
            }
        } catch (err) {
            console.error('Character creation failed:', err);
        } finally {
            setLoading(false);
        }
    };

    const canProceed = () => {
        switch (step) {
            case 0: return true; // Story template selection is optional
            case 1: return true; // Character selection is optional
            case 2: return selectedQuickstart || name.trim().length >= 2;
            case 3: return selectedQuickstart || remaining === 0;
            case 4: return true; // Assets optional
            case 5: return true; // Vow optional (has default)
            case 6: return true; // Review
            default: return true;
        }
    };

    // --- Helper for Progress Bar ---
    const ProgressBar = () => {
        const totalSteps = 6;
        return (
            <div className="flex items-center gap-2 font-mono text-disco-cyan text-lg">
                <span className="text-disco-muted opacity-50">[</span>
                {[...Array(totalSteps)].map((_, i) => (
                    <span key={i} className={`transition-all duration-300 ${i <= step ? "text-disco-cyan text-glow text-xl" : "text-disco-muted opacity-20"}`}>
                        {i <= step ? "■" : "□"}
                    </span>
                ))}
                <span className="text-disco-muted opacity-50">]</span>
            </div>
        );
    };

    // --- Helper for Terminal Card ---
    const TerminalCard = ({ title, subtitle, description, isSelected, onClick, children }) => {
        return (
            <div
                onClick={onClick}
                className={`terminal-card ${isSelected ? 'selected' : ''}`}
            >
                <div className="terminal-corner card-tl"></div>
                <div className="terminal-corner card-tr"></div>
                <div className="terminal-corner card-bl"></div>
                <div className="terminal-corner card-br"></div>

                <h4 className="font-mono text-disco-cyan text-lg mb-2 tracking-wider uppercase text-glow border-b border-disco-cyan/20 pb-2 w-full text-center">
                    [ {title} ]
                </h4>

                {/* Icon Placeholder area - thematic */}
                <div className="w-16 h-16 mx-auto my-4 border border-disco-cyan/30 flex items-center justify-center bg-disco-cyan/5">
                    <div className="w-12 h-12 border border-disco-cyan/20 rotate-45 transform transition-transform duration-1000 group-hover:rotate-90"></div>
                </div>

                {subtitle && <div className="text-xs text-disco-accent font-mono mb-4 text-center uppercase tracking-widest">{subtitle}</div>}

                <div className="text-sm text-disco-paper/80 font-mono leading-relaxed mb-4 flex-grow text-justify">
                    {description}
                </div>

                {children}
            </div>
        );
    };

    const renderStep = () => {
        // If quick-start selected (skipping detailed creation)
        if (selectedQuickstart && step > 1 && step < 6) {
            return (
                <div className="max-w-4xl mx-auto w-full">
                    <h3 className="text-2xl text-disco-cyan font-mono mb-8 text-center uppercase tracking-[0.2em] text-glow">
                       // UPLOADING PRESET: {selectedQuickstart.title}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="terminal-card shadow-lg shadow-disco-cyan/5">
                            <h4 className="font-mono text-disco-muted mb-4 border-b border-disco-muted/20 pb-1">IDENTITY RECORD</h4>
                            <div className="space-y-4 font-mono text-sm">
                                <div><span className="text-disco-accent">NAME:</span> <span className="text-disco-paper ml-2">{selectedQuickstart.name}</span></div>
                                <div><span className="text-disco-accent">ORIGIN:</span> <span className="text-disco-paper ml-2">{selectedQuickstart.description}</span></div>
                                <div><span className="text-disco-accent">VOW:</span> <span className="text-disco-paper ml-2 italic">"{selectedQuickstart.vow}"</span></div>
                            </div>
                        </div>
                        <div className="terminal-card shadow-lg shadow-disco-cyan/5">
                            <h4 className="font-mono text-disco-muted mb-4 border-b border-disco-muted/20 pb-1">COMBAT CAPABILITIES</h4>
                            <div className="font-mono text-disco-cyan text-xl mb-6 tracking-widest">
                                {Object.entries(selectedQuickstart.stats).map(([key, val]) => (
                                    <span key={key} className="mr-3">
                                        {STAT_CONFIG[key]?.code}{val}
                                    </span>
                                ))}
                            </div>
                            <h4 className="font-mono text-disco-muted mb-2 border-b border-disco-muted/20 pb-1">ASSETS</h4>
                            <div className="text-disco-accent font-mono text-sm leading-relaxed">
                                {selectedQuickstart.asset_ids.join(' // ')}
                            </div>
                        </div>
                    </div>
                </div>
            )
        }

        switch (step) {
            case 0:
                return (
                    <div className="w-full max-w-6xl mx-auto">
                        <div className="text-center mb-12">
                            <h3 className="text-3xl text-disco-cyan font-mono tracking-[0.2em] mb-2 text-glow">PHASE 1: ORIGIN STORY</h3>
                            <p className="text-disco-muted font-mono text-sm uppercase tracking-widest">Select Narrative Parameter</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            {storyTemplates.map(template => (
                                <TerminalCard
                                    key={template.id}
                                    title={template.name}
                                    subtitle={template.tagline}
                                    description={template.description}
                                    isSelected={selectedStoryTemplate?.id === template.id}
                                    onClick={() => setSelectedStoryTemplate(template)}
                                >
                                    <div className="mt-4 pt-4 border-t border-disco-muted/20 flex justify-between text-xs font-mono text-disco-muted opacity-70">
                                        <span>[ TONE: {template.tone} ]</span>
                                        <span>[ DIFF: {template.difficulty} ]</span>
                                    </div>
                                </TerminalCard>
                            ))}
                        </div>
                    </div>
                );

            case 1:
                return (
                    <div className="w-full max-w-6xl mx-auto">
                        <div className="text-center mb-12">
                            <h3 className="text-3xl text-disco-cyan font-mono tracking-[0.2em] mb-2 text-glow">PHASE 2: BIOMETRIC SCAN</h3>
                            <p className="text-disco-muted font-mono text-sm uppercase tracking-widest">Select Operative Profile</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 overflow-y-auto max-h-[60vh] p-4">
                            {/* Custom Character Option */}
                            <TerminalCard
                                title="CUSTOM OPERATIVE"
                                subtitle="Build from scratch"
                                description="Manual entry of all biometric and psychological parameters."
                                isSelected={selectedQuickstart === null}
                                onClick={() => {
                                    setSelectedQuickstart(null);
                                    setStep(2);
                                }}
                            />

                            {/* Detailed Quickstarts */}
                            {quickstartCharacters.map(char => (
                                <TerminalCard
                                    key={char.id}
                                    title={char.name}
                                    subtitle={char.title}
                                    description={char.description}
                                    isSelected={selectedQuickstart?.id === char.id}
                                    onClick={() => setSelectedQuickstart(char)}
                                />
                            ))}
                        </div>
                    </div>
                );

            case 2:
                // Identity Input
                return (
                    <div className="w-full max-w-2xl mx-auto">
                        <div className="text-center mb-12">
                            <h3 className="text-3xl text-disco-cyan font-mono tracking-[0.2em] mb-2 text-glow">PHASE 3: IDENTITY RECORD</h3>
                        </div>

                        <div className="terminal-card p-12 space-y-8">
                            <div>
                                <label className="block text-sm text-disco-cyan font-mono mb-2 tracking-widest decoration-clone uppercase"> &gt;&gt; Enter Designation ID</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={e => setName(e.target.value)}
                                    placeholder="ERROR: NO NAME FOUND"
                                    className="w-full bg-black/50 border-b-2 border-disco-muted px-4 py-3 text-disco-paper text-2xl font-mono focus:border-disco-cyan focus:outline-none transition-colors"
                                    autoFocus
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-disco-cyan font-mono mb-2 tracking-widest uppercase"> &gt;&gt; Background Data</label>
                                <textarea
                                    value={background}
                                    onChange={e => setBackground(e.target.value)}
                                    placeholder="Input historical data..."
                                    className="w-full bg-black/50 border border-disco-muted/30 p-4 text-disco-paper font-mono focus:border-disco-cyan focus:outline-none h-32 resize-none text-sm"
                                />
                            </div>
                        </div>
                    </div>
                );

            case 3:
                // Stats
                return (
                    <div className="w-full max-w-3xl mx-auto">
                        <div className="text-center mb-12">
                            <h3 className="text-3xl text-disco-cyan font-mono tracking-[0.2em] mb-2 text-glow">PHASE 4: ATTRIBUTE CALIBRATION</h3>
                            <p className={`font-mono text-sm tracking-widest ${remaining === 0 ? 'text-disco-cyan' : 'text-disco-accent'}`}>
                                [ POINTS AVAILABLE: {remaining} ]
                            </p>
                        </div>

                        <div className="grid grid-cols-1 gap-4">
                            {Object.entries(stats).map(([stat, value]) => (
                                <div key={stat} className="flex items-center justify-between p-4 border border-disco-muted/20 hover:border-disco-cyan/50 transition-colors bg-black/40 group">
                                    <div className="flex-1">
                                        <div className="font-mono text-disco-paper text-xl uppercase tracking-widest flex items-center gap-2 group-hover:text-disco-cyan transition-colors">
                                            {STAT_CONFIG[stat]?.label || stat}
                                            <span className="text-xs text-disco-muted normal-case opacity-50 ml-4 hidden md:inline-block">
                                                // {STAT_CONFIG[stat]?.desc}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <button
                                            onClick={() => handleStatChange(stat, -1)}
                                            disabled={value <= 1}
                                            className="w-12 h-12 flex items-center justify-center border border-disco-muted/50 text-disco-muted hover:text-disco-cyan hover:border-disco-cyan disabled:opacity-20 transition-all text-xl font-mono"
                                        >-</button>
                                        <span className="w-8 text-center text-3xl font-mono text-disco-cyan font-bold">{value}</span>
                                        <button
                                            onClick={() => handleStatChange(stat, 1)}
                                            disabled={value >= 3 || remaining <= 0}
                                            className="w-12 h-12 flex items-center justify-center border border-disco-muted/50 text-disco-muted hover:text-disco-cyan hover:border-disco-cyan disabled:opacity-20 transition-all text-xl font-mono"
                                        >+</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                );

            case 4:
                // Assets
                return (
                    <div className="w-full max-w-6xl mx-auto h-full flex flex-col">
                        <div className="text-center mb-8 shrink-0">
                            <h3 className="text-3xl text-disco-cyan font-mono tracking-[0.2em] mb-2 text-glow">PHASE 5: ASSET ACQUISITION</h3>
                            <p className="text-disco-muted font-mono text-sm uppercase tracking-widest">
                                [ SLOTS OCCUPIED: {selectedAssets.length} / 3 ]
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 overflow-y-auto pr-2 pb-4">
                            {Object.entries(availableAssets).map(([type, assets]) => (
                                <div key={type} className="col-span-full">
                                    <h4 className="font-mono text-disco-accent border-b border-disco-accent/30 mb-4 pb-1 inline-block pr-8 uppercase tracking-widest">{type}</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                        {assets.slice(0, 8).map(asset => {
                                            const isSelected = selectedAssets.includes(asset.name);
                                            const canSelect = selectedAssets.length < 3 || isSelected;
                                            return (
                                                <TerminalCard
                                                    key={asset.name}
                                                    title={asset.name}
                                                    isSelected={isSelected}
                                                    onClick={() => canSelect && toggleAsset(asset.name)}
                                                >
                                                    <div className="text-xs text-disco-muted/80 font-mono min-h-[4rem]">
                                                        {asset.abilities && asset.abilities[0]}
                                                    </div>
                                                </TerminalCard>
                                            )
                                        })}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )

            case 5:
                // Vow
                return (
                    <div className="w-full max-w-3xl mx-auto">
                        <div className="text-center mb-12">
                            <h3 className="text-3xl text-disco-cyan font-mono tracking-[0.2em] mb-2 text-glow">PHASE 6: MISSION PARAMETERS</h3>
                            <p className="text-disco-muted font-mono text-sm uppercase tracking-widest">Initialize Iron Vow</p>
                        </div>

                        <div className="terminal-card p-12">
                            <label className="block text-sm text-disco-cyan font-mono mb-4 tracking-widest uppercase"> &gt;&gt; Swear Oath</label>
                            <textarea
                                value={vow}
                                onChange={e => setVow(e.target.value)}
                                placeholder="State your mission..."
                                className="w-full bg-black/50 border border-disco-muted/50 p-6 text-disco-paper text-lg font-mono focus:border-disco-cyan focus:outline-none h-48 resize-none mb-6"
                            />

                            <div className="flex flex-wrap gap-3">
                                <span className="text-disco-muted font-mono text-xs self-center mr-2 uppercase">Suggested Protocols:</span>
                                {[
                                    "Isolate the anomaly",
                                    "Save the colony",
                                    "Hunt the traitor"
                                ].map(v => (
                                    <button
                                        key={v}
                                        onClick={() => setVow(v)}
                                        className="px-3 py-1 border border-disco-muted/30 text-disco-muted font-mono text-xs hover:border-disco-cyan hover:text-disco-cyan transition-colors uppercase"
                                    >
                                        {v}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )

            case 6:
                // Final Review
                return (
                    <div className="w-full max-w-3xl mx-auto">
                        <div className="text-center mb-12">
                            <h3 className="text-3xl text-disco-cyan font-mono tracking-[0.2em] mb-2 text-glow">INITIALIZATION SEQUENCE READY</h3>
                            <p className="text-disco-muted font-mono text-sm uppercase tracking-widest">Confirm Launch Parameters</p>
                        </div>

                        <div className="terminal-card space-y-4 p-8">
                            <div className="flex justify-between border-b border-disco-muted/30 pb-2">
                                <span className="font-mono text-disco-muted">OPERATIVE:</span>
                                <span className="font-mono text-disco-paper text-xl">{name}</span>
                            </div>
                            <div className="flex justify-between border-b border-disco-muted/30 pb-2">
                                <span className="font-mono text-disco-muted">STATS:</span>
                                <span className="font-mono text-disco-cyan">
                                    {Object.entries(stats).map(([key, val]) => (
                                        <span key={key} className="mr-3">
                                            {STAT_CONFIG[key]?.code}{val}
                                        </span>
                                    ))}
                                </span>
                            </div>
                            <div className="flex justify-between border-b border-disco-muted/30 pb-2">
                                <span className="font-mono text-disco-muted">ASSETS:</span>
                                <span className="font-mono text-disco-accent">{selectedAssets.join(' // ')}</span>
                            </div>
                            <div className="border-b border-disco-muted/30 pb-2">
                                <div className="font-mono text-disco-muted mb-1">MISSION:</div>
                                <div className="font-mono text-disco-paper italic">"{vow}"</div>
                            </div>
                        </div>
                    </div>
                )
        }
    }

    return (
        <div className="fixed inset-0 z-50 bg-black text-disco-paper font-sans flex flex-col overflow-hidden">
            {/* Background Effects */}
            <div className="absolute inset-0 scanline-grid opacity-30 pointer-events-none"></div>
            <div className="wireframe-globe opacity-20 pointer-events-none"></div>

            {/* Header / Nav */}
            <div className="relative z-10 w-full p-6 border-b border-disco-muted/20 flex justify-between items-center bg-black/80 backdrop-blur-sm">
                <div className="flex items-center gap-4">
                    <h2 className="text-2xl font-mono text-disco-cyan tracking-widest uppercase text-glow">
                        // FORGE_TERMINAL //
                    </h2>
                    <span className="text-xs font-mono text-disco-muted border px-2 py-0.5 border-disco-muted/50 rounded opacity-50">
                        v.4.9.2
                    </span>
                </div>

                <ProgressBar />
            </div>

            {/* Main Content Area */}
            <div className="relative z-10 flex-1 overflow-auto p-8 flex items-start justify-center">
                {createdSessionId ? (
                    <div className="w-full max-w-2xl mx-auto">
                        <CalibrationStep
                            sessionId={createdSessionId}
                            onComplete={async () => {
                                /* Same logic as before */
                                try {
                                    const res = await fetch(`${API_URL}/state/${createdSessionId}`);
                                    const state = await res.json();
                                    onComplete({ session_id: createdSessionId, state: state });
                                } catch (err) {
                                    onComplete({ session_id: createdSessionId });
                                }
                            }}
                        />
                    </div>
                ) : (
                    renderStep()
                )}
            </div>

            {/* Footer / Controls */}
            <div className="relative z-10 w-full p-8 border-t border-disco-muted/20 bg-black/90 backdrop-blur-md flex justify-between items-center mt-auto">
                <button
                    onClick={() => {
                        if (step > 0) {
                            if (selectedQuickstart && step === 2) {
                                setStep(1);
                                setSelectedQuickstart(null);
                            } else {
                                setStep(step - 1);
                            }
                        } else {
                            onCancel?.();
                        }
                    }}
                    className="font-mono text-disco-muted hover:text-disco-red transition-colors text-sm uppercase tracking-widest flex items-center gap-2 group"
                >
                    <span className="group-hover:-translate-x-1 transition-transform">[ &lt; ABORT ]</span>
                </button>

                {(selectedQuickstart && step > 1) || step >= 6 ? (
                    <button
                        onClick={handleCreate}
                        disabled={loading}
                        className="btn-terminal"
                    >
                        {loading ? 'INITIALIZING...' : '[ LAUNCH_GAME ]'}
                    </button>
                ) : (
                    <button
                        onClick={() => {
                            if (selectedQuickstart && step === 1) {
                                setStep(2);  // Jump to review for quick-start
                            } else {
                                setStep(step + 1);
                            }
                        }}
                        disabled={!canProceed()}
                        className="btn-terminal disabled:opacity-30 disabled:cursor-not-allowed group"
                    >
                        <span className="group-hover:text-black">[ INITIATE PHASE {step + 2} &gt; ]</span>
                    </button>
                )}
            </div>

            {/* Music Player - Bottom Left */}
            <div className="absolute bottom-6 left-6 z-20 opacity-50 hover:opacity-100 transition-opacity">
                <MusicPlayer />
            </div>
        </div>
    );
};

/**
 * VowSuggestions - Fetches and displays context-aware vow suggestions based on selected assets
 */
const VowSuggestions = ({ selectedAssets, onSelect }) => {
    const [vows, setVows] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchVows = async () => {
            if (selectedAssets.length === 0) {
                setVows([]);
                setLoading(false);
                return;
            }

            setLoading(true);
            try {
                // Fetch vows for the first selected asset (primary path)
                const primaryAsset = selectedAssets[0];
                const res = await fetch(`${API_URL}/narrative/vows/${primaryAsset}`);
                const data = await res.json();
                setVows(data.suggested_vows || []);
            } catch (err) {
                console.error('Failed to fetch vow suggestions:', err);
                setVows([]);
            } finally {
                setLoading(false);
            }
        };

        fetchVows();
    }, [selectedAssets]);

    if (loading) {
        return <div className="text-disco-muted text-xs">Loading suggestions...</div>;
    }

    if (vows.length === 0) {
        return null;
    }

    return (
        <div className="flex flex-wrap gap-2 mt-2">
            {vows.map((v, idx) => (
                <button
                    key={idx}
                    onClick={() => onSelect(v)}
                    className="px-2 py-1 text-xs border border-disco-muted/30 hover:border-disco-cyan
                             hover:text-disco-cyan transition-colors text-left"
                >
                    {v}
                </button>
            ))}
        </div>
    );
};

export default CharacterCreation;
