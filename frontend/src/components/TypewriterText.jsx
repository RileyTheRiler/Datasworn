import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useAccessibility } from '../contexts/AccessibilityContext';
import { useVoice } from '../contexts/VoiceContext';
import NPCHoverCard from './NPCHoverCard';

/**
 * TypewriterText - Reveals text character-by-character for dramatic effect
 * 
 * Features:
 * - Variable speed based on punctuation
 * - Click to skip
 * - Blinking cursor
 * - NPC Hover Cards via [[Name]] syntax
 * - "Read Aloud" button for manually triggering TTS
 */
const TypewriterText = ({
    text,
    characters = {},       // NPC data for hover cards
    baseSpeed = 25,        // ms per character
    onComplete,            // callback when typing finishes
    onInterrogate,         // callback when interrogate button clicked
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

    // Speed modifiers
    const getCharDelay = useCallback((char, nextChar) => {
        if (['.', '!', '?'].includes(char) && nextChar === ' ') return baseSpeed * 8;
        if ([',', ':', ';', '—', '–'].includes(char)) return baseSpeed * 4;
        if (['"', "'"].includes(char)) return baseSpeed * 2;
        if (char === ' ') return baseSpeed * 0.5;
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

    // Start typing
    useEffect(() => {
        indexRef.current = 0;
        setDisplayedText('');
        setIsComplete(false);
        if (timeoutRef.current) clearTimeout(timeoutRef.current);

        if (reducedMotion) {
            setDisplayedText(text);
            setIsComplete(true);
            setIsTyping(false);
            indexRef.current = text.length;
            onComplete?.();
            return;
        }

        setIsTyping(true);
        timeoutRef.current = setTimeout(typeNextChar, 100);

        return () => {
            if (timeoutRef.current) clearTimeout(timeoutRef.current);
        };
    }, [text, typeNextChar, reducedMotion, onComplete]);

    const handleClick = () => {
        if (skipOnClick && !isComplete) {
            if (timeoutRef.current) clearTimeout(timeoutRef.current);
            setDisplayedText(text);
            setIsComplete(true);
            setIsTyping(false);
            indexRef.current = text.length;
            onComplete?.();
        }
    };

    // Parse markers [[Name]]
    const renderProcessedText = useMemo(() => {
        if (!displayedText) return null;
        const parts = displayedText.split(/(\[\[.*?\]\])/g);
        return parts.map((part, i) => {
            if (part.startsWith('[[') && part.endsWith(']]')) {
                const name = part.slice(2, -2);
                return <NPCHoverCard key={i} name={name} characters={characters} onInterrogate={onInterrogate} />;
            }
            return <React.Fragment key={i}>{part}</React.Fragment>;
        });
    }, [displayedText, characters, onInterrogate]);

    return (
        <div className={`relative group/typewriter ${className}`}>
            <div
                ref={containerRef}
                className={`relative ${skipOnClick && !isComplete ? 'cursor-pointer' : ''}`}
                onClick={handleClick}
                title={skipOnClick && !isComplete ? 'Click to skip' : undefined}
            >
                <span className="whitespace-pre-wrap">{renderProcessedText}</span>
                {isTyping && (
                    <span className="typewriter-cursor inline-block w-[2px] h-[1.1em] bg-disco-accent ml-0.5 align-middle" />
                )}
            </div>

            {/* Read Aloud Button */}
            {isComplete && (
                <div className="absolute -top-6 right-0 opacity-0 group-hover/typewriter:opacity-100 transition-opacity duration-300">
                    <ReadAloudButton text={text} />
                </div>
            )}
        </div>
    );
};

const ReadAloudButton = ({ text }) => {
    const { speak, isSpeaking, voiceEnabled } = useVoice();

    if (!voiceEnabled) return null;

    return (
        <button
            onClick={(e) => {
                e.stopPropagation();
                speak(text);
            }}
            className="text-xs font-mono text-disco-muted hover:text-disco-cyan flex items-center gap-1 bg-black/50 px-2 py-1 rounded backdrop-blur-sm transition-colors"
            disabled={isSpeaking}
        >
            <span>{isSpeaking ? '🔊 Playing...' : '🔈 Read'}</span>
        </button>
    );
};

export default TypewriterText;
