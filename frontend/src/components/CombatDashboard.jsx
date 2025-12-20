import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

const CombatDashboard = ({ visible, onClose, sessionId = 'default' }) => {
    const [combatState, setCombatState] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Poll for updates when visible
    useEffect(() => {
        if (!visible) return;

        const fetchData = async () => {
            try {
                const res = await fetch(`${API_URL}/combat/debug/${sessionId}`);
                if (!res.ok) {
                    if (res.status === 404) throw new Error("No active session");
                    throw new Error("Failed to fetch combat state");
                }
                const data = await res.json();

                // If the backend returns {status: "No active combat system"}, handle gracefully
                if (data.status === "No active combat system") {
                    setCombatState(null);
                } else {
                    setCombatState(data);
                }
                setError(null);
            } catch (err) {
                console.error("Combat fetch error:", err);
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 1000); // Poll faster (1s)

        return () => clearInterval(interval);
    }, [visible, sessionId]);

    const handleStartCombat = async (type, count) => {
        setIsLoading(true);
        try {
            await fetch(`${API_URL}/combat/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    enemy_type: type,
                    count: count
                })
            });
            // State will update on next poll
        } catch (err) {
            setError("Failed to start combat");
        } finally {
            setIsLoading(false);
        }
    };

    const handleEndCombat = async () => {
        if (!confirm("Terminate combat simulation?")) return;
        try {
            await fetch(`${API_URL}/combat/end?session_id=${sessionId}`, { method: 'POST' });
            setCombatState(null);
        } catch (err) {
            setError("Failed to end combat");
        }
    };

    if (!visible) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md p-8 animate-in fade-in duration-200">
            {/* Holographic Container */}
            <div className="w-full max-w-4xl h-[80vh] bg-disco-dark border-2 border-disco-cyan/40 shadow-[0_0_30px_rgba(107,228,227,0.2)] flex flex-col relative overflow-hidden">

                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-disco-cyan/20 bg-disco-cyan/5">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl animate-pulse">⚔️</span>
                        <h2 className="font-serif text-2xl text-disco-cyan tracking-widest uppercase text-outline">
                            Combat Orchestrator
                        </h2>
                    </div>
                    <div className="flex items-center gap-2">
                        {combatState && (
                            <button
                                onClick={handleEndCombat}
                                className="px-3 py-1 bg-red-900/50 hover:bg-red-800 text-red-200 text-xs font-mono uppercase border border-red-700/50"
                            >
                                End Sim
                            </button>
                        )}
                        <button
                            onClick={onClose}
                            className="w-8 h-8 flex items-center justify-center border border-disco-red/50 text-disco-red hover:bg-disco-red hover:text-white transition-colors rounded-none font-mono"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 p-8 overflow-y-auto relative bg-[url('/assets/grid_bg.png')] bg-repeat opacity-90">
                    <div className="absolute inset-0 bg-disco-cyan/5 pointer-events-none"
                        style={{ backgroundImage: 'radial-gradient(circle at center, transparent 0%, #0a0a0a 100%)' }}
                    />

                    {isLoading ? (
                        <div className="flex h-full items-center justify-center text-disco-cyan animate-pulse font-mono">
                            CALIBRATING SENSORS...
                        </div>
                    ) : error ? (
                        <div className="flex h-full items-center justify-center text-disco-red font-mono border border-disco-red/30 bg-disco-red/5 p-4 mx-auto max-w-md text-center">
                            ⚠ ERROR: {error}
                        </div>
                    ) : !combatState ? (
                        <div className="flex h-full items-center justify-center text-disco-muted font-mono flex-col gap-4">
                            <div className="text-4xl opacity-50">📡</div>
                            <div>NO ACTIVE COMBAT DETECTED</div>
                            <div className="text-xs opacity-50 mb-4">Systems Standing By</div>

                            {/* Debug Spawn Controls */}
                            <div className="flex gap-4 p-4 border border-disco-cyan/20 bg-black/40">
                                <button
                                    onClick={() => handleStartCombat('SOLDIER', 3)}
                                    className="px-4 py-2 bg-disco-cyan/10 hover:bg-disco-cyan/30 text-disco-cyan border border-disco-cyan/50 font-mono text-xs uppercase transition-colors"
                                >
                                    Spawn Squad (3)
                                </button>
                                <button
                                    onClick={() => handleStartCombat('ELITE', 1)}
                                    className="px-4 py-2 bg-disco-red/10 hover:bg-disco-red/30 text-disco-red border border-disco-red/50 font-mono text-xs uppercase transition-colors"
                                >
                                    Spawn Elite (1)
                                </button>
                                <button
                                    onClick={() => handleStartCombat('MINION', 6)}
                                    className="px-4 py-2 bg-disco-yellow/10 hover:bg-disco-yellow/30 text-disco-yellow border border-disco-yellow/50 font-mono text-xs uppercase transition-colors"
                                >
                                    Horde (6)
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-full">

                            {/* Left: Tokens & Flow */}
                            <div className="border border-disco-cyan/20 bg-black/40 p-6 relative">
                                <h3 className="font-mono text-sm text-disco-cyan/70 uppercase mb-4 border-b border-disco-cyan/10 pb-2">
                                    Token Distribution
                                </h3>
                                <div className="space-y-6">
                                    <div className="flex justify-between items-center bg-disco-cyan/10 p-4 border border-disco-cyan/30">
                                        <span className="font-bold text-disco-paper">Available Tokens</span>
                                        <span className="text-3xl font-mono text-disco-cyan font-bold drop-shadow-glow">
                                            {combatState.token_manager?.available_tokens ?? 0}
                                        </span>
                                    </div>

                                    {/* Active Attackers */}
                                    <div className="space-y-2">
                                        <div className="text-xs font-mono text-disco-muted uppercase">Engaging Hostiles</div>
                                        {Object.entries(combatState.token_manager?.active_tokens || {}).length === 0 ? (
                                            <div className="text-sm text-disco-muted italic p-2">None</div>
                                        ) : (
                                            Object.entries(combatState.token_manager.active_tokens).map(([id, token]) => (
                                                <div key={id} className="flex justify-between bg-disco-red/10 border-l-2 border-disco-red p-3 animate-in slide-in-from-left">
                                                    <span className="font-bold text-disco-red tracking-wide">{id}</span>
                                                    <span className="text-xs font-mono text-disco-red/70">ATTACKING ({token.duration}s left)</span>
                                                </div>
                                            ))
                                        )}
                                    </div>

                                    {/* Cooldowns */}
                                    <div className="space-y-2">
                                        <div className="text-xs font-mono text-disco-muted uppercase">Regrouping</div>
                                        {Object.entries(combatState.token_manager?.cooldowns || {}).length === 0 ? (
                                            <div className="text-sm text-disco-muted italic p-2">None</div>
                                        ) : (
                                            Object.entries(combatState.token_manager.cooldowns).map(([id, time]) => (
                                                <div key={id} className="flex justify-between bg-disco-yellow/5 border-l-2 border-disco-yellow/50 p-2 opacity-70">
                                                    <span className="text-disco-paper/80">{id}</span>
                                                    <span className="text-xs font-mono text-disco-yellow">WAITING ({time}s)</span>
                                                </div>
                                            ))
                                        )}
                                    </div>

                                    {/* NPC Intelligence (Plans) */}
                                    <div className="space-y-2 border-t border-disco-cyan/10 pt-4">
                                        <div className="text-xs font-mono text-disco-cyan/70 uppercase">Agent Intentions</div>
                                        {Object.entries(combatState.npc_intelligence || {}).map(([id, intel]) => (
                                            <div key={id} className="text-[10px] font-mono bg-black/40 p-2 border border-disco-cyan/5">
                                                <div className="flex justify-between mb-1">
                                                    <span className="text-disco-paper font-bold">{id}</span>
                                                    <span className="text-disco-cyan/60">{intel.goal}</span>
                                                </div>
                                                <div className="flex gap-1 overflow-x-auto pb-1">
                                                    {intel.plan.length === 0 ? (
                                                        <span className="text-disco-muted italic">[No Plan]</span>
                                                    ) : (
                                                        intel.plan.map((step, i) => (
                                                            <span key={i} className={`px-1 border ${i === 0 ? 'border-disco-cyan text-disco-cyan bg-disco-cyan/10' : 'border-disco-muted/30 text-disco-muted'}`}>
                                                                {step}
                                                            </span>
                                                        ))
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Right: Attack Grid */}
                            <div className="border border-disco-cyan/20 bg-black/40 p-6 relative flex flex-col">
                                <h3 className="font-mono text-sm text-disco-cyan/70 uppercase mb-4 border-b border-disco-cyan/10 pb-2">
                                    Tactical Grid
                                </h3>

                                {/* Center (Player) */}
                                <div className="flex-1 flex items-center justify-center relative min-h-[300px]">
                                    {/* Rings */}
                                    <div className="absolute inset-0 border border-disco-cyan/10 rounded-full scale-75 animate-pulse-slow"></div>
                                    <div className="absolute inset-0 border border-dashed border-disco-cyan/10 rounded-full scale-100"></div>

                                    {/* Player Icon */}
                                    <div className="w-16 h-16 bg-disco-cyan rounded-full flex items-center justify-center shadow-[0_0_20px_#6be4e3] z-20 relative">
                                        <span className="text-2xl text-black">YOU</span>
                                        {/* Vision Cone */}
                                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] bg-gradient-to-t from-disco-cyan/20 to-transparent -rotate-45"
                                            style={{ clipPath: 'polygon(50% 50%, 0% 0%, 100% 0%)' }}
                                        />
                                    </div>

                                    {/* Slots */}
                                    {/* We visualize the slots around the player */}
                                    <div className="absolute top-10 left-1/2 -translate-x-1/2">
                                        <SlotIndicator name="FRONT"
                                            occupant={combatState.attack_grid?.slots?.ENGAGED?.primary}
                                            active={true} />
                                    </div>
                                    <div className="absolute top-20 right-10">
                                        <SlotIndicator name="FLANK R"
                                            occupant={combatState.attack_grid?.slots?.FLANK?.right} />
                                    </div>
                                    <div className="absolute top-20 left-10">
                                        <SlotIndicator name="FLANK L"
                                            occupant={combatState.attack_grid?.slots?.FLANK?.left} />
                                    </div>
                                    <div className="absolute bottom-10 left-1/2 -translate-x-1/2">
                                        <SlotIndicator name="REAR"
                                            occupant={combatState.attack_grid?.slots?.REAR?.center}
                                            color="border-disco-red/40" />
                                    </div>
                                </div>

                                <div className="mt-4 text-[10px] font-mono text-center text-disco-muted">
                                    GRID STATUS: ACTIVE • SENSORS ONLINE
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// Helper for grid slots
const SlotIndicator = ({ name, occupant, active, color = "border-disco-cyan/40" }) => {
    return (
        <div className={`flex flex-col items-center gap-1 transition-all duration-300 ${occupant ? 'scale-110' : 'opacity-50'}`}>
            <div className={`w-12 h-12 border-2 ${color} ${occupant ? 'bg-disco-red/20 border-disco-red shadow-[0_0_15px_#ff003c]' : 'bg-black/50'} flex items-center justify-center rounded-sm backdrop-blur-sm`}>
                {occupant && <span className="text-xl">👾</span>}
            </div>
            <div className="bg-black/80 px-2 py-0.5 text-[9px] text-disco-paper font-bold tracking-widest border border-disco-muted/30">
                {occupant || name}
            </div>
        </div>
    );
};

export default CombatDashboard;
