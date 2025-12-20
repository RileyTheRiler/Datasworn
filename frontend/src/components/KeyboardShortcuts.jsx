import { useEffect, useCallback } from 'react';

/**
 * KeyboardController - Global keyboard shortcuts for power users
 *
 * Shortcuts:
 * - R: Quick roll (opens skill check)
 * - M: Toggle mute (soundscape)
 * - S: Open save manager
 * - C: Toggle character sheet
 * - P: Toggle psyche dashboard
 * - T: Toggle session timer
 * - H: Toggle high contrast mode
 * - Escape: Close any modal
 * - Space: Skip typewriter animation (handled in TypewriterText)
 * - ?: Show keyboard shortcuts help
 * - 1-5: Quick stat selection for rolls
 */

export const useKeyboardShortcuts = ({
    onToggleRoll,
    onToggleMute,
    onCloseModal,
    onShowHelp,
    onToggleSaves,
    onToggleCharacter,
    onTogglePsyche,
    onToggleTimer,
    onToggleHighContrast,
    onSelectStat,
}) => {
    const handleKeyDown = useCallback((e) => {
        // Don't trigger shortcuts when typing in input fields
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        switch (e.key.toLowerCase()) {
            case 'r':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    onToggleRoll?.();
                }
                break;

            case 'm':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    onToggleMute?.();
                }
                break;

            case 's':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    onToggleSaves?.();
                }
                break;

            case 'c':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    onToggleCharacter?.();
                }
                break;

            case 'p':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    onTogglePsyche?.();
                }
                break;

            case 't':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    onToggleTimer?.();
                }
                break;

            case 'h':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    onToggleHighContrast?.();
                }
                break;

            case 'escape':
                onCloseModal?.();
                break;

            case '?':
                e.preventDefault();
                onShowHelp?.();
                break;

            // Quick stat selection (1-5 for Edge, Heart, Iron, Shadow, Wits)
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    const statMap = { '1': 'edge', '2': 'heart', '3': 'iron', '4': 'shadow', '5': 'wits' };
                    onSelectStat?.(statMap[e.key]);
                }
                break;

            default:
                break;
        }
    }, [onToggleRoll, onToggleMute, onCloseModal, onShowHelp, onToggleSaves, onToggleCharacter, onTogglePsyche, onToggleTimer, onToggleHighContrast, onSelectStat]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);
};

/**
 * KeyboardHelpOverlay - Shows available keyboard shortcuts
 */
export const KeyboardHelpOverlay = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    const shortcuts = [
        { key: 'R', description: 'Open dice roll' },
        { key: 'M', description: 'Toggle soundscape' },
        { key: 'S', description: 'Open save manager' },
        { key: 'C', description: 'Toggle character sheet' },
        { key: 'P', description: 'Toggle psyche dashboard' },
        { key: 'T', description: 'Toggle session timer' },
        { key: 'H', description: 'Toggle high contrast' },
        { key: '1-5', description: 'Select stat (Edge/Heart/Iron/Shadow/Wits)' },
        { key: 'F5', description: 'Quick save' },
        { key: 'F9', description: 'Quick load' },
        { key: 'Esc', description: 'Close dialog' },
        { key: 'Space', description: 'Skip text animation' },
        { key: '?', description: 'Show this help' },
        { key: 'Enter', description: 'Submit action' },
    ];

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm"
            onClick={onClose}
        >
            <div
                className="bg-disco-panel border-2 border-disco-muted p-8 rounded-lg max-w-md w-full mx-4 shadow-2xl"
                onClick={e => e.stopPropagation()}
            >
                <h2 className="font-serif text-2xl text-disco-paper mb-6 text-center uppercase tracking-widest">
                    Keyboard Shortcuts
                </h2>

                <div className="space-y-3">
                    {shortcuts.map(({ key, description }) => (
                        <div key={key} className="flex justify-between items-center">
                            <span className="text-disco-paper/80 font-serif">{description}</span>
                            <kbd className="px-3 py-1 bg-disco-dark border border-disco-muted rounded text-disco-cyan font-mono text-sm">
                                {key}
                            </kbd>
                        </div>
                    ))}
                </div>

                <div className="mt-8 text-center">
                    <button
                        onClick={onClose}
                        className="btn-disco px-6 py-2"
                    >
                        Close
                    </button>
                </div>

                <div className="mt-4 text-center text-[10px] text-disco-muted uppercase">
                    Press ESC or click outside to close
                </div>
            </div>
        </div>
    );
};

export default {
    useKeyboardShortcuts,
    KeyboardHelpOverlay,
};
