import React, { useState, useEffect } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';

const API_URL = 'http://localhost:8001/api';

/**
 * MurderRevelationModal - Displays the 5-phase murder revelation
 * Shows Yuki's confession and the mirror dialogue based on player's archetype
 */
const MurderRevelationModal = ({ isOpen, onClose, sessionId = 'default', onComplete }) => {
    const [currentPhase, setCurrentPhase] = useState(0);
    const [revelationData, setRevelationData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [yukiPortrait, setYukiPortrait] = useState(null);

    // Fetch revelation data when modal opens
    useEffect(() => {
        if (isOpen && !revelationData) {
            fetchRevelation();
            fetchYukiPortrait();
        }
    }, [isOpen]);

    const fetchRevelation = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/narrative/murder-resolution?session_id=${sessionId}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch revelation: ${response.statusText}`);
            }
            const data = await response.json();
            setRevelationData(data);
        } catch (err) {
            console.error('Error fetching revelation:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchYukiPortrait = async () => {
        try {
            // Use 'security' as the NPC ID (matches RelationshipWeb crew ID)
            const response = await fetch(`${API_URL}/npc/security?session_id=${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                setYukiPortrait(data.image_url);
            }
        } catch (err) {
            console.error('Error fetching Yuki portrait:', err);
        }
    };

    const handleNext = () => {
        if (!revelationData) return;

        const nextPhase = currentPhase + 1;
        if (nextPhase >= revelationData.revelation.phases.length) {
            // All phases complete
            onComplete?.();
        } else {
            setCurrentPhase(nextPhase);
        }
    };

    const handleClose = () => {
        setCurrentPhase(0);
        setRevelationData(null);
        onClose();
    };

    if (!isOpen) return null;

    if (loading) {
        return (
            <DraggableModal
                isOpen={isOpen}
                onClose={handleClose}
                title="The Truth Emerges"
                defaultWidth={800}
                defaultHeight={600}
            >
                <div className="flex items-center justify-center h-full">
                    <div className="text-disco-cyan font-mono text-lg animate-pulse">
                        Loading revelation...
                    </div>
                </div>
            </DraggableModal>
        );
    }

    if (error) {
        return (
            <DraggableModal
                isOpen={isOpen}
                onClose={handleClose}
                title="Error"
                defaultWidth={600}
                defaultHeight={400}
            >
                <div className="p-8 text-disco-red">
                    <p className="font-mono">Error loading revelation:</p>
                    <p className="mt-4 text-disco-muted">{error}</p>
                    <button
                        onClick={handleClose}
                        className="mt-6 px-6 py-2 border border-disco-muted hover:bg-disco-accent hover:text-black transition-colors"
                    >
                        Close
                    </button>
                </div>
            </DraggableModal>
        );
    }

    if (!revelationData) return null;

    const phase = revelationData.revelation.phases[currentPhase];
    const totalPhases = revelationData.revelation.phases.length;
    const isLastPhase = currentPhase === totalPhases - 1;

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={handleClose}
            title={`The Murder Solution Mirror - ${phase.name}`}
            defaultWidth={900}
            defaultHeight={700}
            className="bg-disco-bg"
        >
            <div className="flex flex-col h-full">
                {/* Phase Progress Indicator */}
                <div className="px-8 pt-6 pb-4 border-b border-disco-muted/30">
                    <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-sm text-disco-muted">
                            Phase {currentPhase + 1} of {totalPhases}
                        </span>
                        <span className="font-mono text-xs text-disco-cyan">
                            {revelationData.player_wound.toUpperCase()}
                        </span>
                    </div>
                    <div className="w-full bg-disco-dark/50 h-1 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-disco-cyan transition-all duration-500"
                            style={{ width: `${((currentPhase + 1) / totalPhases) * 100}%` }}
                        />
                    </div>
                </div>

                {/* Content Area */}
                <div className="flex-1 overflow-y-auto p-8">
                    <div className="max-w-3xl mx-auto space-y-6">
                        {/* Yuki Portrait (show on phases 2, 4) */}
                        {(currentPhase === 1 || currentPhase === 3) && yukiPortrait && (
                            <div className="flex justify-center mb-6">
                                <div className="relative">
                                    <img
                                        src={yukiPortrait}
                                        alt="Yuki"
                                        className="w-32 h-32 rounded-full border-2 border-disco-cyan/50 shadow-lg"
                                    />
                                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-disco-dark px-3 py-1 rounded-full border border-disco-cyan/30">
                                        <span className="text-disco-cyan font-mono text-xs">YUKI</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Phase Description */}
                        <div className="text-disco-muted/70 font-mono text-sm italic text-center mb-4">
                            {phase.description}
                        </div>

                        {/* Phase Content */}
                        <div className="bg-disco-dark/30 border border-disco-muted/20 rounded-lg p-6">
                            {phase.narrative_beat && (
                                <div className="prose prose-invert max-w-none">
                                    <TypewriterText
                                        text={phase.narrative_beat}
                                        baseSpeed={15}
                                        className="font-serif text-lg leading-relaxed text-disco-paper"
                                    />
                                </div>
                            )}

                            {phase.discovery_highlight && (
                                <div className="mt-6 p-6 border-l-4 border-amber-500 bg-amber-500/10 rounded-r-lg animate-fade-in-up">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-amber-500 text-lg">💡</span>
                                        <span className="font-mono text-xs uppercase tracking-widest text-amber-500 font-bold">New Insight</span>
                                    </div>
                                    <TypewriterText
                                        text={phase.discovery_highlight}
                                        baseSpeed={20}
                                        delay={1000}
                                        className="font-serif text-xl italic text-amber-100"
                                    />
                                </div>
                            )}

                            {phase.dialogue && (
                                <div className="mt-4 border-l-4 border-disco-cyan/50 pl-6">
                                    <TypewriterText
                                        text={phase.dialogue}
                                        baseSpeed={15}
                                        className="font-serif text-lg leading-relaxed text-disco-cyan whitespace-pre-line"
                                    />
                                </div>
                            )}

                            {phase.question && (
                                <div className="mt-6 p-6 bg-disco-accent/10 border border-disco-accent/30 rounded-lg">
                                    <div className="text-disco-accent font-mono text-xs uppercase tracking-wider mb-3">
                                        The Question
                                    </div>
                                    <TypewriterText
                                        text={phase.question}
                                        baseSpeed={15}
                                        className="font-serif text-xl leading-relaxed text-disco-paper italic"
                                    />
                                </div>
                            )}
                        </div>

                        {/* Meta Analysis (show on last phase) */}
                        {isLastPhase && revelationData.revelation.meta_analysis && (
                            <div className="mt-6 space-y-4 text-sm">
                                <div className="bg-disco-purple/10 border border-disco-purple/30 rounded-lg p-4">
                                    <div className="text-disco-purple font-mono text-xs uppercase mb-2">
                                        What the Mirror Shows
                                    </div>
                                    <p className="text-disco-paper/80 font-serif leading-relaxed">
                                        {revelationData.revelation.meta_analysis.what_mirror_shows}
                                    </p>
                                </div>
                                <div className="bg-disco-red/10 border border-disco-red/30 rounded-lg p-4">
                                    <div className="text-disco-red font-mono text-xs uppercase mb-2">
                                        The Parallel
                                    </div>
                                    <p className="text-disco-paper/80 font-serif leading-relaxed">
                                        {revelationData.revelation.meta_analysis.parallel}
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Navigation Footer */}
                <div className="px-8 py-6 border-t border-disco-muted/30 flex items-center justify-between bg-disco-dark/30">
                    <button
                        onClick={handleClose}
                        className="px-6 py-2 border border-disco-muted/50 text-disco-muted hover:text-disco-paper hover:border-disco-paper transition-colors font-mono text-sm"
                    >
                        [ Close ]
                    </button>

                    <div className="flex items-center gap-4">
                        {currentPhase > 0 && (
                            <button
                                onClick={() => setCurrentPhase(currentPhase - 1)}
                                className="px-6 py-2 border border-disco-cyan/50 text-disco-cyan hover:bg-disco-cyan hover:text-black transition-colors font-mono text-sm"
                            >
                                ← Previous
                            </button>
                        )}

                        <button
                            onClick={handleNext}
                            className={`px-8 py-3 border font-serif text-lg transition-all ${isLastPhase
                                ? 'border-disco-accent bg-disco-accent/20 text-disco-accent hover:bg-disco-accent hover:text-black shadow-[0_0_20px_rgba(107,228,227,0.3)]'
                                : 'border-disco-cyan text-disco-cyan hover:bg-disco-cyan hover:text-black'
                                }`}
                        >
                            {isLastPhase ? 'Make Your Choice →' : 'Continue →'}
                        </button>
                    </div>
                </div>
            </div>
        </DraggableModal>
    );
};

export default MurderRevelationModal;
