import React, { useState, useEffect } from 'react';

const TherapyPanel = ({ sessionId = 'default' }) => {
    const [traumaScars, setTraumaScars] = useState([]);
    const [selectedScar, setSelectedScar] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const res = await fetch(`http://localhost:8000/api/psyche/${sessionId}`);
            const data = await res.json();
            const profile = data.profile || data;
            setTraumaScars(profile.trauma_scars || []);
        } catch (err) {
            console.error('Failed to fetch profile:', err);
        }
    };

    const startTherapy = async (scarName) => {
        setLoading(true);
        setResult(null);
        setSelectedScar(scarName);

        try {
            const res = await fetch('http://localhost:8000/api/psyche/therapy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    scar_name: scarName
                })
            });

            const data = await res.json();
            setResult(data);

            // Refresh profile
            fetchProfile();
        } catch (err) {
            console.error('Failed to complete therapy:', err);
        } finally {
            setLoading(false);
        }
    };

    const getStageColor = (stage) => {
        switch (stage) {
            case 'fresh': return 'red';
            case 'healing': return 'yellow';
            case 'scarred': return 'blue';
            case 'integrated': return 'green';
            default: return 'gray';
        }
    };

    const getStageIcon = (stage) => {
        switch (stage) {
            case 'fresh': return '🩸';
            case 'healing': return '🌱';
            case 'scarred': return '⚡';
            case 'integrated': return '✨';
            default: return '❓';
        }
    };

    return (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 max-w-2xl">
            <h3 className="text-lg font-bold text-purple-400 mb-3 flex items-center gap-2">
                <span>🏥</span> Therapy Sessions
            </h3>

            {traumaScars.length === 0 && (
                <div className="text-slate-500 text-sm italic">No trauma scars to heal.</div>
            )}

            <div className="space-y-3">
                {traumaScars.map((scar, idx) => {
                    const stageColor = getStageColor(scar.arc_stage);
                    const stageIcon = getStageIcon(scar.arc_stage);

                    return (
                        <div key={idx} className={`border-2 border-${stageColor}-700/50 bg-${stageColor}-950/20 rounded-lg p-3`}>
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <div className="font-bold text-white flex items-center gap-2">
                                        {stageIcon} {scar.name}
                                    </div>
                                    <div className="text-xs text-slate-400 mt-1">{scar.description}</div>
                                </div>
                                <div className="text-right">
                                    <div className={`text-xs text-${stageColor}-400 uppercase font-bold`}>
                                        {scar.arc_stage}
                                    </div>
                                    <div className="text-xs text-slate-500">
                                        {scar.therapy_sessions || 0} sessions
                                    </div>
                                </div>
                            </div>

                            {/* Progress bar */}
                            <div className="mb-2">
                                <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full bg-${stageColor}-500 transition-all duration-500`}
                                        style={{ width: `${Math.min(100, ((scar.therapy_sessions || 0) / 30) * 100)}%` }}
                                    />
                                </div>
                                <div className="text-xs text-slate-500 mt-1">
                                    Next milestone: {scar.therapy_sessions < 10 ? 10 : scar.therapy_sessions < 20 ? 20 : 30} sessions
                                </div>
                            </div>

                            <button
                                onClick={() => startTherapy(scar.name)}
                                disabled={loading || scar.arc_stage === 'integrated'}
                                className="w-full py-2 px-3 bg-purple-900/50 hover:bg-purple-800/50 border border-purple-700 
                                    rounded text-sm text-purple-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {scar.arc_stage === 'integrated' ? '✓ Fully Integrated' : 'Begin Therapy Session'}
                            </button>
                        </div>
                    );
                })}
            </div>

            {result && (
                <div className="mt-4 p-4 bg-purple-950/50 border border-purple-700 rounded-lg">
                    <div className="font-bold text-purple-300 mb-2">Session Complete</div>

                    {result.arc_result?.transformed && (
                        <div className="bg-green-950/50 border border-green-700 p-3 rounded mb-2">
                            <div className="text-green-300 font-bold">🌟 Transformation!</div>
                            <div className="text-sm text-green-200 mt-1">
                                {result.arc_result.old_name} → {result.arc_result.new_name}
                            </div>
                            <div className="text-xs text-green-400 mt-1">{result.arc_result.message}</div>
                        </div>
                    )}

                    <div className="text-sm text-slate-300">
                        {result.heal_result?.message}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TherapyPanel;
