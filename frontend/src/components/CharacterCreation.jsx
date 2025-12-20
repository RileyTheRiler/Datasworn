import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

/**
 * CharacterCreation - Multi-step wizard for new character creation
 * Steps: 1) Name & Background 2) Stats 3) Assets 4) Vow 5) Review
 */
const CharacterCreation = ({ onComplete, onCancel }) => {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [availableAssets, setAvailableAssets] = useState({});

    // Character data
    const [name, setName] = useState('');
    const [background, setBackground] = useState('');
    const [stats, setStats] = useState({
        edge: 1,
        heart: 2,
        iron: 1,
        shadow: 1,
        wits: 2
    });
    const [selectedAssets, setSelectedAssets] = useState([]);
    const [vow, setVow] = useState('');

    // Stat points remaining (7 total: must sum to 7)
    const totalPoints = 7;
    const usedPoints = Object.values(stats).reduce((a, b) => a + b, 0);
    const remaining = totalPoints - usedPoints;

    // Load available assets on mount
    useEffect(() => {
        fetch(`${API_URL}/assets/available`)
            .then(res => res.json())
            .then(data => setAvailableAssets(data.assets || {}))
            .catch(console.error);
    }, []);

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
                    background: background
                })
            });
            const data = await res.json();
            if (data.session_id) {
                onComplete(data);
            }
        } catch (err) {
            console.error('Character creation failed:', err);
        } finally {
            setLoading(false);
        }
    };

    const canProceed = () => {
        switch (step) {
            case 1: return name.trim().length >= 2;
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
                    </div>
                );

            case 3:
                return (
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xl text-disco-cyan font-mono">Choose Your Assets</h3>
                            <span className="text-sm text-disco-muted">
                                {selectedAssets.length}/3 selected
                            </span>
                        </div>

                        <div className="max-h-64 overflow-y-auto space-y-4 pr-2">
                            {Object.entries(availableAssets).map(([type, assets]) => (
                                <div key={type}>
                                    <div className="text-xs text-disco-accent uppercase tracking-wider mb-2">{type}</div>
                                    <div className="grid grid-cols-2 gap-2">
                                        {assets.slice(0, 6).map(asset => (
                                            <button
                                                key={asset.name}
                                                onClick={() => toggleAsset(asset.name)}
                                                className={`p-2 text-left text-sm border transition-colors
                                                    ${selectedAssets.includes(asset.name)
                                                        ? 'border-disco-cyan bg-disco-cyan/10 text-disco-cyan'
                                                        : 'border-disco-muted/30 hover:border-disco-muted text-disco-paper/70'}`}
                                            >
                                                <div className="font-mono">{asset.name}</div>
                                            </button>
                                        ))}
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

                            {background && (
                                <div className="border-b border-disco-muted/20 pb-2">
                                    <span className="text-disco-muted">Background</span>
                                    <p className="text-disco-paper mt-1">{background}</p>
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
                                <span className="text-disco-accent">
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
                    {renderStep()}
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
