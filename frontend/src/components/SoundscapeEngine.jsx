import React, { useEffect, useRef, useState } from 'react';
import { Howl } from 'howler';

// Sound files are expected in public/sounds/
const SOUNDS = {
    ambient: '/sounds/ship_ambient.mp3',
    heartbeat: '/sounds/heartbeat.mp3',
    whisper: '/sounds/whisper.mp3',
    alarm: '/sounds/alarm.mp3',
    static: '/sounds/static.mp3',
};

const SoundscapeEngine = () => {
    const [enabled, setEnabled] = useState(false);
    const [psycheData, setPsycheData] = useState(null);
    const soundsRef = useRef({});
    const ambientRef = useRef(null);

    // Initialize sounds
    useEffect(() => {
        soundsRef.current = {
            heartbeat: new Howl({ src: [SOUNDS.heartbeat], loop: true, volume: 0 }),
            whisper: new Howl({ src: [SOUNDS.whisper], loop: false, volume: 0.3 }),
            alarm: new Howl({ src: [SOUNDS.alarm], loop: false, volume: 0.5 }),
            static: new Howl({ src: [SOUNDS.static], loop: true, volume: 0 }),
        };

        ambientRef.current = new Howl({
            src: [SOUNDS.ambient],
            loop: true,
            volume: 0.2,
        });

        return () => {
            // Cleanup
            Object.values(soundsRef.current).forEach(s => s.unload());
            ambientRef.current?.unload();
        };
    }, []);

    // Poll psyche data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/psyche/default');
                if (res.ok) {
                    const json = await res.json();
                    setPsycheData(json);
                }
            } catch (err) {
                // Silently fail
            }
        };

        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    // React to psyche changes
    useEffect(() => {
        if (!enabled || !psycheData) return;

        const profile = psycheData.profile || {};
        const stress = profile.stress_level || 0;
        const sanity = profile.sanity !== undefined ? profile.sanity : 1.0;

        // Heartbeat intensifies with stress
        if (stress > 0.7) {
            const volume = (stress - 0.7) / 0.3 * 0.8; // 0-0.8
            soundsRef.current.heartbeat.volume(volume);
            if (!soundsRef.current.heartbeat.playing()) {
                soundsRef.current.heartbeat.play();
            }
        } else {
            soundsRef.current.heartbeat.fade(soundsRef.current.heartbeat.volume(), 0, 1000);
        }

        // Whispers at low sanity
        if (sanity < 0.3 && !soundsRef.current.whisper.playing()) {
            soundsRef.current.whisper.play();
        }

        // Static increases with very low sanity
        if (sanity < 0.15) {
            const staticVol = (0.15 - sanity) / 0.15 * 0.5;
            soundsRef.current.static.volume(staticVol);
            if (!soundsRef.current.static.playing()) {
                soundsRef.current.static.play();
            }
        } else {
            soundsRef.current.static.fade(soundsRef.current.static.volume(), 0, 500);
        }

    }, [psycheData, enabled]);

    // Toggle handler
    const toggleAudio = () => {
        if (enabled) {
            ambientRef.current?.pause();
            Object.values(soundsRef.current).forEach(s => s.pause());
        } else {
            ambientRef.current?.play();
        }
        setEnabled(!enabled);
    };

    return (
        <button
            onClick={toggleAudio}
            className={`fixed bottom-4 left-4 p-3 rounded-full border transition-all ${enabled ? 'bg-cyan-900/80 border-cyan-500 text-cyan-300' : 'bg-slate-900/80 border-slate-700 text-slate-500'}`}
            title={enabled ? 'Mute Soundscape' : 'Enable Soundscape'}
        >
            {enabled ? '🔊' : '🔇'}
        </button>
    );
};

export default SoundscapeEngine;
