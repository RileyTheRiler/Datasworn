import React, { useState, useEffect } from 'react';

const CopingPanel = ({ sessionId = 'default' }) => {
    const [mechanisms, setMechanisms] = useState([]);
    const [profile, setProfile] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    // Fetch available mechanisms
    useEffect(() => {
        fetchAvailableMechanisms();
        fetchProfile();
    }, []);

    const fetchAvailableMechanisms = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/psyche/available-coping/${sessionId}`);
            const data = await res.json();
            setMechanisms(data.mechanisms || []);
        } catch (err) {
            console.error('Failed to fetch mechanisms:', err);
        }
    };

    const fetchProfile = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/psyche/${sessionId}`);
            const data = await res.json();
            setProfile(data.profile || data);
        } catch (err) {
            console.error('Failed to fetch profile:', err);
        }
    };

    const applyCoping = async (mechanismId) => {
        setLoading(true);
        setResult(null);

        try {
            const res = await fetch('http://localhost:8000/api/psyche/coping', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    mechanism_id: mechanismId,
                    success: Math.random() > 0.3 // 70% success rate
                })
            });

            const data = await res.json();
            setResult(data.result);
            setProfile(data.profile);

            // Refresh mechanisms (availability may change)
            fetchAvailableMechanisms();
        } catch (err) {
            console.error('Failed to apply coping:', err);
        } finally {
            setLoading(false);
        }
    };

    const mechanismLabels = {
        meditate: { name: 'Meditate', icon: '🧘', color: 'cyan' },
        journal: { name: 'Journal', icon: '📝', color: 'blue' },
        vent_to_crew: { name: 'Vent to Crew', icon: '💬', color: 'green' },
        exercise: { name: 'Exercise', icon: '💪', color: 'orange' },
        art_therapy: { name: 'Art Therapy', icon: '🎨', color: 'purple' },
        prayer: { name: 'Prayer', icon: '🙏', color: 'yellow' },
        stim_injection: { name: 'Stim Injection', icon: '💉', color: 'red' },
        substance_abuse: { name: 'Substance Abuse', icon: '🍺', color: 'red' },
        self_isolation: { name: 'Self-Isolation', icon: '🚪', color: 'gray' },
    };

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 max-w-md">
            <h3 className="text-lg font-bold text-cyan-400 mb-3">Coping Mechanisms</h3>

            {profile && (
                <div className="mb-4 text-xs text-slate-400">
                    <div>Stress: <span className="text-red-400">{Math.round(profile.stress_level * 100)}%</span></div>
                    <div>Sanity: <span className="text-purple-400">{Math.round(profile.sanity * 100)}%</span></div>
                </div>
            )}

            <div className="grid grid-cols-2 gap-2 mb-4">
                {mechanisms.map(mechId => {
                    const mech = mechanismLabels[mechId] || { name: mechId, icon: '❓', color: 'gray' };
                    return (
                        <button
                            key={mechId}
                            onClick={() => applyCoping(mechId)}
                            disabled={loading}
                            className={`p-3 rounded border-2 border-${mech.color}-500/50 bg-${mech.color}-950/30 
                                hover:bg-${mech.color}-900/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed`}
                        >
                            <div className="text-2xl mb-1">{mech.icon}</div>
                            <div className="text-xs text-slate-300">{mech.name}</div>
                        </button>
                    );
                })}
            </div>

            {result && (
                <div className={`p-3 rounded text-sm ${result.success ? 'bg-green-950/50 border border-green-700' : 'bg-red-950/50 border border-red-700'}`}>
                    <div className="font-bold mb-1">{result.mechanism}</div>
                    {result.success && (
                        <>
                            <div className="text-green-300">✓ Stress reduced by {Math.round(result.stress_reduced * 100)}%</div>
                            {result.sanity_cost && <div className="text-red-300">⚠ Sanity cost: {Math.round(result.sanity_cost * 100)}%</div>}
                            {result.warning && <div className="text-yellow-300 mt-2">⚠ {result.warning}</div>}
                            {result.side_effect && <div className="text-slate-400 text-xs mt-1">{result.side_effect}</div>}
                        </>
                    )}
                    {!result.success && (
                        <div className="text-red-300">{result.message}</div>
                    )}
                </div>
            )}
        </div>
    );
};

export default CopingPanel;
