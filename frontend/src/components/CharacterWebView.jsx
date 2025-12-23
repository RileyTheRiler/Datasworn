import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8001/api';

const CharacterWebView = ({ sessionId = 'default' }) => {
    const [webData, setWebData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedCorner, setSelectedCorner] = useState(null);

    useEffect(() => {
        fetchCharacterWeb();
    }, []);

    const fetchCharacterWeb = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/narrative/character-web`);
            if (response.ok) {
                const data = await response.json();
                setWebData(data);
                if (data.corners && data.corners.length > 0) {
                    setSelectedCorner(data.corners[0]);
                }
            }
        } catch (err) {
            console.error("Character Web fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-disco-cyan font-mono text-sm animate-pulse">
                    Loading Character Web...
                </div>
            </div>
        );
    }

    if (!webData) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-disco-muted font-mono text-sm">
                    Character Web data unavailable
                </div>
            </div>
        );
    }

    const roleColors = {
        hero: 'disco-cyan',
        necessary_opponent: 'disco-red',
        ally: 'disco-green',
        fake_ally_opponent: 'disco-yellow',
        optional_fake_opponent_ally: 'disco-purple',
        subplot_mirror: 'disco-muted'
    };

    const getRoleColor = (role) => roleColors[role] || 'disco-muted';

    return (
        <div className="flex-1 flex overflow-hidden bg-black/20">
            {/* Left Sidebar: Character Corners */}
            <div className="w-1/3 bg-disco-dark/50 border-r border-disco-muted/30 flex flex-col">
                <div className="p-4 border-b border-disco-muted/20">
                    <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider">
                        Four-Corner Opposition
                    </h3>
                    <p className="text-disco-muted text-xs mt-1">
                        {webData.corners?.length || 0} character roles
                    </p>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {webData.corners?.map((corner, idx) => (
                        <button
                            key={idx}
                            onClick={() => setSelectedCorner(corner)}
                            className={`w-full text-left p-3 rounded transition-all border ${
                                selectedCorner?.name === corner.name
                                    ? `bg-${getRoleColor(corner.role)}/10 border-${getRoleColor(corner.role)} text-${getRoleColor(corner.role)}`
                                    : 'bg-transparent border-transparent text-disco-paper/70 hover:bg-disco-muted/10 hover:text-disco-paper'
                            }`}
                        >
                            <div className={`font-mono text-xs opacity-70 mb-1 text-${getRoleColor(corner.role)}`}>
                                {corner.role.replace(/_/g, ' ').toUpperCase()}
                            </div>
                            <div className="font-bold text-sm">{corner.name}</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Right Content: Selected Corner Details */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {selectedCorner ? (
                    <div className="flex-1 overflow-y-auto p-8">
                        <div className="max-w-3xl mx-auto space-y-6">
                            {/* Header */}
                            <div className="pb-4 border-b border-disco-muted/20">
                                <div className={`text-${getRoleColor(selectedCorner.role)} font-mono text-xs uppercase tracking-[0.3em] mb-2`}>
                                    {selectedCorner.role.replace(/_/g, ' ')}
                                </div>
                                <h2 className="text-3xl font-serif font-bold text-disco-paper mb-2">
                                    {selectedCorner.name}
                                </h2>
                            </div>

                            {/* Goal */}
                            <div className="bg-black/40 p-4 rounded border border-disco-muted/20">
                                <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider mb-2">
                                    Goal
                                </h3>
                                <p className="text-disco-paper/90 leading-relaxed">
                                    {selectedCorner.goal}
                                </p>
                            </div>

                            {/* Values */}
                            <div className="bg-black/40 p-4 rounded border border-disco-muted/20">
                                <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider mb-3">
                                    Core Values
                                </h3>
                                <div className="flex flex-wrap gap-2">
                                    {selectedCorner.values?.map((value, idx) => (
                                        <span
                                            key={idx}
                                            className={`px-3 py-1 bg-${getRoleColor(selectedCorner.role)}/10 border border-${getRoleColor(selectedCorner.role)}/30 rounded text-${getRoleColor(selectedCorner.role)} text-sm font-mono`}
                                        >
                                            {value}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Tactic */}
                            <div className="bg-black/40 p-4 rounded border border-disco-muted/20">
                                <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider mb-2">
                                    Tactic Style
                                </h3>
                                <p className="text-disco-paper/90 font-bold uppercase tracking-wide">
                                    {selectedCorner.tactic}
                                </p>
                            </div>

                            {/* Exposure Logic */}
                            <div className="bg-disco-red/5 p-4 rounded border border-disco-red/20">
                                <h3 className="font-mono text-xs text-disco-red uppercase tracking-wider mb-2">
                                    How They Expose the Hero
                                </h3>
                                <p className="text-disco-paper/90 leading-relaxed italic">
                                    {selectedCorner.exposure}
                                </p>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 flex items-center justify-center text-disco-muted/50 font-mono text-sm">
                        Select a character to view details
                    </div>
                )}

                {/* Bottom: Conflicts & Reversals */}
                {webData.conflicts && webData.conflicts.length > 0 && (
                    <div className="border-t border-disco-muted/30 bg-disco-dark/30 p-4">
                        <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider mb-3">
                            Key Conflicts
                        </h3>
                        <div className="space-y-2 max-h-32 overflow-y-auto">
                            {webData.conflicts.map((conflict, idx) => (
                                <div key={idx} className="text-xs bg-black/40 p-2 rounded border border-disco-muted/10">
                                    <div className="text-disco-yellow font-bold">
                                        {conflict.primary} vs {conflict.secondary}
                                    </div>
                                    <div className="text-disco-muted mt-1">
                                        {conflict.type}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CharacterWebView;
