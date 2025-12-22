import React, { useState, useEffect } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';

const API_URL = 'http://localhost:8001/api';

/**
 * ChoiceCrystallizedModal - Stage 4 of the Revelation Ladder
 * Ember names the player's pattern and asks for a response.
 */
const ChoiceCrystallizedModal = ({ isOpen, onClose, sessionId = 'default', onComplete }) => {
    const [scene, setScene] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [selectedChoice, setSelectedChoice] = useState(null);

    useEffect(() => {
        if (isOpen && !scene) {
            fetchScene();
        }
    }, [isOpen]);

    const fetchScene = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/narrative/revelation/choice-crystallized?session_id=${sessionId}`, {
                method: 'POST'
            });
            if (response.ok) {
                const data = await response.json();
                setScene(data);
            }
        } catch (err) {
            console.error('Error fetching choice crystallized scene:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleChoiceSelect = async (choice) => {
        if (submitting) return;
        setSelectedChoice(choice);
        setSubmitting(true);

        try {
            const response = await fetch(`${API_URL}/narrative/revelation/respond`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    stage: 'choice_crystallized',
                    scene_id: scene.scene_id,
                    response_type: choice.type,
                    wound_type: scene.player_wound
                })
            });

            if (response.ok) {
                onComplete?.(choice.type);
            }
        } catch (err) {
            console.error('Error submitting choice:', err);
        } finally {
            setSubmitting(false);
        }
    };

    if (!isOpen) return null;

    if (loading) {
        return (
            <DraggableModal isOpen={isOpen} onClose={onClose} title="A Moment of Clarity" defaultWidth={600} defaultHeight={400}>
                <div className="flex items-center justify-center h-full">
                    <div className="text-disco-cyan font-mono animate-pulse text-lg">Seeking patterns...</div>
                </div>
            </DraggableModal>
        );
    }

    if (!scene) return null;

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={onClose}
            title={`Revelation: ${scene.pattern_name}`}
            defaultWidth={800}
            defaultHeight={600}
        >
            <div className="flex flex-col h-full bg-disco-bg/95">
                {/* Header */}
                <div className="px-8 py-6 border-b border-disco-cyan/20 bg-disco-dark/50">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full border-2 border-disco-purple shadow-[0_0_15px_rgba(147,51,234,0.3)] bg-disco-dark flex items-center justify-center overflow-hidden">
                            <span className="text-disco-purple font-mono text-xl">E</span>
                        </div>
                        <div>
                            <div className="text-disco-purple font-mono text-xs uppercase tracking-widest mb-1">Ember Observes</div>
                            <div className="text-disco-paper font-serif italic text-sm opacity-80">{scene.ember_observation}</div>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-8">
                    <div className="max-w-2xl mx-auto">
                        <div className="border-l-4 border-disco-purple/40 pl-8 py-4 mb-10">
                            <TypewriterText
                                text={scene.dialogue}
                                baseSpeed={20}
                                className="font-serif text-xl leading-relaxed text-disco-paper"
                            />
                        </div>

                        {/* Choices */}
                        <div className="space-y-4">
                            <div className="text-disco-cyan font-mono text-xs uppercase tracking-widest mb-4">How do you respond?</div>
                            {scene.choices.map((choice) => (
                                <button
                                    key={choice.id}
                                    onClick={() => handleChoiceSelect(choice)}
                                    disabled={submitting}
                                    className={`w-full p-4 border transition-all duration-300 transform hover:-translate-y-1 text-left flex items-center justify-between group
                                        ${selectedChoice?.id === choice.id
                                            ? 'border-disco-cyan bg-disco-cyan/20 text-disco-cyan'
                                            : 'border-disco-muted/30 bg-disco-dark/40 text-disco-paper/70 hover:border-disco-cyan/50 hover:bg-disco-dark/60 hover:text-disco-paper'
                                        }
                                        ${submitting && selectedChoice?.id !== choice.id ? 'opacity-50 cursor-not-allowed' : ''}
                                    `}
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-2 h-2 rounded-full transition-colors ${selectedChoice?.id === choice.id ? 'bg-disco-cyan animate-pulse' : 'bg-disco-muted group-hover:bg-disco-cyan/50'}`} />
                                        <span className="font-serif text-lg">{choice.text}</span>
                                    </div>
                                    <div className="font-mono text-[10px] opacity-0 group-hover:opacity-100 transition-opacity uppercase tracking-tighter">[{choice.type}]</div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="px-8 py-4 border-t border-disco-muted/10 bg-disco-dark/30 text-center">
                    <p className="text-[10px] font-mono text-disco-muted uppercase tracking-[0.3em]">Revelation Stage IV : Choice Crystallized</p>
                </div>
            </div>
        </DraggableModal>
    );
};

export default ChoiceCrystallizedModal;
