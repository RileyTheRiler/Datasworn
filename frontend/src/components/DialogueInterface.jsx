import React, { useState, useEffect, useRef } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';
import api from '../utils/api';

/**
 * DialogueInterface - General purpose dialogue modal
 */
const DialogueInterface = ({
    isOpen,
    onClose,
    npcId,
    npcName,
    npcPortrait,
    sessionId = 'default'
}) => {
    const [history, setHistory] = useState([]);
    const [currentLine, setCurrentLine] = useState(null);
    const [loading, setLoading] = useState(false);
    const [playerState, setPlayerState] = useState(null); // Could fetch from context
    const bottomRef = useRef(null);

    useEffect(() => {
        if (isOpen && npcId) {
            // Initial greeting
            fetchDialogue('greeting');
        } else {
            setHistory([]);
            setCurrentLine(null);
        }
    }, [isOpen, npcId]);

    useEffect(() => {
        // Auto-scroll to bottom
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history, currentLine]);

    const fetchDialogue = async (interactionType) => {
        setLoading(true);
        try {
            // In a real app, we'd get real player context. 
            // For now, mocking or passing empty to let backend defaults handle it.
            const context = {
                // Example context:
                // player_has_weapon_drawn: false,
                // player_honor: 0.5
            };

            const data = await api.post('/dialogue/select', {
                npc_id: npcId,
                interaction_type: interactionType,
                context: context
            });

            if (data && data.success) {
                const newLine = {
                    id: Date.now(),
                    speaker: npcName || npcId,
                    text: data.text,
                    isPlayer: false,
                    animation: data.animation
                };

                // If there was a previous line, move it to history
                if (currentLine) {
                    setHistory(prev => [...prev, currentLine]);
                }
                setCurrentLine(newLine);
            }
        } catch (err) {
            console.error("Dialogue Error:", err);
            setCurrentLine({
                id: Date.now(),
                speaker: "System",
                text: "*The NPC seems distracted and doesn't respond.*",
                isError: true
            });
        } finally {
            setLoading(false);
        }
    };

    const handlePlayerChoice = (choiceType, choiceLabel) => {
        // Add player line to history
        const playerLine = {
            id: Date.now(),
            speaker: "You",
            text: choiceLabel,
            isPlayer: true
        };

        if (currentLine) {
            setHistory(prev => [...prev, currentLine]);
        }
        setHistory(prev => [...prev, playerLine]);
        setCurrentLine(null); // Clear current while loading

        // Fetch response
        fetchDialogue(choiceType);
    };

    if (!isOpen) return null;

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={onClose}
            title={`Chat: ${npcName || npcId}`}
            defaultWidth={600}
            defaultHeight={500}
        >
            <div className="flex flex-col h-full bg-disco-panel overflow-hidden">
                {/* Dialogue History */}
                <div className="flex-1 p-6 overflow-y-auto bg-black/20 custom-scrollbar space-y-4">

                    {/* Portrait Header */}
                    <div className="flex items-center gap-4 mb-6 border-b border-disco-muted/20 pb-4">
                        <img
                            src={npcPortrait || '/assets/defaults/portrait_placeholder.png'}
                            alt={npcName}
                            className="w-16 h-16 rounded border border-disco-muted/50 object-cover"
                            onError={(e) => e.target.src = '/assets/defaults/portrait_placeholder.png'}
                        />
                        <div>
                            <h3 className="text-lg font-serif text-disco-cyan">{npcName || npcId}</h3>
                            <div className="flex gap-2 text-xs text-disco-muted">
                                <span className="bg-disco-muted/10 px-2 py-0.5 rounded">Neutral</span>
                            </div>
                        </div>
                    </div>

                    {/* History Messages */}
                    {history.map(msg => (
                        <div key={msg.id} className={`flex ${msg.isPlayer ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[80%] p-3 rounded-lg text-sm ${msg.isPlayer
                                    ? 'bg-disco-accent/10 border border-disco-accent/30 text-disco-paper rounded-tr-none'
                                    : 'bg-disco-dark/50 border border-disco-muted/30 text-disco-paper/80 rounded-tl-none'
                                }`}>
                                <div className="text-[10px] uppercase opacity-50 mb-1">{msg.speaker}</div>
                                {msg.text}
                            </div>
                        </div>
                    ))}

                    {/* Current Line (Typewriter) */}
                    {currentLine && !currentLine.isPlayer && (
                        <div className="flex justify-start">
                            <div className="max-w-[90%] p-4 rounded-lg bg-disco-dark border border-disco-cyan/30 shadow-[0_0_15px_rgba(0,0,0,0.3)] text-disco-paper rounded-tl-none">
                                <div className="text-[10px] uppercase text-disco-cyan mb-1 flex justify-between">
                                    <span>{currentLine.speaker}</span>
                                    {currentLine.animation && <span className="italic opacity-50">*{currentLine.animation}*</span>}
                                </div>
                                <TypewriterText
                                    text={currentLine.text}
                                    speed={20}
                                    className="leading-relaxed font-serif text-lg"
                                />
                            </div>
                        </div>
                    )}

                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-disco-dark/30 p-2 rounded-lg flex gap-1">
                                <div className="w-1.5 h-1.5 bg-disco-cyan rounded-full animate-bounce"></div>
                                <div className="w-1.5 h-1.5 bg-disco-cyan rounded-full animate-bounce delay-75"></div>
                                <div className="w-1.5 h-1.5 bg-disco-cyan rounded-full animate-bounce delay-150"></div>
                            </div>
                        </div>
                    )}

                    <div ref={bottomRef} />
                </div>

                {/* Player Choices */}
                <div className="p-4 bg-disco-dark border-t border-disco-muted/20">
                    <div className="grid grid-cols-2 gap-2">
                        <button onClick={() => handlePlayerChoice('chat', 'Tell me more.')} className="btn-disco-secondary text-xs py-2">
                            💬 Chat
                        </button>
                        <button onClick={() => handlePlayerChoice('ask_news', 'Heard any news?')} className="btn-disco-secondary text-xs py-2">
                            📰 Ask News
                        </button>
                        <button onClick={() => handlePlayerChoice('insult', 'You look like a fool.')} className="btn-disco-secondary text-xs py-2 hover:border-disco-red hover:text-disco-red text-left pl-4">
                            😠 Insult
                        </button>
                        <button onClick={onClose} className="border border-disco-muted/30 text-disco-muted text-xs py-2 hover:bg-white/5 rounded">
                            End Conversation
                        </button>
                    </div>
                </div>
            </div>
        </DraggableModal>
    );
};

export default DialogueInterface;
