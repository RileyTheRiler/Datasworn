
import React from 'react';
import { useVoice } from '../contexts/VoiceContext';

const VoiceInput = ({ className = "" }) => {
    const {
        isListening,
        startListening,
        stopListening,
        supported
    } = useVoice();

    if (!supported) return null;

    return (
        <button
            type="button"
            onClick={isListening ? stopListening : startListening}
            className={`px-4 py-2 border border-disco-muted font-serif transition-all flex items-center justify-center min-w-[3rem] ${className} ${isListening
                    ? 'bg-red-900/50 text-red-500 border-red-500 animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.5)]'
                    : 'text-disco-paper hover:bg-disco-accent hover:text-black'
                }`}
            title={isListening ? "Stop Listening" : "Voice Command"}
        >
            {isListening ? (
                <span className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
                    <span>REC</span>
                </span>
            ) : (
                '🎤'
            )}
        </button>
    );
};

export default VoiceInput;
