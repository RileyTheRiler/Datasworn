import React, { createContext, useContext, useState, useEffect } from 'react';

/**
 * AccessibilityContext - Manages accessibility settings and preferences
 * 
 * Features:
 * - Detects and respects prefers-reduced-motion
 * - Provides screen reader announcements
 * - Manages high contrast mode
 * - Persists user preferences
 */

const AccessibilityContext = createContext(null);

export const useAccessibility = () => {
    const context = useContext(AccessibilityContext);
    if (!context) {
        throw new Error('useAccessibility must be used within AccessibilityProvider');
    }
    return context;
};

export const AccessibilityProvider = ({ children }) => {
    // Detect system preference for reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const [reducedMotion, setReducedMotion] = useState(() => {
        const saved = localStorage.getItem('reducedMotion');
        return saved !== null ? JSON.parse(saved) : prefersReducedMotion;
    });

    const [highContrast, setHighContrast] = useState(() => {
        const saved = localStorage.getItem('highContrast');
        return saved ? JSON.parse(saved) : false;
    });

    const [screenReaderEnabled, setScreenReaderEnabled] = useState(() => {
        const saved = localStorage.getItem('screenReaderEnabled');
        return saved ? JSON.parse(saved) : true;
    });

    const [fontSize, setFontSize] = useState(() => {
        const saved = localStorage.getItem('fontSize');
        return saved ? parseInt(saved) : 100; // Percentage
    });

    // Live region for screen reader announcements
    const [announcement, setAnnouncement] = useState('');

    // Listen for system preference changes
    useEffect(() => {
        const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
        const handleChange = (e) => {
            // Only auto-update if user hasn't manually set a preference
            const userPreference = localStorage.getItem('reducedMotion');
            if (userPreference === null) {
                setReducedMotion(e.matches);
            }
        };

        mediaQuery.addEventListener('change', handleChange);
        return () => mediaQuery.removeEventListener('change', handleChange);
    }, []);

    // Persist preferences
    useEffect(() => {
        localStorage.setItem('reducedMotion', JSON.stringify(reducedMotion));
    }, [reducedMotion]);

    useEffect(() => {
        localStorage.setItem('highContrast', JSON.stringify(highContrast));
        // Apply high contrast class to body
        if (highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
    }, [highContrast]);

    useEffect(() => {
        localStorage.setItem('screenReaderEnabled', JSON.stringify(screenReaderEnabled));
    }, [screenReaderEnabled]);

    useEffect(() => {
        localStorage.setItem('fontSize', fontSize.toString());
        // Apply font size to root
        document.documentElement.style.fontSize = `${fontSize}%`;
    }, [fontSize]);

    /**
     * Announce a message to screen readers
     * @param {string} message - Message to announce
     * @param {string} priority - 'polite' or 'assertive'
     */
    const announceToScreenReader = (message, priority = 'polite') => {
        if (!screenReaderEnabled) return;

        setAnnouncement(''); // Clear first to ensure change is detected
        setTimeout(() => {
            setAnnouncement(message);
        }, 100);
    };

    const value = {
        reducedMotion,
        setReducedMotion,
        highContrast,
        setHighContrast,
        screenReaderEnabled,
        setScreenReaderEnabled,
        fontSize,
        setFontSize,
        announceToScreenReader,
        prefersReducedMotion
    };

    return (
        <AccessibilityContext.Provider value={value}>
            {children}

            {/* Screen reader live region */}
            <div
                role="status"
                aria-live="polite"
                aria-atomic="true"
                className="sr-only"
                style={{
                    position: 'absolute',
                    left: '-10000px',
                    width: '1px',
                    height: '1px',
                    overflow: 'hidden'
                }}
            >
                {announcement}
            </div>
        </AccessibilityContext.Provider>
    );
};

export default AccessibilityProvider;
