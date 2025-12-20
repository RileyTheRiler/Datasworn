import React, { createContext, useContext, useState, useEffect } from 'react';

const AudioContext = createContext();

export const useAudio = () => {
    const context = useContext(AudioContext);
    if (!context) {
        throw new Error('useAudio must be used within AudioProvider');
    }
    return context;
};

export const AudioProvider = ({ children }) => {
    const [volumes, setVolumes] = useState({
        ambient: 0.5,
        music: 0.6,
        voice: 0.8,
        master: 1.0
    });

    const [muted, setMuted] = useState(false);
    const [audioEnabled, setAudioEnabled] = useState(true);

    const setVolume = (channel, value) => {
        setVolumes(prev => ({
            ...prev,
            [channel]: Math.max(0, Math.min(1, value))
        }));
    };

    const toggleMute = () => {
        setMuted(prev => !prev);
    };

    const toggleAudio = () => {
        setAudioEnabled(prev => !prev);
    };

    const value = {
        volumes,
        setVolume,
        muted,
        toggleMute,
        audioEnabled,
        toggleAudio
    };

    return (
        <AudioContext.Provider value={value}>
            {children}
        </AudioContext.Provider>
    );
};
