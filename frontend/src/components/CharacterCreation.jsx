import React, { useState, useEffect } from 'react';
import CalibrationStep from './CalibrationStep';

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
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [availableAssets, setAvailableAssets] = useState({});
    const [createdSessionId, setCreatedSessionId] = useState(null); // For calibration step

    // Character data
    const [name, setName] = useState('');
    const [archetype, setArchetype] = useState('');
    const [visualDescription, setVisualDescription] = useState('');
    const [history, setHistory] = useState(''); // Narrative background
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

    // Load available assets on mount
    useEffect(() => {
        fetch(`${API_URL}/assets/available`)
            .then(res => res.json())
            .then(data => setAvailableAssets(data.assets || {}))
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
            const res = await fetch(`${API_URL}/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    character_name: name,
                    background_vow: vow || "Find my place among the stars",
                    stats: stats,
                    asset_ids: selectedAssets,
                    background: visualDescription
                })
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
            case 1: return name.trim().length >= 2 && archetype;
            case 2: return remaining === 0;
            case 3: return true; // Assets optional
            case 4: return true; // Vow optional (has default)
            default: return true;
        }
    };

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <div className="space-y-6">
                        <h3 className="text-xl text-disco-cyan font-mono">Identity & Archetype</h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-4">
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
                                    <label className="block text-sm text-disco-muted mb-2">Visual Description (for Portrait)</label>
                                    <textarea
                                        value={visualDescription}
                                        onChange={e => setVisualDescription(e.target.value)}
                                        placeholder="Describe your appearance (e.g., weathered face, cybernetic eye, pilot gear)..."
                                        className="w-full bg-disco-bg border border-disco-muted/50 px-4 py-3 text-disco-paper 
                                                 font-serif focus:border-disco-cyan focus:outline-none h-32 resize-none"
                                    />
                                </div>
                            </div>

                            <div className="space-y-3">
                                <label className="block text-sm text-disco-muted">Choose Archetype</label>
                                <div className="grid grid-cols-1 gap-2 max-h-[400px] overflow-y-auto pr-2">
                                    {Object.entries(ARCHETYPES).map(([role, data]) => (
                                        <button
                                            key={role}
                                            onClick={() => handleArchetypeSelect(role)}
                                            className={`p-3 text-left border rounded transition-all
                                                ${archetype === role
                                                    ? 'border-disco-cyan bg-disco-cyan/10 text-disco-paper'
                                                    : 'border-disco-muted/30 hover:border-disco-muted text-disco-muted hover:text-disco-paper'}`}
                                        >
                                            <div className="font-mono font-bold">{role}</div>
                                            <div className="text-xs opacity-70 mt-1">{data.description}</div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                );

            case 2:
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

            case 3:
                return (
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xl text-disco-cyan font-mono">Choose Your Assets</h3>
                            <span className="text-sm text-disco-muted">
                                {selectedAssets.length}/3 selected
                            </span>
                        </div>

                        {/* Help Section */}
                        <details className="bg-disco-bg/50 border border-disco-muted/30 p-3">
                            <summary className="cursor-pointer text-sm text-disco-accent font-mono hover:text-disco-cyan transition-colors">
                                ℹ️ What are Assets?
                            </summary>
                            <div className="mt-3 text-xs text-disco-muted space-y-2">
                                <p>
                                    <strong className="text-disco-paper">Assets</strong> are special abilities, equipment, companions, or traits that make your character unique.
                                    You can choose up to <strong className="text-disco-cyan">3 assets</strong> to start with.
                                </p>
                                <div className="space-y-1">
                                    <p><strong className="text-disco-accent">Path:</strong> Your training/profession (combat skills, navigation, etc.)</p>
                                    <p><strong className="text-disco-accent">Companion:</strong> Allies that travel with you (robots, animals, etc.)</p>
                                    <p><strong className="text-disco-accent">Module:</strong> Ship upgrades or special equipment</p>
                                    <p><strong className="text-disco-accent">Deed:</strong> Special abilities earned through experience</p>
                                </div>
                                <p className="text-disco-cyan">
                                    💡 Tip: Your archetype suggests assets that fit your playstyle, but you can swap them for others!
                                </p>
                            </div>
                        </details>

                        {archetype && selectedAssets.length > 0 && (
                            <div className="text-xs bg-disco-cyan/10 p-2 border border-disco-cyan/30 text-disco-cyan">
                                Pre-selected assets for {archetype}. Click to remove or add others.
                            </div>
                        )}

                        <div className="max-h-80 overflow-y-auto space-y-4 pr-2">
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
                                                        {isSelected && (
                                                            <span className="text-disco-cyan text-lg">✓</span>
                                                        )}
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

            case 4:
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
                            Suggested vows:
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
                        </div>
                    </div>
                );

            case 5:
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
                        Step {step} of 5
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="h-1 bg-disco-bg/50">
                    <div
                        className="h-full bg-disco-cyan transition-all duration-300"
                        style={{ width: `${(step / 5) * 100}%` }}
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
                        onClick={() => step > 1 ? setStep(step - 1) : onCancel?.()}
                        className="px-4 py-2 text-disco-muted hover:text-disco-paper transition-colors"
                    >
                        {step > 1 ? '← Back' : 'Cancel'}
                    </button>

                    {step < 5 ? (
                        <button
                            onClick={() => setStep(step + 1)}
                            disabled={!canProceed()}
                            className="btn-disco disabled:opacity-50"
                        >
                            Next →
                        </button>
                    ) : (
                        <button
                            onClick={handleCreate}
                            disabled={loading}
                            className="btn-disco bg-disco-cyan/20 disabled:opacity-50"
                        >
                            {loading ? 'Creating...' : '🚀 Begin Adventure'}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CharacterCreation;
