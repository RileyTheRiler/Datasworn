import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';

const VoiceContext = createContext();

export const useVoice = () => {
    const context = useContext(VoiceContext);
    if (!context) {
        throw new Error('useVoice must be used within a VoiceProvider');
    }
    return context;
};

export const VoiceProvider = ({ children }) => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [voiceEnabled, setVoiceEnabled] = useState(true);
    const [supported, setSupported] = useState(false);
    const [transcript, setTranscript] = useState("");

    const recognitionRef = useRef(null);
    const synthRef = useRef(window.speechSynthesis);

    useEffect(() => {
        // Check for SpeechRecognition support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            setSupported(true);
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;
            recognitionRef.current.lang = 'en-US';

            recognitionRef.current.onstart = () => setIsListening(true);
            recognitionRef.current.onend = () => setIsListening(false);
            recognitionRef.current.onresult = (event) => {
                const result = event.results[0][0].transcript;
                console.log('Voice transcript:', result);
                setTranscript(result);
                // In a real implementation, this might trigger a callback or dispatch an action
                if (window.handleVoiceInput) {
                    window.handleVoiceInput(result);
                }
            };
            recognitionRef.current.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                setIsListening(false);
            };
        }
    }, []);

    const startListening = useCallback(() => {
        if (recognitionRef.current && !isListening) {
            try {
                recognitionRef.current.start();
            } catch (err) {
                console.error('Failed to start recognition', err);
            }
        }
    }, [isListening]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
        }
    }, [isListening]);

    const speak = useCallback((text) => {
        if (!voiceEnabled || !synthRef.current) return;

        // Cancel any ongoing speech
        synthRef.current.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = () => setIsSpeaking(false);

        // Optional: select a specific voice if available
        const voices = synthRef.current.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Premium')) || voices[0];
        if (preferredVoice) utterance.voice = preferredVoice;

        synthRef.current.speak(utterance);
    }, [voiceEnabled]);

    const value = {
        isListening,
        isSpeaking,
        voiceEnabled,
        setVoiceEnabled,
        supported,
        startListening,
        stopListening,
        speak,
        transcript,
        setTranscript
    };

    return (
        <VoiceContext.Provider value={value}>
            {children}
        </VoiceContext.Provider>
    );
};
