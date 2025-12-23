import React from 'react';
import { useVoice } from '../contexts/VoiceContext';

const VoiceSelector = ({ className = "" }) => {
    const { availableVoices, selectedVoice, setSelectedVoice, speak } = useVoice();

    const handlePlayPreview = (e, voice) => {
        e.stopPropagation();
        const previewText = `This is the ${voice.name} voice. I am ready to chronicle your adventures in the Forge.`;
        // We temporarily play this specific voice without switching yet? 
        // Or just switch and play. Switching is easier.
        setSelectedVoice(voice);
        speak(previewText);
    };

    return (
        <div className={`space-y-4 ${className}`}>
            <h3 className="text-disco-cyan font-mono text-xs uppercase tracking-widest opacity-70">
                Narrator Voice Interface
            </h3>

            <div className="grid grid-cols-1 gap-3">
                {availableVoices.map((voice) => (
                    <div
                        key={voice.id}
                        onClick={() => setSelectedVoice(voice)}
                        className={`
                            relative p-3 rounded border cursor-pointer transition-all group
                            ${selectedVoice?.id === voice.id
                                ? 'bg-disco-cyan/10 border-disco-cyan'
                                : 'bg-black/40 border-disco-muted/20 hover:border-disco-muted/50 hover:bg-white/5'}
                        `}
                    >
                        <div className="flex items-center justify-between gap-3">
                            <div className="flex-1">
                                <div className={`font-serif text-base transition-colors ${selectedVoice?.id === voice.id ? 'text-disco-cyan' : 'text-disco-paper'}`}>
                                    {voice.name}
                                </div>
                                <div className="text-xs text-disco-muted font-mono mt-1">
                                    {voice.description}
                                </div>
                            </div>

                            <button
                                onClick={(e) => handlePlayPreview(e, voice)}
                                className={`
                                    p-2 rounded-full transition-all shrink-0
                                    ${selectedVoice?.id === voice.id
                                        ? 'text-disco-cyan bg-disco-cyan/10 hover:bg-disco-cyan/20'
                                        : 'text-disco-muted hover:text-disco-paper hover:bg-white/10'}
                                `}
                                title="Preview Voice"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                                </svg>
                            </button>
                        </div>

                        {/* Selection Indicator */}
                        {selectedVoice?.id === voice.id && (
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-disco-cyan rounded-l"></div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default VoiceSelector;
