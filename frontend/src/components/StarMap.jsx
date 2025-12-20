import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const StarMap = ({ sessionId, visible, onClose }) => {
    const [systems, setSystems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [currentSector, setCurrentSector] = useState("The Forge");

    useEffect(() => {
        if (visible) {
            fetchNearby();
        }
    }, [visible]);

    const fetchNearby = async () => {
        setLoading(true);
        try {
            // Check if we need to generate first
            const data = await api.get(`/starmap/nearby/${sessionId}?count=10`);
            if (data.systems && data.systems.length > 0) {
                setSystems(data.systems);
            } else {
                // Auto-generate if empty
                await api.post(`/starmap/generate?session_id=${sessionId}&sector_name=${currentSector}`);
                const newData = await api.get(`/starmap/nearby/${sessionId}?count=10`);
                setSystems(newData.systems || []);
            }
        } catch (err) {
            console.error("Failed to fetch systems:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleTravel = async (systemId) => {
        setLoading(true);
        try {
            const result = await api.post('/starmap/travel', {
                session_id: sessionId,
                system_id: systemId
            });

            if (result.success) {
                onClose();
                // Ideally trigger a toast or notification here
            }
        } catch (err) {
            console.error("Travel failed:", err);
        } finally {
            setLoading(false);
        }
    };

    if (!visible) return null;

    return (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center animate-fadeIn">
            <div className="bg-disco-panel border-2 border-disco-cyan p-6 rounded-lg max-w-4xl w-full max-h-[85vh] overflow-y-auto shadow-hard relative">
                {/* Header */}
                <div className="flex justify-between items-center mb-6 border-b border-disco-cyan/30 pb-4">
                    <div>
                        <h2 className="text-3xl font-serif font-bold text-disco-cyan tracking-wider">STAR MAP</h2>
                        <p className="text-disco-paper/60 font-mono text-xs uppercase tracking-[0.2em]">Sector: {currentSector}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-red text-2xl"
                    >
                        ×
                    </button>
                </div>

                {loading ? (
                    <div className="h-64 flex flex-col items-center justify-center gap-4">
                        <div className="w-12 h-12 border-2 border-disco-cyan border-t-transparent rounded-full animate-spin" />
                        <span className="text-disco-cyan font-mono animate-pulse">Calculating Trajectories...</span>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {systems.map(system => (
                            <div
                                key={system.id}
                                className={`
                                    group relative p-4 border transition-all duration-300 cursor-pointer overflow-hidden
                                    ${system.discovered
                                        ? 'bg-disco-cyan/5 border-disco-cyan hover:bg-disco-cyan/10'
                                        : 'bg-black/40 border-disco-muted/50 hover:border-disco-muted'}
                                `}
                                onClick={() => handleTravel(system.id)}
                            >
                                {/* Background Grid Effect */}
                                <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-disco-cyan/50 to-transparent group-hover:opacity-20 transition-opacity" />

                                <div className="relative z-10 flex justify-between items-start">
                                    <h3 className="text-xl font-bold text-disco-paper group-hover:text-disco-cyan transition-colors">
                                        {system.name}
                                    </h3>
                                    {system.has_station && (
                                        <span className="text-xs px-1.5 py-0.5 border border-disco-accent text-disco-accent rounded bg-disco-accent/10">
                                            STATION
                                        </span>
                                    )}
                                </div>

                                <div className="relative z-10 mt-3 space-y-1 font-mono text-xs text-disco-paper/70">
                                    <div className="flex justify-between">
                                        <span>Type:</span>
                                        <span className="text-disco-cyan">{system.star_type}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Planets:</span>
                                        <span>{system.planets}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Danger:</span>
                                        <span className={system.danger_level > 0.7 ? "text-disco-red" : "text-disco-green"}>
                                            {Math.round(system.danger_level * 100)}%
                                        </span>
                                    </div>
                                    {system.controlling_faction && (
                                        <div className="flex justify-between">
                                            <span>Control:</span>
                                            <span className="text-disco-accent">{system.controlling_faction.replace('_', ' ').toUpperCase()}</span>
                                        </div>
                                    )}
                                    {system.hazard && (
                                        <div className="mt-2 p-1.5 bg-disco-red/10 border border-disco-red/30 rounded text-disco-red animate-pulse flex items-center gap-1">
                                            <span className="text-[10px]">⚠️ HAZARD: {system.hazard.name.toUpperCase()}</span>
                                        </div>
                                    )}
                                </div>

                                {/* Resource Tags */}
                                {system.resources && system.resources.length > 0 && (
                                    <div className="relative z-10 mt-4 flex flex-wrap gap-1">
                                        {system.resources.map(res => (
                                            <span key={res} className="text-[10px] px-1.5 py-0.5 bg-black/50 border border-disco-muted/30 rounded text-disco-muted">
                                                {res}
                                            </span>
                                        ))}
                                    </div>
                                )}

                                {/* Hover "Travel" Indicator */}
                                <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0 text-disco-accent font-bold text-xs uppercase tracking-widest">
                                    ENGAGE &gt;&gt;
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                <div className="mt-6 pt-4 border-t border-disco-muted/20 flex justify-between items-center text-xs text-disco-muted font-mono">
                    <span>Targeting System Online</span>
                    <div className="flex gap-4">
                        <span>FUEL: OPTIMAL</span>
                        <span>HYPERDRIVE: READY</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StarMap;
