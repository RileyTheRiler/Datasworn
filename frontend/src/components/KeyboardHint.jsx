import React, { useState, useEffect } from 'react';

/**
 * KeyboardHint - Persistent hint to remind users about keyboard shortcuts
 *
 * Features:
 * - Appears on first load with animation
 * - Can be dismissed
 * - Reappears occasionally as a subtle reminder
 * - Positioned to not interfere with gameplay
 */
const KeyboardHint = ({ onShowHelp }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [isDismissed, setIsDismissed] = useState(false);
    const [isAnimating, setIsAnimating] = useState(false);

    useEffect(() => {
        // Check if user has seen the hint before
        const hasSeenHint = localStorage.getItem('keyboard_hint_seen');

        if (!hasSeenHint) {
            // First time - show animated hint after 3 seconds
            const timer = setTimeout(() => {
                setIsVisible(true);
                setIsAnimating(true);
                localStorage.setItem('keyboard_hint_seen', 'true');

                // Stop animation after 5 seconds
                setTimeout(() => setIsAnimating(false), 5000);
            }, 3000);

            return () => clearTimeout(timer);
        } else {
            // Returning user - show subtle, non-animated hint
            setIsVisible(true);
        }
    }, []);

    const handleDismiss = () => {
        setIsDismissed(true);
        setIsVisible(false);
    };

    const handleClick = () => {
        onShowHelp?.();
    };

    if (isDismissed || !isVisible) return null;

    return (
        <div
            className={`fixed bottom-4 right-4 z-[90] transition-all duration-300 ${
                isAnimating ? 'animate-bounce' : ''
            }`}
        >
            <div className="relative group">
                {/* Main hint button */}
                <button
                    onClick={handleClick}
                    className={`
                        px-4 py-2
                        bg-disco-cyan/10 hover:bg-disco-cyan/20
                        border-2 border-disco-cyan/50 hover:border-disco-cyan
                        text-disco-cyan
                        rounded-lg
                        font-mono text-sm
                        transition-all duration-200
                        shadow-lg hover:shadow-glow
                        flex items-center gap-2
                        ${isAnimating ? 'ring-2 ring-disco-cyan/50 ring-offset-2 ring-offset-disco-bg' : ''}
                    `}
                    title="Show keyboard shortcuts"
                >
                    <span className="text-lg">⌨️</span>
                    <span>Press <kbd className="px-1.5 py-0.5 bg-disco-bg border border-disco-cyan/50 rounded text-xs">?</kbd> for help</span>
                </button>

                {/* Dismiss button - appears on hover */}
                <button
                    onClick={handleDismiss}
                    className="absolute -top-2 -right-2 w-5 h-5 bg-disco-red/80 hover:bg-disco-red border border-disco-red rounded-full text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Dismiss hint"
                >
                    ×
                </button>

                {/* Pulsing indicator for animation phase */}
                {isAnimating && (
                    <div className="absolute -inset-2 rounded-lg border-2 border-disco-cyan/30 animate-ping pointer-events-none" />
                )}
            </div>
        </div>
    );
};

export default KeyboardHint;
