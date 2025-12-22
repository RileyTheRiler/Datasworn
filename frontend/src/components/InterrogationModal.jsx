import React, { useState, useEffect, useRef } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';

const API_URL = 'http://localhost:8001/api';

/**
 * InterrogationModal - Interactive dialogue tree UI for NPC interrogations
 */
const InterrogationModal = ({
    isOpen,
    onClose,
    npcId,
    npcName,
    sessionId = 'default'
}) => {
    const [currentNode, setCurrentNode] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isComplete, setIsComplete] = useState(false);
    const [signals, setSignals] = useState({});
    const [trustDelta, setTrustDelta] = useState(0);
    const [suspicionDelta, setSuspicionDelta] = useState(0);
    const [history, setHistory] = useState([]);
    const [currentChoiceId, setCurrentChoiceId] = useState(null);

    // Initial node fetch
    useEffect(() => {
        if (isOpen && npcId) {
            startInterrogation();
        }
    }, [isOpen, npcId]);

    const startInterrogation = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_URL}/narrative/interrogate/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, npc_id: npcId })
            });

            if (!res.ok) throw new Error('Failed to start interrogation');

            const data = await res.json();
            setCurrentNode(data);
            setIsComplete(data.is_complete);
            setTrustDelta(0);
            setSuspicionDelta(0);
            setSignals({});
            setHistory([]);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleChoiceSelect = async (choiceId) => {
        if (loading || isComplete) return;

        setLoading(true);
        setCurrentChoiceId(choiceId);
        try {
            const res = await fetch(`${API_URL}/narrative/interrogate/respond`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, choice_id: choiceId })
            });

            if (!res.ok) throw new Error('Failed to advance interrogation');

            const data = await res.json();

            // Record choice in local history for UI effects
            setHistory(prev => [...prev, choiceId]);

            setCurrentNode(data);
            setIsComplete(data.is_complete);
            setSignals(data.signals || {});
            setTrustDelta(data.trust_delta || 0);
            setSuspicionDelta(data.suspicion_delta || 0);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
            setCurrentChoiceId(null);
        }
    };

    if (!isOpen) return null;

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={onClose}
            title={`Interrogation: ${npcName || npcId}`}
            defaultWidth={800}
            defaultHeight={600}
        >
            <div className="flex flex-col h-full bg-disco-panel overflow-hidden">
                {/* NPC Response Area */}
                <div className="flex-1 p-8 overflow-y-auto bg-black/20 custom-scrollbar">
                    {loading && !currentNode && (
                        <div className="flex items-center justify-center h-full">
                            <span className="w-4 h-4 bg-disco-cyan rounded-full animate-ping mr-3" />
                            <span className="font-mono text-disco-cyan uppercase tracking-widest">Opening Frequency...</span>
                        </div>
                    )}

                    {error && (
                        <div className="p-4 border border-disco-red bg-disco-red/10 text-disco-red rounded font-mono text-sm">
                            ERROR: {error}
                            <button onClick={startInterrogation} className="block mt-2 underline">Retry</button>
                        </div>
                    )}

                    {currentNode && (
                        <div className="max-w-2xl mx-auto space-y-6">
                            <div className="flex items-start gap-4">
                                <div className="w-12 h-12 rounded border border-disco-muted/50 overflow-hidden flex-shrink-0 bg-disco-dark">
                                    <img
                                        src={`/api/npc/${npcId}/portrait`} // Assuming this endpoint exists or will
                                        alt={npcName}
                                        className="w-full h-full object-cover"
                                        onError={(e) => e.target.src = '/assets/defaults/portrait_placeholder.png'}
                                    />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-xs font-mono text-disco-accent uppercase mb-2 tracking-tighter opacity-70">
                                        {npcName || npcId}
                                    </h3>
                                    <TypewriterText
                                        text={currentNode.npc_text}
                                        baseSpeed={15}
                                        className="font-serif text-xl leading-relaxed text-disco-paper italic"
                                        onComplete={() => { }}
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Player Choice Area */}
                <div className="p-6 border-t border-disco-muted/20 bg-black/40">
                    <div className="max-w-2xl mx-auto">
                        {isComplete ? (
                            <div className="text-center py-4">
                                <p className="text-disco-cyan font-mono text-sm uppercase tracking-widest mb-4">Interrogation Concluded</p>
                                <button
                                    onClick={onClose}
                                    className="btn-disco text-sm"
                                >
                                    Finish
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-3">
                                {currentNode?.choices?.map((choice) => (
                                    <button
                                        key={choice.id}
                                        onClick={() => handleChoiceSelect(choice.id)}
                                        disabled={loading}
                                        className={`w-full text-left p-4 border border-disco-muted/30 rounded bg-disco-dark/30 hover:bg-disco-cyan/10 hover:border-disco-cyan transition-all duration-200 group relative flex items-center justify-between ${loading && currentChoiceId !== choice.id ? 'opacity-50' : ''}`}
                                    >
                                        <span className="font-serif text-disco-paper group-hover:text-disco-cyan transition-colors">
                                            {choice.text}
                                        </span>
                                        {loading && currentChoiceId === choice.id ? (
                                            <span className="w-2 h-2 bg-disco-cyan rounded-full animate-pulse" />
                                        ) : (
                                            <span className="text-disco-muted/30 group-hover:text-disco-cyan/50 font-mono text-[10px] tracking-widest uppercase">Select</span>
                                        )}
                                    </button>
                                ))}
                                {loading && !currentChoiceId && (
                                    <div className="text-center py-2 animate-pulse">
                                        <span className="font-mono text-xs text-disco-muted uppercase">Processing...</span>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* HUD / Status Bar */}
                <div className="px-6 py-3 border-t border-disco-muted/10 bg-disco-dark flex items-center justify-between text-[10px] font-mono tracking-wider">
                    <div className="flex gap-6">
                        <div className="flex items-center gap-2">
                            <span className="text-disco-muted uppercase">Trust Delta:</span>
                            <span className={trustDelta >= 0 ? 'text-disco-cyan' : 'text-disco-red'}>
                                {trustDelta > 0 ? '+' : ''}{trustDelta.toFixed(1)}
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-disco-muted uppercase">Suspicion Delta:</span>
                            <span className={suspicionDelta <= 0 ? 'text-disco-green' : 'text-disco-red'}>
                                {suspicionDelta > 0 ? '+' : ''}{suspicionDelta.toFixed(1)}
                            </span>
                        </div>
                    </div>
                    <div className="flex gap-4">
                        {Object.entries(signals).map(([signal, count]) => (
                            <div key={signal} className="flex items-center gap-1">
                                <span className="text-disco-accent uppercase">{signal}:</span>
                                <span className="text-disco-paper">{count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </DraggableModal>
    );
};

export default InterrogationModal;
