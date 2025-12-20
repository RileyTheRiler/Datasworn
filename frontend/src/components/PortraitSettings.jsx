import React, { useState } from 'react';
import api from '../utils/api';

const STYLES = [
    { id: 'realistic', label: 'Cinematic' },
    { id: 'oil_painting', label: 'Disco Elysium' },
    { id: 'anime', label: 'Anime' },
    { id: 'comic_book', label: 'Comic Book' },
    { id: 'pixel_art', label: 'Pixel Art' },
    { id: 'cyberpunk', label: 'Cyberpunk' }
];

const EXPRESSIONS = [
    { id: 'neutral', label: 'Neutral' },
    { id: 'determined', label: 'Determined' },
    { id: 'angry', label: 'Angry' },
    { id: 'friendly', label: 'Friendly' },
    { id: 'afraid', label: 'Afraid' },
    { id: 'tired', label: 'Weary' },
    { id: 'pained', label: 'Pained' }
];

const PortraitSettings = ({ isOpen, onClose, characterName, currentStyle, onUpdate }) => {
    const [selectedStyle, setSelectedStyle] = useState(currentStyle || 'oil_painting');
    const [selectedExpression, setSelectedExpression] = useState('determined');
    const [description, setDescription] = useState('A gritty sci-fi survivor');
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleRegenerate = async () => {
        setLoading(true);
        try {
            const res = await api.post('/assets/generate-portrait', {
                name: characterName,
                description: description,
                style: selectedStyle,
                expression: selectedExpression,
                conditions: [] // Could pull from character state if passed
            });

            if (res.url) {
                onUpdate({ portrait: res.url });
            }
            onClose();
        } catch (err) {
            console.error("Failed to generate portrait:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fadeIn">
            <div className="bg-disco-panel border-2 border-disco-cyan p-6 rounded-lg max-w-md w-full mx-4 shadow-hard max-h-[90vh] overflow-y-auto">
                <h2 className="text-2xl font-serif font-bold text-disco-cyan mb-4">Portrait Settings</h2>

                {/* Style Selection */}
                <div className="mb-4">
                    <label className="block text-xs font-mono text-disco-muted uppercase mb-2">Art Style</label>
                    <div className="grid grid-cols-2 gap-2">
                        {STYLES.map(style => (
                            <button
                                key={style.id}
                                onClick={() => setSelectedStyle(style.id)}
                                className={`px-3 py-2 text-sm border rounded transition-all ${selectedStyle === style.id
                                        ? 'bg-disco-cyan/20 border-disco-cyan text-disco-cyan'
                                        : 'border-disco-muted/30 text-disco-muted hover:border-disco-muted'
                                    }`}
                            >
                                {style.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Expression Selection */}
                <div className="mb-4">
                    <label className="block text-xs font-mono text-disco-muted uppercase mb-2">Expression</label>
                    <select
                        value={selectedExpression}
                        onChange={(e) => setSelectedExpression(e.target.value)}
                        className="w-full bg-black/50 border border-disco-muted p-2 text-disco-paper rounded focus:border-disco-cyan focus:outline-none"
                    >
                        {EXPRESSIONS.map(exp => (
                            <option key={exp.id} value={exp.id}>{exp.label}</option>
                        ))}
                    </select>
                </div>

                {/* Description Override */}
                <div className="mb-6">
                    <label className="block text-xs font-mono text-disco-muted uppercase mb-2">Description Prompt</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        className="w-full bg-black/50 border border-disco-muted p-2 text-disco-paper rounded focus:border-disco-cyan focus:outline-none h-20 text-sm"
                        placeholder="Describe your character..."
                    />
                </div>

                <div className="flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="btn-disco-secondary px-4 py-2"
                        disabled={loading}
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleRegenerate}
                        className="btn-disco px-6 py-2 flex items-center gap-2"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                Generating...
                            </>
                        ) : (
                            'Regenerate'
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PortraitSettings;
