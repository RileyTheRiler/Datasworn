import React, { useState } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';

const API_URL = 'http://localhost:8001/api';

/**
 * HeroTragedyChoice - Final moral choice after the murder revelation
 * Presents Hero vs Tragedy path based on player's archetype
 */
const HeroTragedyChoice = ({
    isOpen,
    onClose,
    question,
    playerWound,
    sessionId = 'default',
    onChoiceMade,
    onComplete
}) => {
    const [selectedChoice, setSelectedChoice] = useState(null);
    const [showConfirmation, setShowConfirmation] = useState(false);
    const [loading, setLoading] = useState(false);
    const [sequenceData, setSequenceData] = useState(null);
    const [currentStage, setCurrentStage] = useState('decision'); // decision, test, resolution, wisdom, final_scene
    const [path, setPath] = useState(null); // hero or tragedy

    // Fetch ending sequence
    React.useEffect(() => {
        const fetchSequence = async () => {
            if (isOpen) {
                setLoading(true);
                try {
                    const res = await fetch(`${API_URL}/narrative/ending/sequence?session_id=${sessionId}`);
                    if (res.ok) {
                        const data = await res.json();
                        setSequenceData(data);
                    }
                } catch (err) {
                    console.error('Failed to fetch ending sequence:', err);
                } finally {
                    setLoading(false);
                }
            }
        };
        fetchSequence();
    }, [isOpen, sessionId]);

    const activeQuestion = question || sequenceData?.moral_question || "What is your choice?";
    const activeArchetype = playerWound || sequenceData?.archetype;

    // Define choice options based on sequence data
    const getChoiceOptions = () => {
        if (sequenceData?.decision_options) {
            return {
                hero: {
                    label: sequenceData.decision_options.accept || 'Extend Mercy',
                    description: 'Let go of control. Trust the crew to decide.',
                    color: 'disco-cyan',
                    icon: '🕊️'
                },
                tragedy: {
                    label: sequenceData.decision_options.reject || 'Take Control',
                    description: 'You must decide. The crew cannot be trusted with this.',
                    color: 'disco-red',
                    icon: '⚖️'
                }
            };
        }

        const baseChoices = {
            hero: {
                label: 'Extend Mercy',
                description: 'Let go of control. Trust the crew to decide.',
                color: 'disco-cyan',
                icon: '🕊️'
            },
            tragedy: {
                label: 'Take Control',
                description: 'You must decide. The crew cannot be trusted with this.',
                color: 'disco-red',
                icon: '⚖️'
            }
        };

        // Fallback customizations based on wound type
        switch (activeArchetype?.toLowerCase()) {
            case 'controller':
                baseChoices.hero.label = 'Let Go';
                baseChoices.hero.description = 'Let the crew decide Yuki\'s fate. Release your need for control.';
                baseChoices.tragedy.label = 'Maintain Control';
                baseChoices.tragedy.description = 'You know what must be done. Make the decision yourself.';
                break;
            case 'judge':
                baseChoices.hero.label = 'Extend Understanding';
                baseChoices.hero.description = 'Accept the complexity. Yuki is both victim and perpetrator.';
                baseChoices.tragedy.label = 'Pass Judgment';
                baseChoices.tragedy.description = 'Murder is murder. Condemn her for what she did.';
                break;
            case 'ghost':
                baseChoices.hero.label = 'Connect';
                baseChoices.hero.description = 'Let yourself be seen. Show Yuki she\'s not alone.';
                baseChoices.tragedy.label = 'Withdraw';
                baseChoices.tragedy.description = 'Keep your distance. This isn\'t your burden to carry.';
                break;
            case 'fugitive':
                baseChoices.hero.label = 'Face It';
                baseChoices.hero.description = 'Stop running. Confront what needs to be confronted.';
                baseChoices.tragedy.label = 'Keep Running';
                baseChoices.tragedy.description = 'This isn\'t your problem. Move on.';
                break;
            case 'cynic':
                baseChoices.hero.label = 'Trust';
                baseChoices.hero.description = 'Give the crew a chance. Maybe they\'ll surprise you.';
                baseChoices.tragedy.label = 'Assume the Worst';
                baseChoices.tragedy.description = 'People always disappoint. Act accordingly.';
                break;
            // Add more cases as needed
        }

        return baseChoices;
    };

    const choices = getChoiceOptions();

    const handleChoiceSelect = (choiceType) => {
        setSelectedChoice(choiceType);
        setShowConfirmation(true);
    };

    const handleConfirm = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/narrative/ending/decision`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    choice: selectedChoice === 'hero' ? 'accept' : 'reject'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to submit ending decision');
            }

            const data = await response.json();
            setPath(data.ending_type);

            // Start at 'decision' beat
            setCurrentStage('decision');
            setShowConfirmation(false);

            // Notify parent
            onChoiceMade?.(selectedChoice, data.ending_type);
        } catch (err) {
            console.error('Error recording choice:', err);
            // Fallback
            setPath(selectedChoice === 'hero' ? 'hero' : 'tragedy');
            setCurrentStage('decision');
            setShowConfirmation(false);
        } finally {
            setLoading(false);
        }
    };

    const handleNextStage = () => {
        const stages = ['decision', 'test', 'resolution', 'wisdom', 'final_scene'];
        const currentIndex = stages.indexOf(currentStage);
        if (currentIndex < stages.length - 1) {
            setCurrentStage(stages[currentIndex + 1]);
        } else {
            handleClose();
            onComplete?.();
        }
    };

    const handleCancel = () => {
        setSelectedChoice(null);
        setShowConfirmation(false);
    };

    const handleClose = () => {
        setSelectedChoice(null);
        setShowConfirmation(false);
        setPath(null);
        setCurrentStage('decision');
        onClose();
    };

    if (!isOpen) return null;

    // Show ending narration and progression
    if (path) {
        const stageTitleMap = {
            'decision': path === 'hero' ? "The Hero's Decision" : "The Tragedy's Decision",
            'test': path === 'hero' ? "The Test of Character" : "Doubling Down",
            'resolution': path === 'hero' ? "Resolution" : "Catastrophe",
            'wisdom': "The Wisdom Gained",
            'final_scene': "Final Scene"
        };

        const currentText = sequenceData?.[`${path}_path`]?.[currentStage] || "The end is near...";
        const color = path === 'hero' ? 'disco-cyan' : 'disco-red';

        return (
            <DraggableModal
                isOpen={isOpen}
                onClose={handleClose}
                title={stageTitleMap[currentStage]}
                defaultWidth={800}
                defaultHeight={600}
            >
                <div className="flex flex-col h-full bg-disco-bg/95">
                    <div className="flex-1 overflow-y-auto p-10">
                        <div className="max-w-3xl mx-auto">
                            <div className={`border-l-4 border-${color} pl-8 mb-8`}>
                                <TypewriterText
                                    key={currentStage} // Force restart on stage change
                                    text={currentText}
                                    baseSpeed={15}
                                    className="font-serif text-xl leading-relaxed text-disco-paper whitespace-pre-line"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="px-10 py-8 border-t border-disco-muted/30 bg-disco-dark/50 flex justify-center">
                        <button
                            onClick={handleNextStage}
                            className={`px-12 py-4 border-2 border-${color} text-${color} hover:bg-${color} hover:text-black transition-all font-serif text-xl uppercase tracking-widest shadow-[0_0_15px_rgba(255,255,255,0.05)]`}
                        >
                            {currentStage === 'final_scene' ? 'Complete Journey' : 'Continue'}
                        </button>
                    </div>
                </div>
            </DraggableModal>
        );
    }

    // Show confirmation dialog
    if (showConfirmation) {
        const choice = choices[selectedChoice];
        return (
            <DraggableModal
                isOpen={isOpen}
                onClose={handleCancel}
                title="Confirm Your Choice"
                defaultWidth={600}
                defaultHeight={400}
            >
                <div className="flex flex-col h-full">
                    <div className="flex-1 p-8 flex flex-col items-center justify-center">
                        <div className={`text-6xl mb-6`}>{choice.icon}</div>
                        <h3 className={`text-2xl font-serif text-${choice.color} mb-4`}>
                            {choice.label}
                        </h3>
                        <p className="text-disco-paper/80 text-center max-w-md mb-8">
                            {choice.description}
                        </p>
                        <p className="text-disco-muted text-sm italic text-center">
                            This choice will shape your ending. Are you certain?
                        </p>
                    </div>
                    <div className="px-8 py-6 border-t border-disco-muted/30 bg-disco-dark/30 flex justify-between">
                        <button
                            onClick={handleCancel}
                            className="px-6 py-2 border border-disco-muted text-disco-muted hover:text-disco-paper hover:border-disco-paper transition-colors"
                            disabled={loading}
                        >
                            Go Back
                        </button>
                        <button
                            onClick={handleConfirm}
                            className={`px-12 py-3 border border-${choice.color} bg-${choice.color}/20 text-${choice.color} hover:bg-${choice.color} hover:text-black transition-all font-serif text-lg ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                            disabled={loading}
                        >
                            {loading ? 'Recording...' : 'I Am Certain'}
                        </button>
                    </div>
                </div>
            </DraggableModal>
        );
    }

    // Show choice selection
    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={handleClose}
            title="The Choice"
            defaultWidth={900}
            defaultHeight={700}
        >
            <div className="flex flex-col h-full">
                {/* The Question */}
                <div className="px-8 pt-8 pb-6 border-b border-disco-muted/30">
                    <div className="max-w-3xl mx-auto">
                        <div className="text-disco-accent font-mono text-xs uppercase tracking-wider mb-4">
                            Yuki asks you:
                        </div>
                        <p className="font-serif text-2xl leading-relaxed text-disco-paper italic">
                            {activeQuestion}
                        </p>
                    </div>
                </div>

                {/* Choice Cards */}
                <div className="flex-1 overflow-y-auto p-8">
                    <div className="max-w-4xl mx-auto grid grid-cols-2 gap-8">
                        {/* Hero Choice */}
                        <button
                            onClick={() => handleChoiceSelect('hero')}
                            className="group relative bg-disco-dark/30 border-2 border-disco-cyan/30 rounded-lg p-8 hover:border-disco-cyan hover:bg-disco-cyan/10 transition-all duration-300 text-left"
                        >
                            <div className="absolute top-4 right-4 text-4xl opacity-50 group-hover:opacity-100 transition-opacity">
                                {choices.hero.icon}
                            </div>
                            <h3 className="text-2xl font-serif text-disco-cyan mb-4">
                                {choices.hero.label}
                            </h3>
                            <p className="text-disco-paper/80 leading-relaxed mb-6">
                                {choices.hero.description}
                            </p>
                            <div className="text-disco-cyan/60 text-sm font-mono">
                                → The Hero's Path
                            </div>
                        </button>

                        {/* Tragedy Choice */}
                        <button
                            onClick={() => handleChoiceSelect('tragedy')}
                            className="group relative bg-disco-dark/30 border-2 border-disco-red/30 rounded-lg p-8 hover:border-disco-red hover:bg-disco-red/10 transition-all duration-300 text-left"
                        >
                            <div className="absolute top-4 right-4 text-4xl opacity-50 group-hover:opacity-100 transition-opacity">
                                {choices.tragedy.icon}
                            </div>
                            <h3 className="text-2xl font-serif text-disco-red mb-4">
                                {choices.tragedy.label}
                            </h3>
                            <p className="text-disco-paper/80 leading-relaxed mb-6">
                                {choices.tragedy.description}
                            </p>
                            <div className="text-disco-red/60 text-sm font-mono">
                                → The Tragedy's Path
                            </div>
                        </button>
                    </div>
                </div>

                {/* Footer */}
                <div className="px-8 py-6 border-t border-disco-muted/30 bg-disco-dark/30 text-center">
                    <p className="text-disco-muted text-sm font-mono">
                        Choose carefully. This decision cannot be undone.
                    </p>
                </div>
            </div>
        </DraggableModal>
    );
};

export default HeroTragedyChoice;
