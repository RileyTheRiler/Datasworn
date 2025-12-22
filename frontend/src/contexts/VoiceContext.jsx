import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';

/**
 * VoiceContext - Provides Text-to-Speech and Speech-to-Text functionality
 *
 * Features:
 * - Text-to-Speech using Web Speech API (SpeechSynthesis)
 * - Speech-to-Text using Web Speech API (SpeechRecognition)
 * - Voice selection and customization
 * - Persistent settings in localStorage
 */

const VoiceContext = createContext(null);

export const useVoice = () => {
    const context = useContext(VoiceContext);
    if (!context) {
        throw new Error('useVoice must be used within VoiceProvider');
    }
    return context;
};

export const VoiceProvider = ({ children }) => {
    // TTS (Text-to-Speech) state
    const [voiceEnabled, setVoiceEnabled] = useState(() => {
        const saved = localStorage.getItem('voiceEnabled');
        return saved ? JSON.parse(saved) : false;
    });

    const [isSpeaking, setIsSpeaking] = useState(false);
    const [availableVoices, setAvailableVoices] = useState([]);
    const [selectedVoice, setSelectedVoice] = useState(null);

    const [rate, setRate] = useState(() => {
        const saved = localStorage.getItem('voiceRate');
        return saved ? parseFloat(saved) : 1.0;
    });

    const [pitch, setPitch] = useState(() => {
        const saved = localStorage.getItem('voicePitch');
        return saved ? parseFloat(saved) : 1.0;
    });

    const [volume, setVolume] = useState(() => {
        const saved = localStorage.getItem('voiceVolume');
        return saved ? parseFloat(saved) : 1.0;
    });

    // STT (Speech-to-Text) state
    const [isListening, setIsListening] = useState(false);
    const [supported, setSupported] = useState(false);
    const [transcript, setTranscript] = useState('');

    const recognitionRef = useRef(null);
    const utteranceRef = useRef(null);

    // Check browser support for Speech Recognition
    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const speechSynthesisSupported = 'speechSynthesis' in window;

        setSupported(!!SpeechRecognition && speechSynthesisSupported);

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const current = event.resultIndex;
                const transcriptText = event.results[current][0].transcript;
                setTranscript(transcriptText);
                setIsListening(false);
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                setIsListening(false);
            };

            recognition.onend = () => {
                setIsListening(false);
            };

            recognitionRef.current = recognition;
        }
    }, []);

    // Load available voices for TTS
    useEffect(() => {
        if (!('speechSynthesis' in window)) return;

        const loadVoices = () => {
            const voices = window.speechSynthesis.getVoices();
            setAvailableVoices(voices);

            // Try to select a good default voice
            if (!selectedVoice && voices.length > 0) {
                const saved = localStorage.getItem('selectedVoice');
                if (saved) {
                    const voice = voices.find(v => v.name === saved);
                    if (voice) {
                        setSelectedVoice(voice);
                        return;
                    }
                }

                // Fallback: prefer English voices
                const englishVoice = voices.find(v => v.lang.startsWith('en'));
                setSelectedVoice(englishVoice || voices[0]);
            }
        };

        loadVoices();

        // Voices may load asynchronously
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = loadVoices;
        }
    }, [selectedVoice]);

    // Save settings to localStorage
    useEffect(() => {
        localStorage.setItem('voiceEnabled', JSON.stringify(voiceEnabled));
    }, [voiceEnabled]);

    useEffect(() => {
        localStorage.setItem('voiceRate', rate.toString());
    }, [rate]);

    useEffect(() => {
        localStorage.setItem('voicePitch', pitch.toString());
    }, [pitch]);

    useEffect(() => {
        localStorage.setItem('voiceVolume', volume.toString());
    }, [volume]);

    useEffect(() => {
        if (selectedVoice) {
            localStorage.setItem('selectedVoice', selectedVoice.name);
        }
    }, [selectedVoice]);

    /**
     * Speak text using Text-to-Speech
     * @param {string} text - The text to speak
     */
    const speak = useCallback((text) => {
        if (!voiceEnabled || !('speechSynthesis' in window)) return;

        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }

        utterance.rate = rate;
        utterance.pitch = pitch;
        utterance.volume = volume;

        utterance.onstart = () => {
            setIsSpeaking(true);
        };

        utterance.onend = () => {
            setIsSpeaking(false);
        };

        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event.error);
            setIsSpeaking(false);
        };

        utteranceRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    }, [voiceEnabled, selectedVoice, rate, pitch, volume]);

    /**
     * Stop current speech
     */
    const stopSpeaking = useCallback(() => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        }
    }, []);

    /**
     * Start listening for voice input
     */
    const startListening = useCallback(() => {
        if (!recognitionRef.current || isListening) return;

        try {
            setTranscript('');
            recognitionRef.current.start();
            setIsListening(true);
        } catch (err) {
            console.error('Error starting speech recognition:', err);
        }
    }, [isListening]);

    /**
     * Stop listening for voice input
     */
    const stopListening = useCallback(() => {
        if (!recognitionRef.current || !isListening) return;

        try {
            recognitionRef.current.stop();
            setIsListening(false);
        } catch (err) {
            console.error('Error stopping speech recognition:', err);
        }
    }, [isListening]);

    /**
     * Toggle voice enabled/disabled
     */
    const toggleVoice = useCallback(() => {
        setVoiceEnabled(prev => !prev);
        if (isSpeaking) {
            stopSpeaking();
        }
    }, [isSpeaking, stopSpeaking]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
            if (recognitionRef.current && isListening) {
                recognitionRef.current.stop();
            }
        };
    }, [isListening]);

    const value = {
        // TTS
        speak,
        stopSpeaking,
        isSpeaking,
        voiceEnabled,
        setVoiceEnabled,
        toggleVoice,
        availableVoices,
        selectedVoice,
        setSelectedVoice,
        rate,
        setRate,
        pitch,
        setPitch,
        volume,
        setVolume,

        // STT
        isListening,
        startListening,
        stopListening,
        transcript,
        setTranscript,
        supported
    };

    return (
        <VoiceContext.Provider value={value}>
            {children}
        </VoiceContext.Provider>
    );
};

export default VoiceProvider;
