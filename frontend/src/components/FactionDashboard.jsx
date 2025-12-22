import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

const FactionDashboard = ({ sessionId }) => {
    const [factions, setFactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedFaction, setSelectedFaction] = useState(null);

    useEffect(() => {
        fetchFactions();
    }, [sessionId]);

    const fetchFactions = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/factions/status/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                setFactions(data.factions || []);
                if (data.factions && data.factions.length > 0) {
                    setSelectedFaction(data.factions[0]);
                }
            }
        } catch (err) {
            console.error("Failed to fetch factions:", err);
        } finally {
            setLoading(false);
        }
    };

    // Helper to determine color based on standing
    const getStandingColor = (standing) => {
        switch (standing?.toUpperCase()) {
            case 'NEMESIS': return 'text-disco-red';
            case 'HOSTILE': return 'text-disco-red/80';
            case 'SUSPICIOUS': return 'text-orange-400';
            case 'NEUTRAL': return 'text-disco-muted';
            case 'FRIENDLY': return 'text-disco-green';
            case 'ALLIED': return 'text-disco-cyan';
            case 'HONORED': return 'text-disco-gold'; // Assuming gold exists or fallback
            default: return 'text-disco-muted';
        }
    };

    const getReputationPercentage = (rep) => {
        // Map -100 to 100 range to 0 to 100%
        return ((rep + 100) / 200) * 100;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full text-disco-muted font-mono animate-pulse">
                Accessing Faction Database...
            </div>
        );
    }

    return (
        <div className="flex-1 flex overflow-hidden h-full">
            {/* Left Sidebar: Faction List */}
            <div className="w-1/3 bg-disco-dark/50 border-r border-disco-muted/30 flex flex-col">
                <div className="flex-1 overflow-y-auto p-2 space-y-1">
                    {factions.map(faction => (
                        <button
                            key={faction.id}
                            onClick={() => setSelectedFaction(faction)}
                            className={`w-full text-left p-3 rounded transition-all border group ${selectedFaction?.id === faction.id
                                    ? 'bg-disco-cyan/10 border-disco-cyan'
                                    : 'bg-transparent border-transparent hover:bg-white/5'
                                }`}
                        >
                            <div className="flex justify-between items-center mb-1">
                                <span className={`font-bold text-sm ${selectedFaction?.id === faction.id ? 'text-disco-cyan' : 'text-disco-paper group-hover:text-white'
                                    }`}>
                                    {faction.name}
                                </span>
                                <span className={`text-[10px] font-mono px-1.5 rounded border border-current opacity-70 ${getStandingColor(faction.standing)}`}>
                                    {faction.standing}
                                </span>
                            </div>
                            <div className="w-full h-1 bg-black/50 rounded-full overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-500`}
                                    style={{
                                        width: `${getReputationPercentage(faction.reputation)}%`,
                                        backgroundColor: faction.reputation < 0 ? '#ef4444' : '#22d3ee'
                                    }}
                                />
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Right Content: Details */}
            <div className="flex-1 flex flex-col bg-black/20 relative">
                {selectedFaction ? (
                    <div className="flex-1 overflow-y-auto p-8">
                        {/* Header */}
                        <div className="border-b border-disco-muted/20 pb-6 mb-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <div className="text-disco-muted text-xs font-mono uppercase tracking-wider mb-1">
                                        {selectedFaction.type}
                                    </div>
                                    <h2 className="text-3xl font-serif text-disco-paper font-bold mb-2">
                                        {selectedFaction.name}
                                    </h2>
                                </div>
                                <div className={`text-right ${getStandingColor(selectedFaction.standing)}`}>
                                    <div className="text-2xl font-bold tracking-widest uppercase">
                                        {selectedFaction.standing}
                                    </div>
                                    <div className="text-xs font-mono opacity-70">
                                        Reputation: {selectedFaction.reputation.toFixed(1)}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Description */}
                        <div className="mb-8">
                            <p className="font-serif text-lg leading-relaxed text-disco-paper/90 text-justify">
                                {selectedFaction.description}
                            </p>
                        </div>

                        {/* Stats / Influence */}
                        <div className="grid grid-cols-2 gap-4 mb-8">
                            <div className="bg-black/40 p-4 rounded border border-disco-muted/10">
                                <div className="text-disco-muted text-xs font-mono uppercase mb-2">Trade Modifier</div>
                                <div className="text-xl font-mono text-disco-cyan">
                                    {(selectedFaction.trade_modifier * 100).toFixed(0)}%
                                </div>
                                <div className="text-xs text-disco-muted mt-1">
                                    Market prices adjust based on standing.
                                </div>
                            </div>
                            <div className="bg-black/40 p-4 rounded border border-disco-muted/10">
                                <div className="text-disco-muted text-xs font-mono uppercase mb-2">Influence</div>
                                <div className="text-sm text-disco-paper/80">
                                    Controlled Sectors, Stations
                                </div>
                            </div>
                        </div>

                        {/* Reputation Meter Visual */}
                        <div className="mt-auto pt-6 border-t border-disco-muted/10">
                            <div className="flex justify-between text-xs font-mono text-disco-muted mb-2">
                                <span>HOSTILE (-100)</span>
                                <span>NEUTRAL (0)</span>
                                <span>ALLIED (+100)</span>
                            </div>
                            <div className="relative h-4 bg-black/60 rounded-full overflow-hidden border border-disco-muted/20">
                                {/* Center Marker */}
                                <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-white/20 z-10" />

                                {/* Bar */}
                                <div
                                    className={`absolute top-0 bottom-0 transition-all duration-700 ease-out ${selectedFaction.reputation < 0 ? 'bg-gradient-to-r from-red-900 to-red-500 right-1/2' : 'bg-gradient-to-r from-cyan-900 to-cyan-400 left-1/2'
                                        }`}
                                    style={{
                                        width: `${Math.abs(selectedFaction.reputation) / 2}%`,
                                        [selectedFaction.reputation < 0 ? 'marginRight' : 'marginLeft']: '0px'
                                    }}
                                />

                                {/* Current Marker */}
                                <div
                                    className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_10px_white] z-20 transition-all duration-700"
                                    style={{ left: `${getReputationPercentage(selectedFaction.reputation)}%` }}
                                />
                            </div>
                        </div>

                    </div>
                ) : (
                    <div className="flex items-center justify-center h-full text-disco-muted">
                        Select a faction
                    </div>
                )}
            </div>
        </div>
    );
};

export default FactionDashboard;
