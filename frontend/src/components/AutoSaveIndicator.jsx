import React, { useState, useEffect } from 'react';

/**
 * AutoSaveIndicator - Visual feedback for auto-save status
 *
 * Features:
 * - Shows when auto-save is in progress
 * - Displays last save time
 * - Animated saving indicator
 * - Success/error feedback
 */

const AutoSaveIndicator = ({ sessionId = 'default', saveInterval = 60000 }) => {
    const [status, setStatus] = useState('idle'); // idle, saving, saved, error
    const [lastSave, setLastSave] = useState(null);
    const [isVisible, setIsVisible] = useState(false);

    // Poll for auto-save status
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/autosave/status/${sessionId}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.last_save) {
                        setLastSave(new Date(data.last_save));
                    }
                }
            } catch (err) {
                // Silently fail - offline mode
            }
        };

        checkStatus();
        const interval = setInterval(checkStatus, 30000); // Check every 30s
        return () => clearInterval(interval);
    }, [sessionId]);

    // Simulate auto-save trigger (in a real implementation, this would be triggered by the server)
    useEffect(() => {
        const triggerAutoSave = async () => {
            setStatus('saving');
            setIsVisible(true);

            try {
                const res = await fetch('http://localhost:8000/api/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        slot_name: 'autosave',
                        description: 'Auto-save'
                    })
                });

                if (res.ok) {
                    setStatus('saved');
                    setLastSave(new Date());

                    // Hide after 3 seconds
                    setTimeout(() => {
                        setIsVisible(false);
                        setStatus('idle');
                    }, 3000);
                } else {
                    setStatus('error');
                    setTimeout(() => {
                        setIsVisible(false);
                        setStatus('idle');
                    }, 5000);
                }
            } catch (err) {
                setStatus('error');
                setTimeout(() => {
                    setIsVisible(false);
                    setStatus('idle');
                }, 5000);
            }
        };

        // Auto-save at interval (default: every 60 seconds)
        const interval = setInterval(triggerAutoSave, saveInterval);
        return () => clearInterval(interval);
    }, [sessionId, saveInterval]);

    // Format relative time
    const getRelativeTime = () => {
        if (!lastSave) return 'Never';

        const diff = Date.now() - lastSave.getTime();
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);

        if (seconds < 60) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        return lastSave.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div
            className={`
                fixed bottom-4 right-4 z-50 transition-all duration-300
                ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'}
            `}
        >
            <div className={`
                flex items-center gap-2 px-4 py-2 rounded-lg shadow-lg backdrop-blur-sm
                ${status === 'saving' ? 'bg-disco-accent/20 border border-disco-accent' : ''}
                ${status === 'saved' ? 'bg-disco-cyan/20 border border-disco-cyan' : ''}
                ${status === 'error' ? 'bg-disco-red/20 border border-disco-red' : ''}
                ${status === 'idle' ? 'bg-disco-panel/80 border border-disco-muted/30' : ''}
            `}>
                {/* Status Icon */}
                <div className="text-lg">
                    {status === 'saving' && (
                        <div className="animate-spin">⟳</div>
                    )}
                    {status === 'saved' && (
                        <span className="text-disco-cyan">✓</span>
                    )}
                    {status === 'error' && (
                        <span className="text-disco-red">✕</span>
                    )}
                </div>

                {/* Status Text */}
                <div className="text-sm font-mono">
                    {status === 'saving' && (
                        <span className="text-disco-accent">Saving...</span>
                    )}
                    {status === 'saved' && (
                        <span className="text-disco-cyan">Saved</span>
                    )}
                    {status === 'error' && (
                        <span className="text-disco-red">Save failed</span>
                    )}
                </div>
            </div>
        </div>
    );
};

/**
 * Compact version for status bar
 */
export const AutoSaveStatus = ({ lastSave }) => {
    const getRelativeTime = () => {
        if (!lastSave) return 'Never';

        const diff = Date.now() - new Date(lastSave).getTime();
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);

        if (seconds < 60) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        return new Date(lastSave).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="flex items-center gap-1 text-xs font-mono text-disco-muted">
            <span>💾</span>
            <span>Saved: {getRelativeTime()}</span>
        </div>
    );
};

export default AutoSaveIndicator;
