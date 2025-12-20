import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const RumorBoard = ({ sessionId, visible, onClose }) => {
    const [rumors, setRumors] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (visible) {
            fetchRumors();
        }
    }, [visible]);

    const fetchRumors = async () => {
        setLoading(true);
        try {
            const data = await api.get(`/rumors/active/${sessionId}`);
            // If empty, auto-seed one for demo
            if (!data.rumors || data.rumors.length === 0) {
                const newRumor = await api.post('/rumors/generate', {
                    session_id: sessionId,
                    source: "System Scan",
                    category: "mystery"
                });
                setRumors([newRumor.rumor]);
            } else {
                setRumors(data.rumors);
            }
        } catch (err) {
            console.error("Failed to fetch rumors:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleInvestigate = async (rumorId) => {
        setLoading(true);
        try {
            const result = await api.post('/rumors/investigate', {
                session_id: sessionId,
                rumor_id: rumorId,
                success: true // In a real game, this would depend on a roll
            });

            // Show result (simple alert for MVP, should be a toast)
            alert(result.message);
            fetchRumors();
        } catch (err) {
            console.error("Investigation failed:", err);
        } finally {
            setLoading(false);
        }
    };

    if (!visible) return null;

    const getCategoryStyle = (category) => {
        switch (category) {
            case 'treasure': return 'bg-disco-yellow/10 border-disco-yellow text-disco-yellow';
            case 'danger': return 'bg-disco-red/10 border-disco-red text-disco-red';
            case 'opportunity': return 'bg-disco-cyan/10 border-disco-cyan text-disco-cyan';
            case 'mystery': return 'bg-disco-purple/10 border-disco-purple text-disco-purple';
            default: return 'bg-disco-muted/10 border-disco-muted text-disco-muted';
        }
    };

    return (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center animate-fadeIn">
            <div className="bg-disco-panel border-2 border-disco-yellow p-6 rounded-lg max-w-3xl w-full max-h-[85vh] overflow-y-auto shadow-hard relative">
                {/* Header */}
                <div className="flex justify-between items-center mb-6 border-b border-disco-yellow/30 pb-4">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl">📡</span>
                        <div>
                            <h2 className="text-3xl font-serif font-bold text-disco-yellow tracking-wider">RUMOR NETWORK</h2>
                            <p className="text-disco-paper/60 font-mono text-xs uppercase tracking-[0.2em]">Interstellar Chatter</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-red text-2xl"
                    >
                        ×
                    </button>
                </div>

                {loading && rumors.length === 0 ? (
                    <div className="text-center py-12 text-disco-yellow animate-pulse font-mono">
                        Scanning frequencies...
                    </div>
                ) : rumors.length === 0 ? (
                    <div className="text-center py-12 text-disco-muted italic">
                        The void is silent. No active rumors.
                    </div>
                ) : (
                    <div className="space-y-4">
                        {rumors.map(rumor => (
                            <div
                                key={rumor.id}
                                className="bg-black/40 border-l-4 p-4 rounded-r relative overflow-hidden group hover:bg-black/60 transition-colors"
                                style={{
                                    borderLeftColor:
                                        rumor.category === 'treasure' ? '#fbbf24' :
                                            rumor.category === 'danger' ? '#ef4444' :
                                                rumor.category === 'opportunity' ? '#22d3ee' :
                                                    '#c084fc'
                                }}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-xl font-bold text-disco-paper">{rumor.title}</h3>
                                    <span className={`text-[10px] px-2 py-0.5 rounded font-mono uppercase tracking-wider border ${getCategoryStyle(rumor.category)}`}>
                                        {rumor.category}
                                    </span>
                                </div>

                                <p className="text-disco-paper/80 font-serif leading-relaxed italic mb-4">
                                    "{rumor.description}"
                                </p>

                                <div className="flex items-center gap-6 text-xs font-mono text-disco-muted border-t border-white/5 pt-3">
                                    <span className="flex items-center gap-1">
                                        <span className="text-disco-paper/40">SOURCE:</span> {rumor.source}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <span className="text-disco-paper/40">RELIABILITY:</span>
                                        <span className={rumor.reliability > 0.7 ? "text-disco-green" : "text-disco-yellow"}>
                                            {Math.round(rumor.reliability * 100)}%
                                        </span>
                                    </span>
                                    <span className="flex items-center gap-1 ml-auto">
                                        <span className="text-disco-paper/40">EXPIRES:</span>
                                        {new Date(rumor.expires_at).toLocaleDateString()}
                                    </span>
                                </div>

                                <div className="mt-4 flex justify-end">
                                    <button
                                        onClick={() => handleInvestigate(rumor.id)}
                                        className="btn-disco-secondary px-4 py-1.5 text-xs uppercase tracking-wider hover:bg-white/10"
                                        disabled={loading}
                                    >
                                        Investigate
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default RumorBoard;
