import React, { useState, useEffect } from 'react';

const PsycheDashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isCollapsed, setIsCollapsed] = useState(() => {
        // Load collapse state from localStorage
        const saved = localStorage.getItem('psycheDashboardCollapsed');
        return saved === 'true';
    });

    // Persist collapse state
    useEffect(() => {
        localStorage.setItem('psycheDashboardCollapsed', isCollapsed);
    }, [isCollapsed]);

    // Poll every 2 seconds
    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/psyche/default');
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                }
            } catch (err) {
                console.error("Failed to fetch psyche data", err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        // Reduced from 2s to 10s to save battery and reduce server load
        const interval = setInterval(() => {
            if (!document.hidden) fetchData(); // Pause when tab inactive
        }, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading || !data) return null;

    // Radar Chart Logic
    const regions = [
        { key: 'amygdala', label: 'Amygdala' },
        { key: 'cortex', label: 'Cortex' },
        { key: 'hippocampus', label: 'Hippocampus' },
        { key: 'brain_stem', label: 'Brain Stem' },
        { key: 'temporal', label: 'Temporal' }
    ];

    const dominance = data.voice_dominance || {};

    // Calculate specific points
    const points = regions.map((r, i) => {
        const value = dominance[r.key] || 0.1; // Min value for visibility
        const angle = (Math.PI / 2) + (2 * Math.PI * i / 5);
        const x = 100 + (value * 80) * Math.cos(angle);
        const y = 100 - (value * 80) * Math.sin(angle);
        return `${x},${y}`;
    }).join(" ");

    const isHijacked = !!data.active_hijack;
    const profile = data.profile || {};

    return (
        <div className={`psyche-dashboard fixed bottom-4 right-4 p-4 rounded-xl border backdrop-blur-md transition-all duration-500 ${isCollapsed ? 'w-48' : 'w-64'} ${isHijacked ? 'bg-red-950/90 border-red-500 animate-pulse' : 'bg-slate-900/80 border-slate-700'}`}>
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 text-center flex-1">Neuro-Status</h3>
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="text-slate-400 hover:text-cyan-400 transition-colors ml-2"
                    title={isCollapsed ? "Expand" : "Collapse"}
                >
                    <svg
                        className={`w-4 h-4 transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>
            </div>

            {!isCollapsed && (
                <>

                    {/* Vital Signs (Stress & Sanity) */}
                    <div className="space-y-2 mb-4">
                        <div>
                            <div className="flex justify-between text-[10px] uppercase text-slate-500 mb-1">
                                <span>Stress</span>
                                <span className={profile.stress_level > 0.7 ? "text-red-400" : "text-cyan-400"}>
                                    {Math.round(profile.stress_level * 100)}%
                                </span>
                            </div>
                            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-500 ${profile.stress_level > 0.7 ? 'bg-red-500' : 'bg-cyan-500'}`}
                                    style={{ width: `${profile.stress_level * 100}%` }}
                                />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-[10px] uppercase text-slate-500 mb-1">
                                <span>Sanity</span>
                                <span className={profile.sanity < 0.3 ? "text-red-400" : "text-emerald-400"}>
                                    {Math.round(profile.sanity * 100)}%
                                </span>
                            </div>
                            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-500 ${profile.sanity < 0.3 ? 'bg-red-500' : 'bg-emerald-500'}`}
                                    style={{ width: `${profile.sanity * 100}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Current Emotion */}
                    <div className="text-center mb-4 p-1 bg-slate-800/50 rounded border border-slate-700/50">
                        <span className="text-[10px] uppercase text-slate-500 block">Primary Emotion</span>
                        <span className="text-xs font-bold text-cyan-400 uppercase tracking-widest">{profile.current_emotion || "Neutral"}</span>
                    </div>

                    {/* Hijack Warning */}
                    {isHijacked && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-50">
                            <div className="text-red-500 font-mono text-center">
                                <h1 className="text-2xl font-bold">SYSTEM HIJACK</h1>
                                <p>{data.active_hijack.aspect} OVERRIDE</p>
                            </div>
                        </div>
                    )}

                    {/* Radar Chart */}
                    <div className="relative w-48 h-48 mx-auto">
                        <svg viewBox="0 0 200 200" className="w-full h-full">
                            {/* Background Grid */}
                            <circle cx="100" cy="100" r="80" fill="none" stroke="#334155" strokeWidth="1" />
                            <circle cx="100" cy="100" r="40" fill="none" stroke="#334155" strokeWidth="1" />

                            {/* Data Shape */}
                            <polygon points={points} fill="rgba(56, 189, 248, 0.3)" stroke="#38bdf8" strokeWidth="2" />

                            {/* Labels */}
                            {regions.map((r, i) => {
                                const angle = (Math.PI / 2) + (2 * Math.PI * i / 5);
                                const x = 100 + 95 * Math.cos(angle);
                                const y = 100 - 95 * Math.sin(angle);
                                return (
                                    <text
                                        key={r.key}
                                        x={x}
                                        y={y}
                                        fill={dominance[r.key] > 0.8 ? "#ef4444" : "#94a3b8"}
                                        fontSize="8"
                                        textAnchor="middle"
                                        alignmentBaseline="middle"
                                    >
                                        {r.label}
                                    </text>
                                );
                            })}
                        </svg>
                    </div>

                    {/* Memory Status */}
                    <div className="mt-4 border-t border-slate-700 pt-2">
                        <h4 className="text-[10px] text-slate-500 uppercase">Memory Fragments</h4>
                        <div className="flex gap-1 mt-1 flex-wrap">
                            {data.unlocked_memories.length > 0 ? (
                                data.unlocked_memories.map(m => (
                                    <span key={m} className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_5px_cyan]" title={m} />
                                ))
                            ) : (
                                <span className="text-[10px] text-slate-600 italic">No fragments recovered.</span>
                            )}
                        </div>
                    </div>

                    {/* Trauma Scars */}
                    {profile.trauma_scars && profile.trauma_scars.length > 0 && (
                        <div className="mt-3 border-t border-red-800/50 pt-2">
                            <h4 className="text-[10px] text-red-400 uppercase font-bold">Trauma Scars</h4>
                            <div className="space-y-1 mt-1">
                                {profile.trauma_scars.map((scar, idx) => (
                                    <div key={idx} className="text-[10px] text-red-300/80 bg-red-950/30 p-1 rounded" title={scar.description}>
                                        ⚠ {scar.name}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Phobias */}
                    {data.phobias && data.phobias.length > 0 && (
                        <div className="mt-3 border-t border-yellow-800/50 pt-2">
                            <h4 className="text-[10px] text-yellow-400 uppercase font-bold">Phobias</h4>
                            <div className="space-y-1.5 mt-1">
                                {data.phobias.map((phobia, idx) => (
                                    <div key={idx} className="space-y-0.5">
                                        <div className="flex justify-between text-[9px] text-yellow-300/70">
                                            <span>{phobia.name}</span>
                                            <span>{Math.round(phobia.panic * 100)}% Panic</span>
                                        </div>
                                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full transition-all duration-500 ${phobia.panic > 0.8 ? 'bg-red-500 animate-pulse' : 'bg-yellow-500'}`}
                                                style={{ width: `${phobia.panic * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Addictions */}
                    {data.addictions && data.addictions.length > 0 && (
                        <div className="mt-3 border-t border-orange-800/50 pt-2">
                            <h4 className="text-[10px] text-orange-400 uppercase font-bold">Addictions</h4>
                            <div className="space-y-1.5 mt-1">
                                {data.addictions.map((addiction, idx) => (
                                    <div key={idx} className="space-y-0.5">
                                        <div className="flex justify-between text-[9px] text-orange-300/70">
                                            <span>{addiction.substance}</span>
                                            <span className={addiction.satisfaction < 0.3 ? 'text-red-400' : ''}>
                                                {addiction.satisfaction < 0.3 ? 'CRAVING' : `${Math.round(addiction.satisfaction * 100)}%`}
                                            </span>
                                        </div>
                                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full transition-all duration-500 ${addiction.satisfaction < 0.3 ? 'bg-red-500 animate-pulse' : 'bg-orange-500'}`}
                                                style={{ width: `${addiction.satisfaction * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Guilt Level */}
                    {data.guilt > 0.1 && (
                        <div className="mt-3 border-t border-indigo-800/50 pt-2">
                            <div className="flex justify-between text-[10px] uppercase text-slate-500 mb-1">
                                <span>Moral Burden</span>
                                <span className={data.guilt > 0.5 ? "text-indigo-400" : "text-slate-400"}>
                                    {Math.round(data.guilt * 100)}%
                                </span>
                            </div>
                            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full transition-all duration-500 ${data.guilt > 0.7 ? 'bg-indigo-400' : 'bg-indigo-600'}`}
                                    style={{ width: `${data.guilt * 100}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {/* Suppressed Memories */}
                    {profile.suppressed_memories && profile.suppressed_memories.length > 0 && (
                        <div className="mt-3 border-t border-purple-800/50 pt-2">
                            <h4 className="text-[10px] text-purple-400 uppercase font-bold">Suppressed Memories</h4>
                            <div className="space-y-1.5 mt-1">
                                {profile.suppressed_memories.filter(m => !m.is_revealed).map((mem, idx) => (
                                    <div key={idx} className="space-y-0.5">
                                        <div className="flex justify-between text-[9px] text-purple-300/70">
                                            <span>Seal #{idx + 1}</span>
                                            <span>{Math.round(mem.seal_integrity * 100)}%</span>
                                        </div>
                                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-purple-500 transition-all duration-500"
                                                style={{ width: `${mem.seal_integrity * 100}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Dominant Trait */}
                    {profile.dominant_trait && (
                        <div className="mt-3 text-center text-[10px] text-slate-400">
                            <span className="uppercase tracking-widest">Dominant: </span>
                            <span className="text-cyan-300 font-bold">{profile.dominant_trait}</span>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default PsycheDashboard;
