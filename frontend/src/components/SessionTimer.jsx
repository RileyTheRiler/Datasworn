import React, { useState, useEffect, useCallback } from 'react';

/**
 * SessionTimer - Tracks and displays session duration
 *
 * Features:
 * - Real-time session duration tracking
 * - Minimizable display
 * - Session start time display
 * - Break reminders at configurable intervals
 */

const SessionTimer = ({ isVisible = true, onToggle, breakReminderInterval = 60 }) => {
    const [startTime] = useState(() => Date.now());
    const [elapsed, setElapsed] = useState(0);
    const [isMinimized, setIsMinimized] = useState(false);
    const [showBreakReminder, setShowBreakReminder] = useState(false);

    // Update elapsed time every second
    useEffect(() => {
        const interval = setInterval(() => {
            const newElapsed = Math.floor((Date.now() - startTime) / 1000);
            setElapsed(newElapsed);

            // Check for break reminder (default: every 60 minutes)
            if (breakReminderInterval > 0 && newElapsed > 0 && newElapsed % (breakReminderInterval * 60) === 0) {
                setShowBreakReminder(true);
                // Auto-dismiss after 10 seconds
                setTimeout(() => setShowBreakReminder(false), 10000);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [startTime, breakReminderInterval]);

    // Format time as HH:MM:SS
    const formatTime = useCallback((seconds) => {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hrs > 0) {
            return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }, []);

    // Format start time
    const formatStartTime = useCallback(() => {
        return new Date(startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }, [startTime]);

    if (!isVisible) return null;

    return (
        <>
            {/* Main Timer Display */}
            <div
                className={`
                    fixed top-4 left-4 z-50 transition-all duration-300
                    ${isMinimized ? 'w-auto' : 'w-48'}
                `}
            >
                <div className="bg-disco-panel/90 border border-disco-muted/30 rounded-lg shadow-lg backdrop-blur-sm overflow-hidden">
                    {/* Header */}
                    <div
                        className="flex items-center justify-between px-3 py-2 bg-disco-dark/50 cursor-pointer hover:bg-disco-dark/70 transition-colors"
                        onClick={() => setIsMinimized(!isMinimized)}
                    >
                        <div className="flex items-center gap-2">
                            <span className="text-disco-cyan text-sm">⏱</span>
                            <span className="font-mono text-disco-paper text-lg font-bold tracking-wider">
                                {formatTime(elapsed)}
                            </span>
                        </div>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onToggle?.();
                            }}
                            className="text-disco-muted hover:text-disco-paper text-xs transition-colors"
                            title="Hide timer"
                        >
                            ✕
                        </button>
                    </div>

                    {/* Expanded Details */}
                    {!isMinimized && (
                        <div className="px-3 py-2 space-y-1 border-t border-disco-muted/20">
                            <div className="flex justify-between text-xs font-mono">
                                <span className="text-disco-muted">Started</span>
                                <span className="text-disco-paper">{formatStartTime()}</span>
                            </div>
                            <div className="flex justify-between text-xs font-mono">
                                <span className="text-disco-muted">Session</span>
                                <span className="text-disco-cyan">Active</span>
                            </div>

                            {/* Progress bar for break reminder */}
                            {breakReminderInterval > 0 && (
                                <div className="mt-2">
                                    <div className="text-[10px] text-disco-muted uppercase mb-1">
                                        Next break in {formatTime((breakReminderInterval * 60) - (elapsed % (breakReminderInterval * 60)))}
                                    </div>
                                    <div className="h-1 bg-disco-dark rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-disco-accent transition-all duration-1000"
                                            style={{
                                                width: `${((elapsed % (breakReminderInterval * 60)) / (breakReminderInterval * 60)) * 100}%`
                                            }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Break Reminder Overlay */}
            {showBreakReminder && (
                <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="bg-disco-panel border-2 border-disco-accent p-8 rounded-lg max-w-md text-center shadow-2xl animate-pulse">
                        <div className="text-4xl mb-4">☕</div>
                        <h2 className="font-serif text-2xl text-disco-paper mb-2">
                            Time for a Break!
                        </h2>
                        <p className="text-disco-muted font-mono text-sm mb-4">
                            You've been playing for {formatTime(elapsed)}.
                            <br />
                            Consider stretching, hydrating, or resting your eyes.
                        </p>
                        <button
                            onClick={() => setShowBreakReminder(false)}
                            className="btn-disco px-6 py-2"
                        >
                            Continue Playing
                        </button>
                        <div className="mt-4 text-xs text-disco-muted">
                            Press any key or click to dismiss
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default SessionTimer;
