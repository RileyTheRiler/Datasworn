import React, { useState, useEffect } from 'react';

const TextScramble = ({ text, duration = 150, className = '' }) => {
    const [display, setDisplay] = useState(text);
    const chars = '!@#$%^&*()_+-=[]{}|;:,.<>/?0123456789ABCDEF';

    useEffect(() => {
        let startTime = Date.now();
        let frameId;

        const update = () => {
            const now = Date.now();
            const progress = Math.min((now - startTime) / duration, 1);

            if (progress < 1) {
                const scrambled = text
                    .split('')
                    .map((char, index) => {
                        if (char === ' ') return ' ';
                        if (Math.random() < progress) return char;
                        return chars[Math.floor(Math.random() * chars.length)];
                    })
                    .join('');
                setDisplay(scrambled);
                frameId = requestAnimationFrame(update);
            } else {
                setDisplay(text);
            }
        };

        frameId = requestAnimationFrame(update);
        return () => cancelAnimationFrame(frameId);
    }, [text, duration]);

    return <span className={className}>{display}</span>;
};

export default TextScramble;
