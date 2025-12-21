import React, { useState } from 'react';
import { useMusic } from '../contexts/MusicContext';

const MusicPlayer = () => {
    const {
        isPlaying,
        currentMood,
        volume,
        togglePlay,
        skipTrack,
        setVolume,
        playMood
    } = useMusic();

    const [isExpanded, setIsExpanded] = useState(false);

    const getMoodColor = (mood) => {
        switch (mood) {
            case 'relaxing': return 'text-disco-cyan';
            case 'tense': return 'text-disco-purple';
            case 'dramatic': return 'text-disco-yellow';
            case 'intense': return 'text-disco-red';
            default: return 'text-disco-muted';
        }
    };

    const moodColor = getMoodColor(currentMood);

    return (
        <div className={`relative flex items-center transition-all duration-300 ${isExpanded ? 'bg-black/80 pr-4 rounded-full border border-disco-muted/30' : ''}`}>
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className={`flex items-center gap-2 px-3 py-1 hover:text-disco-paper transition-colors ${moodColor}`}
                title="Music Player"
            >
                <span className={`text-lg ${isPlaying ? 'animate-pulse' : ''}`}>
                    {isPlaying ? '🎵' : '🔇'}
                </span>
                {!isExpanded && (
                    <span className="text-xs font-mono uppercase tracking-wider opacity-70">
                        {currentMood}
                    </span>
                )}
            </button>

            {isExpanded && (
                <div className="flex items-center gap-4 ml-2 animate-slide-in-right">
                    <div className="flex gap-1">
                        {['relaxing', 'tense', 'dramatic', 'intense'].map(m => (
                            <button
                                key={m}
                                onClick={() => playMood(m)}
                                className={`w-2 h-2 rounded-full transition-all ${currentMood === m ? getMoodColor(m) + ' scale-125 shadow-glow' : 'bg-disco-muted/30 hover:bg-disco-paper'}`}
                                title={`Switch to ${m}`}
                            />
                        ))}
                    </div>

                    <button
                        onClick={togglePlay}
                        className="text-disco-paper hover:text-disco-accent transition-colors"
                    >
                        {isPlaying ? 'I I' : '▶'}
                    </button>

                    <button
                        onClick={skipTrack}
                        className="text-disco-paper hover:text-disco-accent transition-colors text-sm"
                        title="Skip Track"
                    >
                        ⏭
                    </button>

                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={volume}
                        onChange={(e) => setVolume(parseFloat(e.target.value))}
                        className="w-16 h-1 bg-disco-muted/30 rounded-lg appearance-none cursor-pointer accent-disco-cyan"
                    />
                </div>
            )}
        </div>
    );
};

export default MusicPlayer;
