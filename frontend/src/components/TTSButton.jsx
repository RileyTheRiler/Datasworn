import React, { useState, useEffect } from 'react';

const TTSButton = ({ text, label = "Read Aloud", className = "", asSpan = false }) => {
    const [isSpeaking, setIsSpeaking] = useState(false);

    useEffect(() => {
        // Cleanup on unmount
        return () => {
            if (isSpeaking) {
                window.speechSynthesis.cancel();
            }
        };
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    const toggleSpeech = (e) => {
        e.stopPropagation(); // Prevent triggering parent click

        if (isSpeaking) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        } else {
            window.speechSynthesis.cancel(); // Stop any current speech
            const utterance = new SpeechSynthesisUtterance(text);

            // Optional: Select a better voice if available
            const voices = window.speechSynthesis.getVoices();
            // Try to find a google voice or natural sounding voice
            const preferredVoice = voices.find(v => v.name.includes("Google") || v.name.includes("Natural")) || voices[0];
            if (preferredVoice) utterance.voice = preferredVoice;

            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = () => setIsSpeaking(false);

            window.speechSynthesis.speak(utterance);
            setIsSpeaking(true);
        }
    };

    const handleKeyDown = (e) => {
        // Make span keyboard accessible
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleSpeech(e);
        }
    };

    const commonClassName = `p-2 rounded-full hover:bg-white/10 transition-colors z-10 ${isSpeaking ? 'text-disco-cyan animate-pulse' : 'text-disco-muted hover:text-disco-paper'} ${className}`;

    const iconContent = (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            {isSpeaking ? (
                <>
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                </>
            ) : (
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            )}
        </svg>
    );

    if (asSpan) {
        return (
            <span
                onClick={toggleSpeech}
                onKeyDown={handleKeyDown}
                className={`${commonClassName} cursor-pointer inline-block`}
                role="button"
                tabIndex="0"
                title={label}
                aria-label={label}
            >
                {iconContent}
            </span>
        );
    }

    return (
        <button
            onClick={toggleSpeech}
            className={commonClassName}
            title={label}
            aria-label={label}
        >
            {iconContent}
        </button>
    );
};

export default TTSButton;
