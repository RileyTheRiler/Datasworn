import React, { useState } from 'react';
import { useMusic } from '../contexts/MusicContext';
import { useSoundEffects } from '../contexts/SoundEffectsContext';
import SaveManager from './SaveManager';
import SoundSettings from './SoundSettings';
import { AmbientParticles, Starfield } from './UXEffects';

const MainMenu = ({ onNewGame, onLoadGame, onExit }) => {
    const { playMood } = useMusic();
    const [showSaveManager, setShowSaveManager] = useState(false);
    const [showSettings, setShowSettings] = useState(false);

    // Initial music start
    React.useEffect(() => {
        playMood('theme');
    }, [playMood]);

    const handleLoadGame = (state) => {
        onLoadGame(state);
    };

    return (
        <div className="relative h-screen w-full bg-black overflow-hidden flex flex-col items-center justify-center font-sans text-disco-paper selection:bg-disco-cyan selection:text-black">

            {/* Background Effects */}
            <Starfield count={200} speed={0.5} />
            <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/60 pointer-events-none z-10"></div>

            {/* Holographic Wireframe Schematic */}
            <div className="absolute inset-0 z-0 flex items-center justify-center pointer-events-none opacity-20 mix-blend-screen overflow-hidden">
                <img
                    src="/backgrounds/ship-schematic.jpg"
                    alt="Ship Schematic"
                    className="w-full h-full object-cover scale-110"
                />
            </div>

            {/* Vignette Overlay */}
            <div className="absolute inset-0 z-10 bg-[radial-gradient(circle_at_center,transparent_30%,rgba(0,0,0,0.8)_95%)] pointer-events-none"></div>

            {/* Main Content Container */}
            <div className="z-10 flex flex-col items-center gap-16 animate-fade-in-up">

                {/* Title Section */}
                <div className="text-center space-y-6 relative">
                    <h1 className="text-8xl font-serif tracking-[0.2em] text-transparent bg-clip-text bg-gradient-to-b from-disco-paper via-gray-300 to-gray-500 drop-shadow-[0_0_35px_rgba(255,255,255,0.6)] animate-text-scanline relative z-10">
                        IN WHAT DISTANT DEEPS OR SKIES
                    </h1>

                    {/* Horizon Line with Bloom */}
                    <div className="absolute left-1/2 -bottom-2 -translate-x-1/2 w-[120%] h-px bg-disco-cyan shadow-[0_0_15px_rgba(107,228,227,0.8)] opacity-80"></div>
                </div>

                {/* Sub-title System Text */}
                <div className="font-mono text-sm tracking-[0.3em] text-disco-muted/80 animate-pulse">
                    [ SYSTEM READY // AWAITING INPUT ]
                </div>

                {/* Menu Buttons */}
                <div className="flex flex-col gap-6 w-80">
                    <MenuButton onClick={onNewGame} variant="primary">
                        NEW GAME
                    </MenuButton>

                    <MenuButton onClick={() => setShowSaveManager(true)}>
                        LOAD GAME
                    </MenuButton>

                    <MenuButton onClick={() => setShowSettings(true)}>
                        SETTINGS
                    </MenuButton>

                    <MenuButton onClick={onExit} variant="danger">
                        EXIT
                    </MenuButton>
                </div>
            </div>

            {/* Footer / Music Controls */}
            <div className="absolute bottom-8 right-8 z-20 font-mono text-disco-cyan/80 text-sm tracking-widest flex items-center gap-4">
                <MusicControls />
            </div>

            {/* Version Info & Protocol Header */}
            <div className="absolute bottom-6 left-8 text-xs font-mono text-disco-muted/60 tracking-widest digital-flicker">
                <div>v0.9.1-alpha // PROTOCOL: GEMINI</div>
                <div className="text-[10px] opacity-50 mt-1">SYS.READY // AWAITING INPUT</div>
            </div>

            {/* Modals */}
            <SaveManager
                isOpen={showSaveManager}
                onClose={() => setShowSaveManager(false)}
                onLoadComplete={handleLoadGame}
                sessionId={null}
            />

            <SoundSettings
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
            />

        </div>
    );
};

const MusicControls = () => {
    const { isPaused, isMuted, togglePause, toggleMute } = useMusic();

    return (
        <div className="flex items-center gap-3">
            <span className="opacity-60 text-xs">[ AUDIO ]</span>

            <button
                onClick={togglePause}
                className="group relative px-3 py-1.5 border border-disco-cyan/40 bg-disco-cyan/5 hover:bg-disco-cyan/10 transition-all duration-200 hover:border-disco-cyan/80"
                title={isPaused ? "Play Music" : "Pause Music"}
            >
                <span className="text-disco-cyan text-xs font-bold">
                    {isPaused ? '▶' : '❚❚'}
                </span>
            </button>

            <button
                onClick={toggleMute}
                className="group relative px-3 py-1.5 border border-disco-cyan/40 bg-disco-cyan/5 hover:bg-disco-cyan/10 transition-all duration-200 hover:border-disco-cyan/80"
                title={isMuted ? "Unmute" : "Mute"}
            >
                <span className="text-disco-cyan text-xs font-bold">
                    {isMuted ? '🔇' : '🔊'}
                </span>
            </button>

            <span className="w-2 h-4 bg-disco-cyan animate-pulse block shadow-[0_0_8px_rgba(107,228,227,0.8)] opacity-60"></span>
        </div>
    );
};

const MenuButton = ({ children, onClick, variant = 'default' }) => {
    const { playRandomGlitch } = useSoundEffects();

    const isDanger = variant === 'danger';
    const borderColor = isDanger ? 'border-disco-red' : 'border-disco-cyan';
    const textColor = isDanger ? 'text-disco-red' : 'text-disco-cyan';
    const glowShadow = isDanger
        ? 'shadow-[0_0_10px_rgba(239,68,68,0.3),inset_0_0_5px_rgba(239,68,68,0.1)] group-hover:shadow-[0_0_25px_rgba(239,68,68,0.6),inset_0_0_15px_rgba(239,68,68,0.3)]'
        : 'shadow-[0_0_10px_rgba(107,228,227,0.3),inset_0_0_5px_rgba(107,228,227,0.1)] group-hover:shadow-[0_0_25px_rgba(107,228,227,0.6),inset_0_0_15px_rgba(107,228,227,0.3)]';

    return (
        <button
            onClick={onClick}
            onMouseEnter={() => playRandomGlitch && playRandomGlitch()}
            className={`group relative px-8 py-5 font-serif text-xl tracking-[0.2em] transition-all duration-300 focus:outline-none hover:scale-105 active:scale-95 w-full flex items-center justify-center border-2 ${borderColor} ${textColor} ${glowShadow} bg-black/80 overflow-hidden`}
        >
            {/* Internal Scanline Texture */}
            <div className="absolute inset-0 bg-scanline-btn opacity-30 pointer-events-none"></div>

            {/* 3D Bevel Highlight (Top/Left) */}
            <div className="absolute inset-0 border-t border-l border-white/10 opacity-50 pointer-events-none"></div>
            {/* 3D Bevel Shadow (Bottom/Right) */}
            <div className="absolute inset-0 border-b border-r border-black/50 opacity-50 pointer-events-none"></div>

            {/* Content */}
            <span className="relative z-10 font-bold drop-shadow-[0_0_8px_rgba(0,0,0,0.8)]">
                {children}
            </span>

            {/* Hover Highlight Overlay */}
            <div className={`absolute inset-0 bg-${isDanger ? 'disco-red' : 'disco-cyan'}/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300`}></div>

            {/* Technical Corner Accents */}
            <div className={`absolute top-0 left-0 w-1 h-1 ${isDanger ? 'bg-disco-red' : 'bg-disco-cyan'} opacity-60`}></div>
            <div className={`absolute top-0 right-0 w-1 h-1 ${isDanger ? 'bg-disco-red' : 'bg-disco-cyan'} opacity-60`}></div>
            <div className={`absolute bottom-0 left-0 w-1 h-1 ${isDanger ? 'bg-disco-red' : 'bg-disco-cyan'} opacity-60`}></div>
            <div className={`absolute bottom-0 right-0 w-1 h-1 ${isDanger ? 'bg-disco-red' : 'bg-disco-cyan'} opacity-60`}></div>
        </button>
    );
};

export default MainMenu;
