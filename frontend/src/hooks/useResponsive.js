import { useState, useEffect } from 'react';

/**
 * useResponsive - Hook for responsive design helpers
 *
 * Returns:
 * - isMobile: true if screen width < 768px
 * - isTablet: true if screen width >= 768px and < 1024px
 * - isDesktop: true if screen width >= 1024px
 * - width: current window width
 * - height: current window height
 */
export const useResponsive = () => {
    const [dimensions, setDimensions] = useState({
        width: typeof window !== 'undefined' ? window.innerWidth : 0,
        height: typeof window !== 'undefined' ? window.innerHeight : 0,
    });

    useEffect(() => {
        const handleResize = () => {
            setDimensions({
                width: window.innerWidth,
                height: window.innerHeight,
            });
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    return {
        width: dimensions.width,
        height: dimensions.height,
        isMobile: dimensions.width < 768,
        isTablet: dimensions.width >= 768 && dimensions.width < 1024,
        isDesktop: dimensions.width >= 1024,
        isSmallScreen: dimensions.width < 1024,
        isLargeScreen: dimensions.width >= 1280,
    };
};

/**
 * useMediaQuery - Hook for custom media queries
 *
 * @param {string} query - Media query string (e.g., '(max-width: 768px)')
 * @returns {boolean} - Whether the media query matches
 */
export const useMediaQuery = (query) => {
    const [matches, setMatches] = useState(() => {
        if (typeof window !== 'undefined') {
            return window.matchMedia(query).matches;
        }
        return false;
    });

    useEffect(() => {
        const mediaQuery = window.matchMedia(query);
        const handler = (e) => setMatches(e.matches);

        // Modern browsers
        if (mediaQuery.addEventListener) {
            mediaQuery.addEventListener('change', handler);
            return () => mediaQuery.removeEventListener('change', handler);
        } else {
            // Fallback for older browsers
            mediaQuery.addListener(handler);
            return () => mediaQuery.removeListener(handler);
        }
    }, [query]);

    return matches;
};

/**
 * useTouchDevice - Detect if device supports touch
 */
export const useTouchDevice = () => {
    const [isTouch, setIsTouch] = useState(() => {
        if (typeof window !== 'undefined') {
            return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        }
        return false;
    });

    useEffect(() => {
        const checkTouch = () => {
            setIsTouch('ontouchstart' in window || navigator.maxTouchPoints > 0);
        };

        checkTouch();
    }, []);

    return isTouch;
};

export default useResponsive;
