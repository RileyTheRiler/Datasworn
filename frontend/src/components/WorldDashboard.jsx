import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

const WorldDashboard = ({ sessionId = "default", onClose, visible }) => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [ticking, setTicking] = useState(false);

    // Weather controls
    const weatherTypes = [
        "clear", "light_nebula", "dense_nebula", "asteroid_field",
        "debris_field", "ion_storm", "solar_flare"
    ];

    const fetchStatus = async () => {
        try {
            const response = await fetch(`${API_URL}/world/status/${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                setStatus(data);
            }
        } catch (error) {
            console.error("Failed to fetch world status", error);
        }
    };

    useEffect(() => {
        if (visible) {
            fetchStatus();
            const interval = setInterval(fetchStatus, 5000);
            return () => clearInterval(interval);
        }
    }, [visible, sessionId]);

    const handleTick = async () => {
        setTicking(true);
        try {
            await fetch(`${API_URL}/world/tick`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, hours: 1 })
            });
            await fetchStatus();
        } catch (error) {
            console.error("Tick failed", error);
        } finally {
            setTicking(false);
        }
    };

    const handleSetWeather = async (weatherType) => {
        try {
            await fetch(`${API_URL}/world/debug/weather`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    weather: weatherType,
                    sector: "current_sector"
                })
            });
            await fetchStatus();
        } catch (error) {
            console.error("Set weather failed", error);
        }
    };

    if (!visible) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fadeIn">
            <div className="w-[800px] max-h-[90vh] bg-disco-bg border border-disco-cyan/30 shadow-[0_0_30px_rgba(34,211,238,0.1)] flex flex-col overflow-hidden rounded-lg">

                {/* Header */}
                <div className="p-4 border-b border-disco-cyan/20 flex justify-between items-center bg-black/40">
                    <h2 className="text-xl font-serif text-disco-cyan tracking-widest flex items-center gap-2">
                        <span className="animate-pulse">🌍</span> WORLD SIMULATION CONTROL
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-red transition-colors font-mono"
                    >
                        [CLOSE]
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8 font-mono">

                    {/* Status Overview */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="p-4 border border-disco-muted/20 bg-black/20 rounded">
                            <div className="text-xs text-disco-muted uppercase tracking-wider mb-2">Weather</div>
                            <div className="text-xl text-disco-paper">
                                {status?.weather?.state || "Unknown"}
                            </div>
                            <div className="mt-2 text-xs text-disco-green">
                                Modifiers: {status?.weather?.modifiers ? Object.keys(status.weather.modifiers).length : 0} active
                            </div>
                        </div>
                        <div className="p-4 border border-disco-muted/20 bg-black/20 rounded">
                            <div className="text-xs text-disco-muted uppercase tracking-wider mb-2">Traffic</div>
                            <div className="text-xl text-disco-paper">
                                {status?.formatted_traffic || "Low"}
                            </div>
                            <div className="mt-2 text-xs text-disco-yellow">
                                Congestion: {(status?.congestion * 100).toFixed(0)}%
                            </div>
                        </div>
                        <div className="p-4 border border-disco-muted/20 bg-black/20 rounded">
                            <div className="text-xs text-disco-muted uppercase tracking-wider mb-2">Active Entities</div>
                            <div className="text-xl text-disco-paper">
                                {(status?.active_ships || 0) + (status?.active_creatures || 0)}
                            </div>
                            <div className="mt-2 text-xs text-disco-purple">
                                Law: {status?.law_level || "Unknown"}
                            </div>
                        </div>
                    </div>

                    {/* Controls */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-bold text-disco-paper border-b border-disco-muted/30 pb-2">SIMULATION CONTROLS</h3>

                        <div className="flex gap-4">
                            <button
                                onClick={handleTick}
                                disabled={ticking}
                                className={`
                                    px-6 py-3 font-bold uppercase tracking-wider transition-all
                                    ${ticking
                                        ? 'bg-disco-cyan/20 text-disco-cyan cursor-wait'
                                        : 'bg-disco-cyan hover:bg-white hover:text-black text-black shadow-[0_0_15px_rgba(34,211,238,0.4)]'
                                    }
                                `}
                            >
                                {ticking ? 'CALCULATING...' : '▶ ADVANCE TIME (1H)'}
                            </button>
                        </div>
                    </div>

                    {/* Weather Override */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-bold text-disco-paper border-b border-disco-muted/30 pb-2">WEATHER OVERRIDE</h3>
                        <div className="grid grid-cols-4 gap-2">
                            {weatherTypes.map(w => (
                                <button
                                    key={w}
                                    onClick={() => handleSetWeather(w)}
                                    className={`
                                        p-2 text-xs border transition-colors
                                        ${status?.weather?.state === w
                                            ? 'border-disco-cyan bg-disco-cyan/10 text-disco-cyan font-bold'
                                            : 'border-disco-muted/30 text-disco-muted hover:border-disco-paper hover:text-disco-paper'
                                        }
                                    `}
                                >
                                    {w.toUpperCase()}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Suspicion Heatmap (Text Only for MVP) */}
                    {status?.suspicion && Object.keys(status.suspicion).length > 0 && (
                        <div className="space-y-4">
                            <h3 className="text-sm font-bold text-disco-red border-b border-disco-red/30 pb-2">FACTION SUSPICION</h3>
                            <div className="grid grid-cols-2 gap-2">
                                {Object.entries(status.suspicion).map(([faction, value]) => (
                                    <div key={faction} className="flex justify-between items-center bg-black/20 p-2 border border-disco-red/20">
                                        <span className="text-disco-paper text-sm">{faction}</span>
                                        <div className="flex items-center gap-2">
                                            <div className="w-24 h-2 bg-disco-muted/20">
                                                <div
                                                    className="h-full bg-disco-red transition-all duration-500"
                                                    style={{ width: `${value * 100}%` }}
                                                />
                                            </div>
                                            <span className="text-disco-red text-xs font-bold">{value.toFixed(2)}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WorldDashboard;
