import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAccessibility } from '../contexts/AccessibilityContext';

/**
 * TypewriterText - Reveals text character-by-character for dramatic effect
 * 
 * Features:
 * - Variable speed based on punctuation (pauses at periods, commas)
 * - Click to skip and reveal all
 * - Blinking cursor at the end
 * - Smooth reveal with natural rhythm
 * - Respects prefers-reduced-motion
 */
const TypewriterText = ({
    text,
    baseSpeed = 25,        // ms per character (lower = faster)
    onComplete,            // callback when typing finishes
    className = "",
    skipOnClick = true,
}) => {
    const [displayedText, setDisplayedText] = useState('');
    const [isComplete, setIsComplete] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const indexRef = useRef(0);
    const timeoutRef = useRef(null);
    const containerRef = useRef(null);

    const { reducedMotion } = useAccessibility();

    // Speed modifiers for different characters
    const getCharDelay = useCallback((char, nextChar) => {
        // Long pause after sentence endings
        if (['.', '!', '?'].includes(char) && nextChar === ' ') {
            return baseSpeed * 8;
        }
        // Medium pause after commas, colons, semicolons
        if ([',', ':', ';', '—', '–'].includes(char)) {
            return baseSpeed * 4;
        }
        // Slight pause after closing quotes
        if (['"', "'", '"', "'"].includes(char)) {
            return baseSpeed * 2;
        }
        // Quick for spaces
        if (char === ' ') {
            return baseSpeed * 0.5;
        }
        // Faster for common letters in rapid sequences
        return baseSpeed;
    }, [baseSpeed]);

    // Type next character
    const typeNextChar = useCallback(() => {
        if (indexRef.current < text.length) {
            const currentChar = text[indexRef.current];
            const nextChar = text[indexRef.current + 1] || '';

            setDisplayedText(text.slice(0, indexRef.current + 1));
            indexRef.current++;

            const delay = getCharDelay(currentChar, nextChar);
            timeoutRef.current = setTimeout(typeNextChar, delay);
        } else {
            setIsComplete(true);
            setIsTyping(false);
            onComplete?.();
        }
    }, [text, getCharDelay, onComplete]);

    // Start typing when text changes
    useEffect(() => {
        // Reset state for new text
        indexRef.current = 0;
        setDisplayedText('');
        setIsComplete(false);

        // Clear any existing timeout
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        // If reduced motion, show all text immediately
        if (reducedMotion) {
            setDisplayedText(text);
            setIsComplete(true);
            setIsTyping(false);
            indexRef.current = text.length;
            onComplete?.();
            return;
        }

        setIsTyping(true);

        // Start typing after a brief delay
        timeoutRef.current = setTimeout(typeNextChar, 100);

        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [text, typeNextChar, reducedMotion, onComplete]);

    // Skip to end on click
    const handleClick = () => {
        if (skipOnClick && !isComplete) {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
            setDisplayedText(text);
            setIsComplete(true);
            setIsTyping(false);
            indexRef.current = text.length;
            onComplete?.();
        }
    };

    return (
        <div
            ref={containerRef}
            className={`relative ${className} ${skipOnClick && !isComplete ? 'cursor-pointer' : ''}`}
            onClick={handleClick}
            title={skipOnClick && !isComplete ? 'Click to skip' : undefined}
        >
            <span className="whitespace-pre-wrap">{displayedText}</span>
            {isTyping && (
                <span className="typewriter-cursor inline-block w-[2px] h-[1.1em] bg-disco-accent ml-0.5 align-middle" />
            )}
        </div>
    );
};

export default TypewriterText;
