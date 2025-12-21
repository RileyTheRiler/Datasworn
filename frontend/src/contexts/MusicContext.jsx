import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { Howl } from 'howler';

const MusicContext = createContext(null);

export const useMusic = () => {
    const context = useContext(MusicContext);
    if (!context) {
        throw new Error('useMusic must be used within MusicProvider');
    }
    return context;
};

const API_URL = 'http://localhost:8001/api';

export const MusicProvider = ({ children }) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentMood, setCurrentMood] = useState('relaxing');
    const [playlist, setPlaylist] = useState({
        relaxing: [],
        tense: [],
        dramatic: [],
        intense: []
    });
    const [currentTrack, setCurrentTrack] = useState(null);
    const [volume, setVolume] = useState(() => {
        const saved = localStorage.getItem('musicVolume');
        return saved ? parseFloat(saved) : 0.3;
    });

    const soundRef = useRef(null);
    const playedTracksRef = useRef({
        relaxing: new Set(),
        tense: new Set(),
        dramatic: new Set(),
        intense: new Set()
    });

    // Fetch manifest on mount
    useEffect(() => {
        fetch(`${API_URL}/music/manifest`)
            .then(res => res.json())
            .then(data => {
                setPlaylist(data);
            })
            .catch(err => console.error("Failed to load music manifest:", err));
    }, []);

    // Save volume
    useEffect(() => {
        localStorage.setItem('musicVolume', volume.toString());
        if (soundRef.current) {
            soundRef.current.volume(volume);
        }
    }, [volume]);

    const playMood = (mood) => {
        if (!playlist[mood] || playlist[mood].length === 0) {
            console.warn(`No music found for mood: ${mood}`);
            return;
        }

        if (currentMood !== mood) {
            setCurrentMood(mood);
            if (isPlaying) {
                stopMusic();
                playNextTrack(mood);
            }
        } else {
            if (!isPlaying) {
                playNextTrack(mood);
            }
        }
    };

    const playNextTrack = (mood = currentMood) => {
        const tracks = playlist[mood];
        if (!tracks || tracks.length === 0) return;

        let available = tracks.filter(t => !playedTracksRef.current[mood].has(t));
        if (available.length === 0) {
            playedTracksRef.current[mood].clear();
            available = tracks;
        }

        const nextTrack = available[Math.floor(Math.random() * available.length)];
        playedTracksRef.current[mood].add(nextTrack);

        playTrack(nextTrack);
    };

    const playTrack = (src) => {
        if (soundRef.current) {
            soundRef.current.unload();
        }

        const fullSrc = src.startsWith('http') ? src : `http://localhost:8001${src}`;

        const sound = new Howl({
            src: [fullSrc],
            html5: true,
            volume: volume,
            onend: () => {
                playNextTrack(currentMood);
            },
            onloaderror: (id, err) => {
                console.error("Music load error:", err);
                setTimeout(() => playNextTrack(currentMood), 1000);
            }
        });

        soundRef.current = sound;
        setCurrentTrack(src);
        sound.play();
        setIsPlaying(true);
    };

    const stopMusic = () => {
        if (soundRef.current) {
            soundRef.current.fade(volume, 0, 1000);
            setTimeout(() => {
                soundRef.current.stop();
                setIsPlaying(false);
            }, 1000);
        } else {
            setIsPlaying(false);
        }
    };

    const pauseMusic = () => {
        if (soundRef.current) {
            soundRef.current.pause();
            setIsPlaying(false);
        }
    };

    const resumeMusic = () => {
        if (soundRef.current) {
            soundRef.current.play();
            soundRef.current.fade(0, volume, 500);
            setIsPlaying(true);
        } else {
            playNextTrack(currentMood);
        }
    };

    const skipTrack = () => {
        if (soundRef.current) {
            soundRef.current.stop();
        }
        playNextTrack(currentMood);
    };

    const togglePlay = () => {
        if (isPlaying) {
            pauseMusic();
        } else {
            resumeMusic();
        }
    };

    const value = {
        isPlaying,
        currentMood,
        currentTrack,
        volume,
        playlist,
        playMood,
        togglePlay,
        setVolume,
        skipTrack
    };

    return (
        <MusicContext.Provider value={value}>
            {children}
        </MusicContext.Provider>
    );
};

export default MusicProvider;
