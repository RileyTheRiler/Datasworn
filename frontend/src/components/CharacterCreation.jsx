import React, { useState, useEffect } from 'react';
import CalibrationStep from './CalibrationStep';
import TTSButton from './TTSButton';
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

    const renderStep = () => {
        // If quick-start selected, skip to review
        if (selectedQuickstart && step > 1 && step < 6) {
            return (
                <div className="space-y-6">
                    <h3 className="text-xl text-disco-cyan font-mono">{selectedQuickstart.title}</h3>

                    <div className="space-y-4">
                        <div>
                            <div className="text-sm text-disco-muted mb-2">Character</div>
                            <div className="text-disco-paper font-serif text-lg">{selectedQuickstart.name}</div>
                        </div>

                        <div>
                            <div className="text-sm text-disco-muted mb-2">Description</div>
                            <div className="text-disco-paper text-sm">{selectedQuickstart.description}</div>
                        </div>

                        <div>
                            <div className="text-sm text-disco-muted mb-2">Background</div>
                            <div className="text-disco-paper text-sm whitespace-pre-line max-h-48 overflow-y-auto">
                                {selectedQuickstart.background_story}
                            </div>
                        </div>

                        <div>
                            <div className="text-sm text-disco-muted mb-2">Stats</div>
                            <div className="text-disco-cyan font-mono">
                                Edge {selectedQuickstart.stats.edge} | Heart {selectedQuickstart.stats.heart} | Iron {selectedQuickstart.stats.iron} | Shadow {selectedQuickstart.stats.shadow} | Wits {selectedQuickstart.stats.wits}
                            </div>
                        </div>

                        <div>
                            <div className="text-sm text-disco-muted mb-2">Starting Assets</div>
                            <div className="text-disco-accent">{selectedQuickstart.asset_ids.join(', ')}</div>
                        </div>

                        <div>
                            <div className="text-sm text-disco-muted mb-2">Starting Vow</div>
                            <div className="text-disco-paper italic text-sm">"{selectedQuickstart.vow}"</div>
                        </div>
                    </div>
                </div>
            );
        }

        switch (step) {
            case 0:
                return (
                    <div className="space-y-6">
                        <h3 className="text-xl text-disco-cyan font-mono">Choose Your Story</h3>
                        <p className="text-sm text-disco-muted">
                            Select a story template to set the scene for your adventure, or skip to create your own setting.
                        </p>

                        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                            {storyTemplates.map(template => (
                                <button
                                    key={template.id}
                                    onClick={() => setSelectedStoryTemplate(template)}
                                    className={`w-full p-4 text-left border transition-all ${selectedStoryTemplate?.id === template.id
                                        ? 'border-disco-cyan bg-disco-cyan/10'
                                        : 'border-disco-muted/30 hover:border-disco-muted bg-disco-bg/50'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex-1">
                                            <div className="font-mono text-disco-paper">{template.name}</div>
                                            <div className="text-xs text-disco-accent">{template.tagline}</div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <TTSButton text={`${template.name}. ${template.description}`} className="shrink-0" asSpan={true} />
                                            {selectedStoryTemplate?.id === template.id && (
                                                <span className="text-disco-cyan text-xs">✓ Selected</span>
                                            )}
                                        </div>
                                    </div>
                                    <div className={`text-xs text-disco-muted ${selectedStoryTemplate?.id === template.id ? 'whitespace-pre-wrap' : 'line-clamp-2'}`}>{template.description}</div>
                                    <div className="flex gap-2 mt-2">
                                        <span className="text-xs px-2 py-0.5 border border-disco-muted/30 text-disco-muted">
                                            {template.tone}
                                        </span>
                                        <span className="text-xs px-2 py-0.5 border border-disco-muted/30 text-disco-muted">
                                            {template.difficulty}
                                        </span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                );

            case 1:
                return (
                    <div className="space-y-6">
                        <h3 className="text-xl text-disco-cyan font-mono">Choose Your Character</h3>
                        <p className="text-sm text-disco-muted">
                            Select a quick-start character to jump into the action, or create a custom character from scratch.
                        </p>

                        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                            {quickstartCharacters.map(char => (
                                <button
                                    key={char.id}
                                    onClick={() => setSelectedQuickstart(char)}
                                    className={`w-full p-4 text-left border transition-all ${selectedQuickstart?.id === char.id
                                        ? 'border-disco-cyan bg-disco-cyan/10'
                                        : 'border-disco-muted/30 hover:border-disco-muted bg-disco-bg/50'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex-1">
                                            <div className="font-mono text-disco-paper">{char.name}</div>
                                            <div className="text-xs text-disco-accent">{char.title}</div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <TTSButton text={`${char.name}. ${char.description}`} className="shrink-0" asSpan={true} />
                                            {selectedQuickstart?.id === char.id && (
                                                <span className="text-disco-cyan text-xs">✓ Selected</span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="text-xs text-disco-muted line-clamp-2">{char.description}</div>
                                </button>
                            ))}

                            <button
                                onClick={() => {
                                    setSelectedQuickstart(null);
                                    setStep(2);
                                }}
                                className="w-full p-4 text-left border border-disco-muted/30 hover:border-disco-cyan
                                         bg-disco-bg/50 transition-all"
                            >
                                <div className="font-mono text-disco-paper mb-1">Custom Character</div>
                                <div className="text-xs text-disco-muted">Create your own unique character from scratch</div>
                            </button>
                        </div>
                    </div>
                );

            case 2:
                return (
                    <div className="space-y-6">
                        <h3 className="text-xl text-disco-cyan font-mono">Who are you?</h3>

                        <div>
                            <label className="block text-sm text-disco-muted mb-2">Character Name</label>
                            <input
                                type="text"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                placeholder="Enter your name..."
                                className="w-full bg-disco-bg border border-disco-muted/50 px-4 py-3 text-disco-paper
                                         text-xl font-serif focus:border-disco-cyan focus:outline-none"
                                autoFocus
                            />
                        </div>

                        <div>
                            <label className="block text-sm text-disco-muted mb-2">Background (optional)</label>
                            <textarea
                                value={background}
                                onChange={e => setBackground(e.target.value)}
                                placeholder="Describe your character... (e.g., 'A former soldier haunted by past failures')"
                                className="w-full bg-disco-bg border border-disco-muted/50 px-4 py-3 text-disco-paper
                                         font-serif focus:border-disco-cyan focus:outline-none h-24 resize-none"
                            />
                        </div>
                    </div>
                );

            case 3:
                return (
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xl text-disco-cyan font-mono">Allocate Your Stats</h3>
                            <span className={`text-sm font-mono ${remaining === 0 ? 'text-disco-cyan' : 'text-disco-accent'}`}>
                                {remaining} points remaining
                            </span>
                        </div>

                        <div className="space-y-4">
                            {Object.entries(stats).map(([stat, value]) => (
                                <div key={stat} className="flex items-center justify-between gap-4 p-3 bg-disco-bg/50 border border-disco-muted/30">
                                    <div className="flex-1">
                                        <div className="font-mono text-disco-paper uppercase">{stat}</div>
                                        <div className="text-xs text-disco-muted">
                                            {stat === 'edge' && 'Speed, agility, stealth'}
                                            {stat === 'heart' && 'Courage, empathy, charisma'}
                                            {stat === 'iron' && 'Strength, endurance, combat'}
                                            {stat === 'shadow' && 'Deception, cunning, trickery'}
                                            {stat === 'wits' && 'Knowledge, perception, wisdom'}
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => handleStatChange(stat, -1)}
                                            disabled={value <= 1}
                                            className="w-8 h-8 border border-disco-muted text-disco-muted hover:text-disco-paper 
                                                     hover:border-disco-paper disabled:opacity-30 transition-colors"
                                        >
                                            -
                                        </button>
                                        <span className="w-8 text-center text-xl font-bold text-disco-cyan">{value}</span>
                                        <button
                                            onClick={() => handleStatChange(stat, 1)}
                                            disabled={value >= 3 || remaining <= 0}
                                            className="w-8 h-8 border border-disco-muted text-disco-muted hover:text-disco-paper 
                                                     hover:border-disco-paper disabled:opacity-30 transition-colors"
                                        >
                                            +
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                        {archetype && (
                            <div className="text-xs text-disco-muted mt-2 text-center">
                                Suggested stats for {archetype} applied. Adjust as needed.
                            </div>
                        )}
                    </div>
                );

            case 4:
                return (
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xl text-disco-cyan font-mono">Choose Your Assets</h3>
                            <span className="text-sm text-disco-muted">
                                {selectedAssets.length}/3 selected
                            </span>
                        </div>

                        <p className="text-sm text-disco-muted">
                            Assets represent your character's skills, equipment, and relationships. Choose paths that
                            define your playstyle and create your unique identity in the Forge.
                        </p>

                        <div className="max-h-64 overflow-y-auto space-y-4 pr-2">
                            {Object.entries(availableAssets).map(([type, assets]) => (
                                <div key={type}>
                                    <div className="text-xs text-disco-accent uppercase tracking-wider mb-2 font-bold">{type}</div>
                                    <div className="space-y-2">
                                        {assets.slice(0, 8).map(asset => {
                                            const isSelected = selectedAssets.includes(asset.name);
                                            const canSelect = selectedAssets.length < 3 || isSelected;

                                            return (
                                                <button
                                                    key={asset.name}
                                                    onClick={() => toggleAsset(asset.name)}
                                                    disabled={!canSelect}
                                                    className={`w-full p-3 text-left border transition-all
                                                        ${isSelected
                                                            ? 'border-disco-cyan bg-disco-cyan/10 text-disco-cyan'
                                                            : canSelect
                                                                ? 'border-disco-muted/30 hover:border-disco-muted text-disco-paper/70 hover:bg-disco-bg/30'
                                                                : 'border-disco-muted/10 text-disco-muted/30 cursor-not-allowed'
                                                        }`}
                                                >
                                                    <div className="flex items-start justify-between gap-2">
                                                        <div className="flex-1">
                                                            <div className="font-mono font-bold text-sm mb-1">{asset.name}</div>
                                                            {asset.abilities && asset.abilities.length > 0 && (
                                                                <div className="text-xs opacity-80 space-y-1">
                                                                    {asset.abilities.slice(0, 2).map((ability, idx) => (
                                                                        <div key={idx} className="flex gap-1">
                                                                            <span className="text-disco-accent">•</span>
                                                                            <span>{ability}</span>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            )}
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <TTSButton text={`${asset.name}. ${asset.abilities ? asset.abilities.join('. ') : ''}`} className="shrink-0" asSpan={true} />
                                                            {isSelected && (
                                                                <span className="text-disco-cyan text-lg">✓</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            ))}
                            {Object.keys(availableAssets).length === 0 && (
                                <div className="text-disco-muted text-center py-8">
                                    Loading assets...
                                </div>
                            )}
                        </div>
                    </div>
                );

            case 5:
                return (
                    <div className="space-y-6">
                        <h3 className="text-xl text-disco-cyan font-mono">Swear Your Vow</h3>
                        <p className="text-sm text-disco-muted">
                            What drives you? What oath have you sworn that cannot be broken?
                        </p>

                        <textarea
                            value={vow}
                            onChange={e => setVow(e.target.value)}
                            placeholder="I swear to find my place among the stars..."
                            className="w-full bg-disco-bg border border-disco-muted/50 px-4 py-3 text-disco-paper
                                     font-serif focus:border-disco-cyan focus:outline-none h-32 resize-none"
                        />

                        <div className="text-xs text-disco-muted">
                            {selectedAssets.length > 0 ? (
                                <>
                                    <div className="mb-1">Suggested vows for your character type:</div>
                                    <VowSuggestions
                                        selectedAssets={selectedAssets}
                                        onSelect={setVow}
                                    />
                                </>
                            ) : (
                                <>
                                    <div className="mb-1">Suggested vows:</div>
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {[
                                            "Discover the truth about my past",
                                            "Protect those who cannot protect themselves",
                                            "Find redemption for my failures",
                                            "Uncover ancient secrets of the Forge"
                                        ].map(v => (
                                            <button
                                                key={v}
                                                onClick={() => setVow(v)}
                                                className="px-2 py-1 text-xs border border-disco-muted/30 hover:border-disco-cyan
                                                         hover:text-disco-cyan transition-colors"
                                            >
                                                {v}
                                            </button>
                                        ))}
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                );

            case 6:
                return (
                    <div className="space-y-6">
                        <h3 className="text-xl text-disco-cyan font-mono">Ready to Begin?</h3>

                        <div className="space-y-4 text-sm">
                            <div className="flex justify-between border-b border-disco-muted/20 pb-2">
                                <span className="text-disco-muted">Name</span>
                                <span className="text-disco-paper font-serif text-lg">{name}</span>
                            </div>
                            <div className="flex justify-between border-b border-disco-muted/20 pb-2">
                                <span className="text-disco-muted">Archetype</span>
                                <span className="text-disco-cyan font-mono">{archetype}</span>
                            </div>

                            {visualDescription && (
                                <div className="border-b border-disco-muted/20 pb-2">
                                    <span className="text-disco-muted">Visual Description</span>
                                    <p className="text-disco-paper mt-1 italic text-xs">{visualDescription}</p>
                                </div>
                            )}

                            <div className="flex justify-between border-b border-disco-muted/20 pb-2">
                                <span className="text-disco-muted">Stats</span>
                                <span className="text-disco-cyan font-mono">
                                    E{stats.edge} H{stats.heart} I{stats.iron} S{stats.shadow} W{stats.wits}
                                </span>
                            </div>

                            <div className="flex justify-between border-b border-disco-muted/20 pb-2">
                                <span className="text-disco-muted">Assets</span>
                                <span className="text-disco-accent text-right">
                                    {selectedAssets.length > 0 ? selectedAssets.join(', ') : 'None selected'}
                                </span>
                            </div>

                            <div className="border-b border-disco-muted/20 pb-2">
                                <span className="text-disco-muted">Vow</span>
                                <p className="text-disco-paper italic mt-1">
                                    "{vow || 'Find my place among the stars'}"
                                </p>
                            </div>
                        </div>
                    </div>
                );
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm">
            <div className="panel-glass w-full max-w-xl max-h-[85vh] overflow-hidden flex flex-col m-4">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-disco-muted/30">
                    <h2 className="text-2xl font-serif text-disco-paper">
                        Create Your Character
                    </h2>
                    <div className="text-sm text-disco-muted font-mono">
                        {selectedQuickstart && step > 1 ? 'Review' : `Step ${step} of ${selectedQuickstart ? '2' : '6'}`}
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="h-1 bg-disco-bg/50">
                    <div
                        className="h-full bg-disco-cyan transition-all duration-300"
                        style={{ width: `${selectedQuickstart && step > 1 ? 100 : (step / 6) * 100}%` }}
                    />
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {createdSessionId ? (
                        <CalibrationStep
                            sessionId={createdSessionId}
                            onComplete={() => onComplete({ session_id: createdSessionId })}
                        />
                    ) : (
                        renderStep()
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-disco-muted/30 flex justify-between">
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
                        className="px-4 py-2 text-disco-muted hover:text-disco-paper transition-colors"
                    >
                        {step > 0 ? '← Back' : 'Cancel'}
                    </button>

                    {(selectedQuickstart && step > 1) || step >= 6 ? (
                        <button
                            onClick={handleCreate}
                            disabled={loading}
                            className="btn-disco bg-disco-cyan/20 disabled:opacity-50"
                        >
                            {loading ? 'Creating...' : '🚀 Begin Adventure'}
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
                            className="btn-disco disabled:opacity-50"
                        >
                            Next →
                        </button>
                    )}
                </div>
            </div>

            {/* Music Player - Bottom Right */}
            <div className="absolute bottom-8 right-8 z-20">
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
