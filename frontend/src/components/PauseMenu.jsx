import React, { useState } from 'react';
import DraggableModal from './DraggableModal';
import SaveManager from './SaveManager';

const API_URL = 'http://localhost:8000/api';

const PauseMenu = ({ isOpen, onClose, onResume, sessionId = 'default' }) => {
    const [showSaveManager, setShowSaveManager] = useState(false);
    const [saveStatus, setSaveStatus] = useState('');

    const handleQuickSave = async () => {
        try {
            const response = await fetch(`${API_URL}/save/quicksave`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (response.ok) {
                setSaveStatus('✓ Game Saved');
                setTimeout(() => setSaveStatus(''), 2000);
            } else {
                setSaveStatus('✗ Save Failed');
                setTimeout(() => setSaveStatus(''), 2000);
            }
        } catch (error) {
            console.error('Save error:', error);
            setSaveStatus('✗ Save Failed');
            setTimeout(() => setSaveStatus(''), 2000);
        }
    };

    const handleExit = async () => {
        if (confirm('Exit game and stop all servers?')) {
            try {
                await fetch(`${API_URL}/shutdown`, { method: 'POST' });
            } catch (e) {
                console.log('Server already stopped');
            }
            window.close();
        }
    };

    if (!isOpen) return null;

    return (
        <>
            <DraggableModal
                isOpen={isOpen && !showSaveManager}
                onClose={onClose}
                title="⏸ GAME PAUSED"
                defaultWidth={500}
                defaultHeight={600}
                className="bg-disco-bg"
            >
                <div className="flex flex-col h-full p-8 space-y-6">
                    {/* Status Message */}
                    {saveStatus && (
                        <div className={`text-center font-mono text-sm p-2 border ${saveStatus.includes('✓')
                                ? 'text-disco-green border-disco-green/30 bg-disco-green/10'
                                : 'text-disco-red border-disco-red/30 bg-disco-red/10'
                            }`}>
                            {saveStatus}
                        </div>
                    )}

                    {/* Menu Buttons */}
                    <div className="flex-1 flex flex-col justify-center space-y-4">
                        <MenuButton onClick={onResume}>
                            ▶️ Resume Game
                        </MenuButton>

                        <MenuButton onClick={handleQuickSave}>
                            💾 Quick Save
                        </MenuButton>

                        <MenuButton onClick={() => setShowSaveManager(true)}>
                            📁 Save/Load Manager
                        </MenuButton>

                        <div className="h-px bg-disco-muted/30 my-2"></div>

                        <MenuButton onClick={handleExit} variant="danger">
                            🚪 Exit to Desktop
                        </MenuButton>
                    </div>

                    {/* Keyboard Hint */}
                    <div className="text-center text-xs font-mono text-disco-muted/50">
                        Press <kbd className="px-2 py-1 bg-disco-dark/50 border border-disco-muted/30 rounded">ESC</kbd> to resume
                    </div>
                </div>
            </DraggableModal>

            {/* Save Manager Modal */}
            <SaveManager
                isOpen={showSaveManager}
                onClose={() => setShowSaveManager(false)}
                sessionId={sessionId}
            />
        </>
    );
};

const MenuButton = ({ children, onClick, variant = 'default' }) => {
    const baseStyles = "w-full px-6 py-4 font-serif text-lg tracking-wide transition-all duration-300 border focus:outline-none group";

    const variants = {
        default: "border-disco-muted/30 text-disco-paper hover:border-disco-cyan hover:text-disco-cyan hover:bg-disco-cyan/10 hover:shadow-[0_0_15px_rgba(34,211,238,0.2)]",
        danger: "border-disco-muted/30 text-disco-muted hover:border-disco-red hover:text-disco-red hover:bg-disco-red/10"
    };

    return (
        <button
            onClick={onClick}
            className={`${baseStyles} ${variants[variant]}`}
        >
            {children}
        </button>
    );
};

export default PauseMenu;
