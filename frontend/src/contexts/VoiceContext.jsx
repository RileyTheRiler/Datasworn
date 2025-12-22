import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { Howl } from 'howler';

const VoiceContext = createContext();

export const useVoice = () => {
    const context = useContext(VoiceContext);
    if (!context) {
        throw new Error('useVoice must be used within a VoiceProvider');
    }
    return context;
};

// ElevenLabs voice profiles available
// Maps friendly names and IDs to the backend archetypes
const VOICE_PROFILES = {
    'narrator_female': {
        id: 'narrator_female',
        name: 'Narrator (Female)',
        archetype: 'enigmatic_oracle', // Corresponding backend archetype
        description: 'Mysterious, calm female narrator',
        lang: 'en-US'
    },
    'narrator_male': {
        id: 'narrator_male',
        name: 'Narrator (Male)',
        archetype: 'gruff_veteran',
        description: 'Deep, authoritative male narrator',
        lang: 'en-US'
    },
    'scholar': {
        id: 'scholar',
        name: 'Scholar',
        archetype: 'nervous_scholar',
        description: 'Analytical, quick-speaking',
        lang: 'en-US'
    },
    'merchant': {
        id: 'merchant',
        name: 'Merchant',
        archetype: 'pragmatic_merchant',
        description: 'Smooth, persuasive',
        lang: 'en-US'
    },
    'rebel': {
        id: 'rebel',
        name: 'Rebel',
        archetype: 'charismatic_rebel',
        description: 'Passionate, energetic',
        lang: 'en-US'
    }
};

export const VoiceProvider = ({ children }) => {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [voiceEnabled, setVoiceEnabled] = useState(true);
    const [supported, setSupported] = useState(false);
    const [transcript, setTranscript] = useState("");

    // Convert VOICE_PROFILES object to array for UI consumption
    const [availableVoices, setAvailableVoices] = useState(Object.values(VOICE_PROFILES));

    // Initialize selectedVoice immediately from localStorage or default
    const [selectedVoice, setSelectedVoice] = useState(() => {
        if (typeof window === 'undefined') return VOICE_PROFILES['narrator_female'];
        const savedVoiceId = localStorage.getItem('tts_voice_preference');
        if (savedVoiceId && VOICE_PROFILES[savedVoiceId]) {
            return VOICE_PROFILES[savedVoiceId];
        }
        return VOICE_PROFILES['narrator_female'];
    });

    const recognitionRef = useRef(null);
    const currentAudioRef = useRef(null);

    // Save voice preference when it changes
    useEffect(() => {
        if (selectedVoice) {
            localStorage.setItem('tts_voice_preference', selectedVoice.id);
        }
    }, [selectedVoice]);

    // Global audio unlock for Howler and SpeechSynthesis
    useEffect(() => {
        const unlock = () => {
            if (Howler.ctx && Howler.ctx.state === 'suspended') {
                Howler.ctx.resume().then(() => {
                    console.log('Audio Context unlocked');
                });
            }
            window.removeEventListener('click', unlock);
            window.removeEventListener('keydown', unlock);
        };
        window.addEventListener('click', unlock);
        window.addEventListener('keydown', unlock);
        return () => {
            window.removeEventListener('click', unlock);
            window.removeEventListener('keydown', unlock);
        };
    }, []);

    // Speech Recognition setup (Browser native)
    useEffect(() => {
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

    const speak = useCallback(async (text) => {
        if (!voiceEnabled || !selectedVoice) return;
        if (!text) return;

        console.log(`[TTS] Initiating narration with voice: ${selectedVoice.name}`);

        // Stop any currently playing audio
        if (currentAudioRef.current) {
            currentAudioRef.current.stop();
            currentAudioRef.current = null;
        }

        // Cancel any pending browser speech
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }

        setIsSpeaking(true);

        // Fallback function using browser TTS
        const speakFallback = () => {
            console.log('[TTS] Falling back to browser speech synthesis');
            if (!window.speechSynthesis) {
                setIsSpeaking(false);
                return;
            }
            const utterance = new SpeechSynthesisUtterance(text);
            // Try to find a nice female voice for fallback if possible
            const voices = window.speechSynthesis.getVoices();
            const preferred = voices.find(v => v.name.includes('Google') || v.name.includes('Premium') || v.name.includes('Female')) || voices[0];
            if (preferred) utterance.voice = preferred;
            utterance.onend = () => setIsSpeaking(false);
            utterance.onerror = () => setIsSpeaking(false);
            window.speechSynthesis.speak(utterance);
        };

        try {
            // Call backend to generate TTS with ElevenLabs
            const response = await fetch('http://localhost:8000/api/audio/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                timeout: 5000, // 5 second timeout
                body: JSON.stringify({
                    session_id: 'default',
                    text: text,
                    character_archetype: selectedVoice.archetype
                })
            });

            if (!response.ok) {
                console.warn(`[TTS] Backend returned error: ${response.status}`);
                speakFallback();
                return;
            }

            const data = await response.json();

            if (data.audio_url) {
                console.log('[TTS] Playing ElevenLabs audio stream');
                // Play the generated audio using Howler
                const audio = new Howl({
                    src: [`http://localhost:8000${data.audio_url}`],
                    format: ['mp3'],
                    html5: true,
                    volume: 1.0,
                    onend: () => {
                        setIsSpeaking(false);
                        currentAudioRef.current = null;
                    },
                    onloaderror: (id, error) => {
                        console.error('[TTS] Audio load error:', error);
                        speakFallback();
                    },
                    onplayerror: (id, error) => {
                        console.error('[TTS] Audio play error:', error);
                        speakFallback();
                    }
                });

                currentAudioRef.current = audio;
                audio.play();
            } else {
                console.warn("[TTS] No audio URL returned from backend, triggering fallback");
                speakFallback();
            }
        } catch (error) {
            console.error('[TTS] Synthesis error:', error);
            speakFallback();
        }
    }, [voiceEnabled, selectedVoice]);

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
        setTranscript,
        availableVoices,
        selectedVoice,
        setSelectedVoice
    };

    return (
        <VoiceContext.Provider value={value}>
            {children}
        </VoiceContext.Provider>
    );
};
