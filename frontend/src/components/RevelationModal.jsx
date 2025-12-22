import React, { useState } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';

const API_URL = 'http://localhost:8001/api';

/**
 * RevelationModal - Handles Stages 1-3 of the Revelation Ladder
 * - Mirror Moment (Passive Observation)
 * - Cost Revealed (Confrontation)
 * - Origin Glimpsed (Insight)
 */
const RevelationModal = ({ isOpen, onClose, sessionId = 'default', stage, data, onComplete }) => {
    const [submitting, setSubmitting] = useState(false);

    if (!isOpen || !data) return null;

    const handleResponse = async (responseType) => {
        setSubmitting(true);
        try {
            const response = await fetch(`${API_URL}/narrative/revelation/respond`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    stage: stage,
                    scene_id: data.scene_id,
                    response_type: responseType,
                    wound_type: data.player_wound
                })
            });

            if (response.ok) {
                onComplete?.();
                onClose();
            }
        } catch (err) {
            console.error('Error submitting revelation response:', err);
        } finally {
            setSubmitting(false);
        }
    };

    // Render logic based on stage
    const renderContent = () => {
        switch (stage) {
            case 'mirror_moment':
                return (
                    <>
                        <div className="border-l-4 border-disco-cyan/30 pl-6 mb-8">
                            <h3 className="text-disco-cyan font-mono text-sm uppercase mb-2">Reflected Pattern</h3>
                            <TypewriterText
                                text={data.content}
                                baseSpeed={15}
                                className="font-serif text-lg leading-relaxed text-disco-paper"
                            />
                        </div>
                        <div className="flex justify-end">
                            <button
                                onClick={() => handleResponse('observed')}
                                disabled={submitting}
                                className="px-8 py-3 bg-disco-cyan/20 border border-disco-cyan text-disco-cyan hover:bg-disco-cyan hover:text-black transition-all font-mono uppercase tracking-widest"
                            >
                                {submitting ? 'Recording...' : 'Observe'}
                            </button>
                        </div>
                    </>
                );

            case 'cost_revealed':
                return (
                    <>
                        <div className="bg-disco-red/10 border border-disco-red/30 p-6 rounded mb-6">
                            <h3 className="text-disco-red font-mono text-sm uppercase mb-2">The Cost</h3>
                            <p className="font-serif text-disco-paper/90 mb-4">{data.harm_description}</p>
                        </div>
                        <div className="border-l-4 border-disco-paper/30 pl-6 mb-8">
                            <TypewriterText
                                text={data.dialogue}
                                baseSpeed={15}
                                className="font-serif text-lg leading-relaxed text-disco-paper font-italic"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => handleResponse('deflect')}
                                disabled={submitting}
                                className="p-4 border border-disco-muted text-disco-muted hover:border-disco-paper hover:text-disco-paper transition-all font-mono uppercase text-sm"
                            >
                                Deflect
                            </button>
                            <button
                                onClick={() => handleResponse('accept')}
                                disabled={submitting}
                                className="p-4 bg-disco-red/20 border border-disco-red text-disco-red hover:bg-disco-red hover:text-black transition-all font-mono uppercase text-sm"
                            >
                                Accept Responsibility
                            </button>
                        </div>
                    </>
                );

            case 'origin_glimpsed':
                return (
                    <>
                        <div className="mb-6">
                            <p className="font-mono text-xs text-disco-purple mb-2">TRIGGER EVENT</p>
                            <p className="font-serif text-disco-paper/80 italic">{data.trigger_event}</p>
                        </div>
                        <div className="bg-disco-dark/50 border border-disco-purple/30 p-6 rounded mb-6">
                            <TypewriterText
                                text={data.prompt}
                                baseSpeed={20}
                                className="font-serif text-lg text-disco-cyan mb-4 block"
                            />
                            <div className="h-px w-full bg-disco-purple/20 my-4" />
                            <TypewriterText
                                text={data.revelation}
                                baseSpeed={20}
                                startDelay={2000}
                                className="font-serif text-lg text-disco-paper block"
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => handleResponse('withhold')}
                                disabled={submitting}
                                className="p-4 border border-disco-muted text-disco-muted hover:border-disco-paper hover:text-disco-paper transition-all font-mono uppercase text-sm"
                            >
                                Withhold
                            </button>
                            <button
                                onClick={() => handleResponse('share')}
                                disabled={submitting}
                                className="p-4 bg-disco-purple/20 border border-disco-purple text-disco-purple hover:bg-disco-purple hover:text-black transition-all font-mono uppercase text-sm"
                            >
                                Share Truth
                            </button>
                        </div>
                    </>
                );

            default:
                return <div className="text-disco-red">Unknown revelation stage: {stage}</div>;
        }
    };

    const getTitle = () => {
        switch (stage) {
            case 'mirror_moment': return 'A Familiar Pattern';
            case 'cost_revealed': return 'The Price Paid';
            case 'origin_glimpsed': return 'Echoes of the Past';
            default: return 'Revelation';
        }
    };

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={onClose}
            title={getTitle()}
            defaultWidth={700}
            defaultHeight={data.stage === 'origin_glimpsed' ? 600 : 500}
        >
            <div className="h-full flex flex-col bg-disco-bg/95 p-8 overflow-y-auto">
                {renderContent()}
            </div>
        </DraggableModal>
    );
};

export default RevelationModal;
