import React, { useEffect, useRef, useState } from 'react';
import { Howl, Howler } from 'howler';
import { useAudio } from '../contexts/AudioContext';

/**
 * AudioManager - Manages all audio playback using Howler.js
 * Handles 3 channels: ambient, music, voice
 */
const AudioManager = ({ sessionId }) => {
    const { volumes, muted, audioEnabled } = useAudio();

    // Howl instances for each channel
    const ambientRef = useRef(null);
    const musicRef = useRef(null);
    const voiceRef = useRef(null);
    const sfxRefs = useRef({}); // Store active SFX by ID for looping/stopping

    // Current track IDs
    const [currentAmbient, setCurrentAmbient] = useState(null);
    const [currentMusic, setCurrentMusic] = useState(null);
    const [activeSfxCues, setActiveSfxCues] = useState([]); // SFX from psyche engine

    // Polling interval for audio state
    const pollIntervalRef = useRef(null);

    // Initialize Howler global settings
    useEffect(() => {
        Howler.volume(volumes.master);
        Howler.mute(muted);
    }, [volumes.master, muted]);

    // Fetch audio state and psyche state from backend
    const fetchAudioState = async () => {
        if (!audioEnabled || !sessionId) return;

        try {
            // 1. Fetch game-level audio directives (ambient & music)
            const audioRes = await fetch(`/api/audio/state/${sessionId}`);
            if (audioRes.ok) {
                const directives = await audioRes.json();

                if (directives.ambient?.zone_type !== currentAmbient) {
                    updateAmbient(directives.ambient);
                }

                if (directives.music?.track_id !== currentMusic) {
                    updateMusic(directives.music);
                }
            }

            // 2. Fetch psyche-based audio cues (heartbeat, whispers, etc.)
            const psycheRes = await fetch(`/api/psyche/${sessionId}`);
            if (psycheRes.ok) {
                const data = await psycheRes.json();
                const cues = data.audio_cues || []; // Psyche engine returns IDs like 'heartbeat_loop'
                updatePsycheSfx(cues);
            }

        } catch (error) {
            console.error('Failed to fetch audio state:', error);
        }
    };

    // Handle psychological SFX cues
    const updatePsycheSfx = (cues) => {
        // Stop SFX no longer in the cue list
        Object.keys(sfxRefs.current).forEach(id => {
            if (!cues.includes(id)) {
                sfxRefs.current[id].fade(sfxRefs.current[id].volume(), 0, 1000);
                setTimeout(() => {
                    if (sfxRefs.current[id]) {
                        sfxRefs.current[id].stop();
                        delete sfxRefs.current[id];
                    }
                }, 1000);
            }
        });

        // Start new SFX cues
        cues.forEach(id => {
            if (!sfxRefs.current[id]) {
                playSFX(id);
            }
        });

        setActiveSfxCues(cues);
    };

    // Play an SFX (one-shot or looping)
    const playSFX = (id, options = {}) => {
        if (!audioEnabled) return;

        // Custom path logic for SFX
        const isPsych = ["heartbeat_loop", "breathing_heavy", "whispers_distant", "static_interference"].includes(id);
        const folder = isPsych ? "sfx" : "sfx"; // Can be extended
        const trackFile = `/assets/audio/${folder}/${id}.mp3`;

        // Auto-loop if ID contains '_loop' or specified in options
        const shouldLoop = id.includes('_loop') || options.loop;

        // If it's a looping sound already playing, don't restart
        if (shouldLoop && sfxRefs.current[id]) return;

        const sfx = new Howl({
            src: [trackFile],
            loop: shouldLoop,
            volume: options.volume || volumes.ambient, // Default to ambient layer volume
            onend: function () {
                if (!shouldLoop) delete sfxRefs.current[id];
            },
            onloaderror: function (i, e) {
                console.warn(`SFX failed to load: ${trackFile}`, e);
            }
        });

        sfx.play();
        if (shouldLoop) {
            sfxRefs.current[id] = sfx;
        }
    };

    // Update ambient soundscape
    const updateAmbient = (ambientData) => {
        if (!ambientData || !ambientData.tracks || ambientData.tracks.length === 0) {
            // Stop ambient
            if (ambientRef.current) {
                ambientRef.current.fade(volumes.ambient, 0, 1000);
                setTimeout(() => {
                    ambientRef.current?.stop();
                    ambientRef.current = null;
                }, 1000);
            }
            setCurrentAmbient(null);
            return;
        }

        // For simplicity, play first track (could layer multiple)
        const trackFile = `/assets/audio/ambient/${ambientData.tracks[0]}.mp3`;

        // Crossfade
        if (ambientRef.current) {
            ambientRef.current.fade(volumes.ambient, 0, 1000);
            setTimeout(() => ambientRef.current?.stop(), 1000);
        }

        // Create new ambient sound
        ambientRef.current = new Howl({
            src: [trackFile],
            loop: true,
            volume: 0,
            onload: function () {
                this.play();
                this.fade(0, volumes.ambient * ambientData.volume, 1000);
            },
            onloaderror: function (id, error) {
                console.warn(`Ambient audio failed to load: ${trackFile}`, error);
            }
        });

        setCurrentAmbient(ambientData.zone_type);
    };

    // Update music track
    const updateMusic = (musicData) => {
        if (!musicData || !musicData.filename) {
            // Stop music
            if (musicRef.current) {
                musicRef.current.fade(volumes.music, 0, 1000);
                setTimeout(() => {
                    musicRef.current?.stop();
                    musicRef.current = null;
                }, 1000);
            }
            setCurrentMusic(null);
            return;
        }

        const trackFile = `/assets/${musicData.filename}`;

        // Crossfade
        if (musicRef.current) {
            musicRef.current.fade(volumes.music, 0, 1000);
            setTimeout(() => musicRef.current?.stop(), 1000);
        }

        // Create new music sound
        musicRef.current = new Howl({
            src: [trackFile],
            loop: true,
            volume: 0,
            onload: function () {
                this.play();
                this.fade(0, volumes.music * (musicData.volume || 1.0), 1000);
            },
            onloaderror: function (id, error) {
                console.warn(`Music failed to load: ${trackFile}`, error);
            }
        });

        setCurrentMusic(musicData.track_id);
    };

    // Play voice/TTS
    const playVoice = (audioUrl) => {
        if (!audioEnabled) return;

        // Stop current voice if playing
        if (voiceRef.current) {
            voiceRef.current.stop();
        }

        voiceRef.current = new Howl({
            src: [audioUrl],
            volume: volumes.voice,
            onend: function () {
                voiceRef.current = null;
            },
            onloaderror: function (id, error) {
                console.warn(`Voice audio failed to load: ${audioUrl}`, error);
            }
        });

        voiceRef.current.play();
    };

    // Update volumes when they change
    useEffect(() => {
        if (ambientRef.current) {
            ambientRef.current.volume(volumes.ambient);
        }
        if (musicRef.current) {
            musicRef.current.volume(volumes.music);
        }
        if (voiceRef.current) {
            voiceRef.current.volume(volumes.voice);
        }
    }, [volumes]);

    // Poll for audio state changes
    useEffect(() => {
        if (!audioEnabled) return;

        // Initial fetch
        fetchAudioState();

        // Poll every 5 seconds
        pollIntervalRef.current = setInterval(fetchAudioState, 5000);

        return () => {
            if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
            }
        };
    }, [sessionId, audioEnabled, currentAmbient, currentMusic]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            ambientRef.current?.stop();
            musicRef.current?.stop();
            voiceRef.current?.stop();
            Object.values(sfxRefs.current).forEach(s => s.stop());
        };
    }, []);

    // Expose playVoice and playSFX globally for other components
    useEffect(() => {
        window.playVoice = playVoice;
        window.playSFX = playSFX;
        return () => {
            delete window.playVoice;
            delete window.playSFX;
        };
    }, [playVoice, playSFX]);

    // This component doesn't render anything
    return null;
};

export default AudioManager;
