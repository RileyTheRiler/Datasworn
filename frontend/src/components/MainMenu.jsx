import React, { useState } from 'react';
import { useMusic } from '../contexts/MusicContext';
import MusicPlayer from './MusicPlayer';
import SaveManager from './SaveManager';
import SoundSettings from './SoundSettings';
import { AmbientParticles } from './UXEffects';

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
        <div className="relative h-screen w-full bg-disco-bg overflow-hidden flex flex-col items-center justify-center font-sans text-disco-paper selection:bg-disco-cyan selection:text-black">

            {/* Background Effects */}
            <div className="absolute inset-0 bg-grunge opacity-20 pointer-events-none mix-blend-overlay"></div>
            <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/80 pointer-events-none"></div>
            <AmbientParticles type="dust" count={30} />

            {/* Main Content Container */}
            <div className="z-10 flex flex-col items-center gap-12 animate-fade-in-up">

                {/* Title Section */}
                <div className="text-center space-y-4">
                    <h1 className="text-8xl font-serif tracking-widest text-transparent bg-clip-text bg-gradient-to-b from-disco-paper via-gray-400 to-gray-600 drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]">
                        IN WHAT DISTANT DEEPS OR SKIES
                    </h1>
                    <div className="h-px w-full bg-gradient-to-r from-transparent via-disco-cyan/50 to-transparent"></div>
                </div>

                {/* Menu Buttons */}
                <div className="flex flex-col gap-4 w-64">
                    <MenuButton onClick={onNewGame}>
                        New Game
                    </MenuButton>

                    <MenuButton onClick={() => setShowSaveManager(true)}>
                        Load Game
                    </MenuButton>

                    <MenuButton onClick={() => setShowSettings(true)}>
                        Settings
                    </MenuButton>

                    <MenuButton onClick={onExit} variant="danger">
                        Exit
                    </MenuButton>
                </div>
            </div>

            {/* Footer / Music Player */}
            <div className="absolute bottom-8 right-8 z-20">
                <MusicPlayer />
            </div>

            {/* Version Info */}
            <div className="absolute bottom-4 left-4 text-xs font-mono text-disco-muted/40">
                v0.9.1-alpha // PROTOCOL: GEMINI
            </div>

            {/* Modals */}
            <SaveManager
                isOpen={showSaveManager}
                onClose={() => setShowSaveManager(false)}
                onLoadComplete={handleLoadGame}
                sessionId={null} // No session yet
            />

            <SoundSettings
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
            />

        </div>
    );
};

const MenuButton = ({ children, onClick, variant = 'default' }) => {
    const baseStyles = "relative px-8 py-3 font-serif text-xl tracking-wide transition-all duration-300 border focus:outline-none group overflow-hidden";

    const variants = {
        default: "border-disco-muted/30 text-disco-paper hover:border-disco-cyan hover:text-disco-cyan hover:bg-disco-cyan/5 hover:shadow-[0_0_15px_rgba(34,211,238,0.2)]",
        danger: "border-disco-muted/30 text-disco-muted hover:border-disco-red hover:text-disco-red hover:bg-disco-red/5"
    };

    return (
        <button
            onClick={onClick}
            className={`${baseStyles} ${variants[variant]}`}
        >
            <span className="relative z-10">{children}</span>
            {/* Tech Decoration */}
            <div className="absolute top-0 left-0 w-1 h-1 bg-current opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="absolute bottom-0 right-0 w-1 h-1 bg-current opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </button>
    );
};

export default MainMenu;
