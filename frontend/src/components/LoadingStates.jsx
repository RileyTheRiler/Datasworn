import React from 'react';

/**
 * LoadingSpinner - Animated loading spinner
 */
export const LoadingSpinner = ({ size = 'md', message = '', className = '' }) => {
    const sizeClasses = {
        sm: 'w-4 h-4',
        md: 'w-8 h-8',
        lg: 'w-12 h-12',
        xl: 'w-16 h-16'
    };

    return (
        <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
            {/* Spinner */}
            <div className="relative">
                <div className={`${sizeClasses[size]} border-2 border-disco-cyan/20 rounded-full`} />
                <div
                    className={`${sizeClasses[size]} border-2 border-transparent border-t-disco-cyan border-r-disco-cyan rounded-full absolute top-0 left-0 animate-spin`}
                />
            </div>

            {/* Message */}
            {message && (
                <p className="text-disco-muted font-mono text-sm animate-pulse">
                    {message}
                </p>
            )}
        </div>
    );
};

/**
 * LoadingDots - Three animated dots
 */
export const LoadingDots = ({ className = '' }) => {
    return (
        <div className={`flex gap-2 items-center justify-center ${className}`}>
            {[0, 1, 2].map(i => (
                <div
                    key={i}
                    className="w-2 h-2 bg-disco-accent rounded-full animate-pulse"
                    style={{ animationDelay: `${i * 0.15}s` }}
                />
            ))}
        </div>
    );
};

/**
 * LoadingSkeleton - Placeholder for loading content
 */
export const LoadingSkeleton = ({ width = '100%', height = '1rem', className = '' }) => {
    return (
        <div
            className={`bg-disco-muted/10 rounded animate-pulse ${className}`}
            style={{ width, height }}
        />
    );
};

/**
 * LoadingCard - Full card skeleton
 */
export const LoadingCard = ({ lines = 3 }) => {
    return (
        <div className="bg-disco-bg border border-disco-cyan/20 rounded-lg p-4 space-y-3">
            {/* Title */}
            <LoadingSkeleton width="60%" height="1.5rem" />

            {/* Content lines */}
            {Array.from({ length: lines }).map((_, i) => (
                <LoadingSkeleton
                    key={i}
                    width={i === lines - 1 ? '80%' : '100%'}
                    height="1rem"
                />
            ))}
        </div>
    );
};

/**
 * LoadingOverlay - Fullscreen loading overlay
 */
export const LoadingOverlay = ({ message = 'Loading...', transparent = false }) => {
    return (
        <div
            className={`fixed inset-0 z-[999] flex items-center justify-center ${
                transparent ? 'bg-black/50' : 'bg-disco-bg'
            } backdrop-blur-sm`}
        >
            <div className="bg-disco-bg border-2 border-disco-cyan/30 rounded-lg p-8 shadow-2xl">
                <LoadingSpinner size="lg" message={message} />
            </div>
        </div>
    );
};

/**
 * LoadingText - Animated loading text with typewriter effect
 */
export const LoadingText = ({ messages = ['Loading...'], interval = 3000 }) => {
    const [messageIndex, setMessageIndex] = React.useState(0);

    React.useEffect(() => {
        if (messages.length <= 1) return;

        const timer = setInterval(() => {
            setMessageIndex(prev => (prev + 1) % messages.length);
        }, interval);

        return () => clearInterval(timer);
    }, [messages, interval]);

    return (
        <p className="text-disco-paper font-serif italic text-xl animate-pulse">
            {messages[messageIndex]}
        </p>
    );
};

export default LoadingSpinner;
