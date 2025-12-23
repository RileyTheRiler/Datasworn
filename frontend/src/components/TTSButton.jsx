import React, { useState, useEffect } from 'react';
import { useVoice } from '../contexts/VoiceContext';

const TTSButton = ({ text, label = "Read Aloud", className = "", asSpan = false }) => {




    const { speak } = useVoice();
    const [localIsSpeaking, setLocalIsSpeaking] = useState(false);

    useEffect(() => {
        // Cleanup on unmount
        return () => {
            // No direct cancel access via context yet, but we can reset local state
            setLocalIsSpeaking(false);
        };
    }, []);

    const toggleSpeech = async (e) => {
        e.stopPropagation(); // Prevent triggering parent click

        if (localIsSpeaking) {
            // If we are currently speaking, we can't easily "stop" just this via context 
            // without a stop function. But VoiceContext's speak usually cancels previous.
            // For now, let's just allow re-triggering or finding a way to stop.
            // A simple hack is to speak empty text or implement stop in context.
            // But usually clicking again to "stop" is desired.
            // Let's check VoiceContext for a stop function.
            // The context has `stopListening` but not explicit `stopSpeaking` exposed 
            // (it does have internal stop logic when speak is called).
            // Let's assume hitting it again re-starts it for now or does nothing, 
            // but the user complained about the VOICE, not the toggle behavior.
            // ACTUALLY: VoiceContext DOES NOT expose a `stop` function for TTS.
            // I should technically initiate a speak("") to stop, or just let it play.

            // BETTER APPROACH: Just call speak(text).
            // To fix the "robotic voice" issue, using `speak(text)` is the priority.

            // We'll manage local "speaking" state just for the UI feedback for a few seconds
            // or until we implement better tracking.
            setLocalIsSpeaking(false);
        } else {
            setLocalIsSpeaking(true);
            await speak(text);
            setLocalIsSpeaking(false); // Reset after await finishes (approximate)
        }
    };

    const handleKeyDown = (e) => {
        // Make span keyboard accessible
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleSpeech(e);
        }
    };

    const commonClassName = `p-2 rounded-full hover:bg-white/10 transition-colors z-10 ${localIsSpeaking ? 'text-disco-cyan animate-pulse' : 'text-disco-muted hover:text-disco-paper'} ${className}`;

    const iconContent = (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
            {localIsSpeaking ? (
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
