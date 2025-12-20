import React, { createContext, useContext, useState, useCallback } from 'react';

/**
 * ToastProvider - Non-intrusive notification system
 * 
 * Usage:
 * const { addToast } = useToast();
 * addToast({ message: 'Momentum +2!', type: 'success' });
 */

const ToastContext = createContext(null);

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
};

const Toast = ({ id, message, type, subtext, onDismiss }) => {
    const typeStyles = {
        success: 'border-disco-cyan bg-disco-cyan/10 text-disco-cyan',
        warning: 'border-disco-yellow bg-disco-yellow/10 text-disco-yellow',
        danger: 'border-disco-red bg-disco-red/10 text-disco-red',
        info: 'border-disco-purple bg-disco-purple/10 text-disco-purple',
        narrative: 'border-disco-paper/50 bg-disco-panel text-disco-paper',
    };

    const icons = {
        success: '✦',
        warning: '⚠',
        danger: '✕',
        info: '◈',
        narrative: '❧',
    };

    return (
        <div
            className={`
                flex items-start gap-3 px-4 py-3 rounded border backdrop-blur-sm
                animate-slideIn shadow-lg max-w-sm
                ${typeStyles[type] || typeStyles.info}
            `}
            onClick={() => onDismiss(id)}
        >
            <span className="text-lg mt-0.5">{icons[type] || icons.info}</span>
            <div className="flex-1">
                <div className="font-serif text-sm">{message}</div>
                {subtext && (
                    <div className="font-mono text-xs opacity-70 mt-1">{subtext}</div>
                )}
            </div>
        </div>
    );
};

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const addToast = useCallback(({ message, type = 'info', subtext = '', duration = 4000 }) => {
        const id = Date.now() + Math.random();

        setToasts(prev => [...prev, { id, message, type, subtext }]);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                setToasts(prev => prev.filter(t => t.id !== id));
            }, duration);
        }

        return id;
    }, []);

    const dismissToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    }, []);

    return (
        <ToastContext.Provider value={{ addToast, dismissToast }}>
            {children}

            {/* Toast Container */}
            <div className="fixed bottom-20 right-4 z-50 flex flex-col gap-2">
                {toasts.map(toast => (
                    <Toast
                        key={toast.id}
                        {...toast}
                        onDismiss={dismissToast}
                    />
                ))}
            </div>
        </ToastContext.Provider>
    );
};

export default ToastProvider;
