import React, { useState, useEffect, useRef } from 'react';
import { useSoundEffects } from '../contexts/SoundEffectsContext';
import { useAccessibility } from '../contexts/AccessibilityContext';
import api from '../utils/api';

/**
 * Enhanced SkillCheck with dramatic multi-stage dice animation
 * 
 * Stages:
 * 1. Gather - Dice appear and gather energy
 * 2. Tumble - Dice tumble with number cycling
 * 3. Reveal - Dramatic pause, then result
 */
const SkillCheck = ({ stat, statName, character, onRollComplete, onClose }) => {
    const [odds, setOdds] = useState(null);
    const [stage, setStage] = useState('ready'); // ready, gather, tumble, reveal, complete
    const [result, setResult] = useState(null);
    const [displayNumbers, setDisplayNumbers] = useState({ action: 0, c1: 0, c2: 0 });
    const numberCycleRef = useRef(null);

    // Sound and accessibility
    const { playSound } = useSoundEffects();
    const { reducedMotion, announceToScreenReader } = useAccessibility();

    useEffect(() => {
        // Fetch odds when component mounts
        const fetchOdds = async () => {
            try {
                const data = await api.post('/roll/calculate', { stat: stat, adds: 0 });
                setOdds(data);
            } catch (err) {
                console.error("Failed to fetch odds", err);
            }
        };
        fetchOdds();
    }, [stat]);

    // Number cycling animation during tumble phase
    useEffect(() => {
        if (stage === 'tumble') {
            numberCycleRef.current = setInterval(() => {
                setDisplayNumbers({
                    action: Math.floor(Math.random() * 6) + 1,
                    c1: Math.floor(Math.random() * 10) + 1,
                    c2: Math.floor(Math.random() * 10) + 1,
                });
            }, 50);
        } else {
            clearInterval(numberCycleRef.current);
        }

        return () => clearInterval(numberCycleRef.current);
    }, [stage]);

    const handleRoll = async () => {
        // Announce to screen readers
        announceToScreenReader('Rolling dice...');

        // Reduced motion: skip straight to result
        if (reducedMotion) {
            try {
                const res = await onRollComplete();
                setDisplayNumbers({
                    action: res.roll.action_score,
                    c1: res.roll.challenge_dice[0],
                    c2: res.roll.challenge_dice[1],
                });
                setResult(res.roll);
                setStage('complete');

                // Announce result
                announceToScreenReader(`Roll result: ${res.roll.result}`);

                // Play result sound
                if (res.roll.result === 'Strong Hit') {
                    playSound('dice_hit');
                } else if (res.roll.result === 'Miss') {
                    playSound('dice_miss');
                }

                setTimeout(() => onClose(), 3500);
            } catch (err) {
                console.error("Roll failed", err);
                setStage('ready');
            }
            return;
        }

        // Stage 1: Gather
        setStage('gather');

        // Stage 2: Tumble (after brief gather)
        await new Promise(r => setTimeout(r, 400));
        setStage('tumble');

        // Play dice roll sound
        playSound('dice_roll');

        try {
            // Actually commit the roll
            const res = await onRollComplete();

            // Continue tumbling for drama
            await new Promise(r => setTimeout(r, 1200));

            // Stage 3: Reveal - freeze on final numbers
            setStage('reveal');
            setDisplayNumbers({
                action: res.roll.action_score,
                c1: res.roll.challenge_dice[0],
                c2: res.roll.challenge_dice[1],
            });

            // Brief pause for tension
            await new Promise(r => setTimeout(r, 800));

            // Stage 4: Complete - show result
            setResult(res.roll);
            setStage('complete');

            // Play result sound
            if (res.roll.result === 'Strong Hit') {
                playSound('dice_hit');
            } else if (res.roll.result === 'Miss') {
                playSound('dice_miss');
            }

            // Announce result to screen readers
            announceToScreenReader(`Roll result: ${res.roll.result}. Action score ${res.roll.action_score} versus challenge dice ${res.roll.challenge_dice[0]} and ${res.roll.challenge_dice[1]}`);

            // Auto close after viewing result
            setTimeout(() => onClose(), 3500);

        } catch (err) {
            console.error("Roll failed", err);
            setStage('ready');
        }
    };

    // Close on escape key
    useEffect(() => {
        const handleKey = (e) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, [onClose]);

    if (!odds) return null;

    const successChance = Math.round((odds.strong_hit + odds.weak_hit) * 100);

    const getResultColor = () => {
        if (!result) return 'border-disco-paper';
        if (result.result === 'Strong Hit') return 'border-disco-cyan';
        if (result.result === 'Weak Hit') return 'border-disco-yellow';
        return 'border-disco-red';
    };

    const getResultFlash = () => {
        if (!result) return '';
        if (result.result === 'Strong Hit') return 'flash-success';
        if (result.result === 'Miss') return 'flash-danger';
        return '';
    };

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md">
            <div className={`
                relative bg-disco-panel border-2 p-8 w-[520px] shadow-2xl overflow-hidden transition-all duration-300
                ${getResultColor()} ${getResultFlash()}
            `}>
                {/* Ambient glow effect */}
                <div className={`absolute inset-0 pointer-events-none transition-opacity duration-500 ${stage === 'tumble' ? 'opacity-30' : 'opacity-0'
                    }`} style={{
                        background: 'radial-gradient(circle at center, rgba(107, 228, 227, 0.3) 0%, transparent 70%)'
                    }} />

                {/* Header */}
                <div className="text-center mb-8 relative z-10">
                    <h2 className="font-serif text-3xl text-disco-paper uppercase tracking-widest mb-1 text-glow">
                        {stage === 'complete' ? result.result : "Skill Check"}
                    </h2>
                    <div className="font-mono text-disco-cyan text-sm uppercase">
                        {stage === 'gather' && 'Gathering fate...'}
                        {stage === 'tumble' && 'Dice tumbling...'}
                        {stage === 'reveal' && 'The Forge speaks...'}
                        {(stage === 'ready' || stage === 'complete') && `Checking ${statName} [${stat}]`}
                    </div>
                </div>

                {/* Dice Display Area */}
                <div className="flex justify-center items-center mb-8 relative h-40">
                    {stage === 'ready' ? (
                        /* Pre-roll odds display */
                        <div className="relative w-32 h-32 flex items-center justify-center border-4 border-disco-muted/30 rounded-full">
                            <div className="text-4xl font-serif font-bold text-white">{successChance}%</div>
                            <div className="absolute inset-0 border-4 border-disco-paper rounded-full opacity-20"></div>
                            {/* Animated ring */}
                            <div className="absolute inset-[-4px] border-4 border-disco-accent/50 rounded-full animate-pulse"></div>
                        </div>
                    ) : (
                        /* Dice rolling display */
                        <div className="flex items-center gap-6">
                            {/* Action Die (d6) */}
                            <div className={`
                                relative w-20 h-20 bg-disco-dark border-2 border-disco-cyan rounded-lg 
                                flex items-center justify-center shadow-lg
                                ${stage === 'gather' ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}
                                ${stage === 'tumble' ? 'animate-tumble' : ''}
                                transition-all duration-300
                            `}>
                                <span className="text-3xl font-mono font-bold text-disco-cyan">
                                    {displayNumbers.action}
                                </span>
                                <div className="absolute -bottom-6 text-xs font-mono text-disco-muted uppercase">
                                    +{stat}
                                </div>
                            </div>

                            {/* VS indicator */}
                            <div className={`
                                font-serif text-2xl text-disco-muted italic
                                ${stage === 'gather' ? 'opacity-0' : 'opacity-100'}
                                transition-all duration-500 delay-100
                            `}>
                                vs
                            </div>

                            {/* Challenge Dice (d10s) */}
                            <div className="flex gap-3">
                                <div className={`
                                    w-16 h-16 bg-disco-dark border-2 border-disco-red/70 rounded-lg 
                                    flex items-center justify-center shadow-lg
                                    ${stage === 'gather' ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}
                                    ${stage === 'tumble' ? 'animate-tumble' : ''}
                                    transition-all duration-300 delay-75
                                `} style={{ animationDelay: '0.1s' }}>
                                    <span className="text-2xl font-mono font-bold text-disco-red">
                                        {displayNumbers.c1}
                                    </span>
                                </div>
                                <div className={`
                                    w-16 h-16 bg-disco-dark border-2 border-disco-red/70 rounded-lg 
                                    flex items-center justify-center shadow-lg
                                    ${stage === 'gather' ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}
                                    ${stage === 'tumble' ? 'animate-tumble' : ''}
                                    transition-all duration-300 delay-150
                                `} style={{ animationDelay: '0.2s' }}>
                                    <span className="text-2xl font-mono font-bold text-disco-red">
                                        {displayNumbers.c2}
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Result Summary (when complete) */}
                {stage === 'complete' && result && (
                    <div className={`
                        text-center py-4 mb-4 border-t border-b border-disco-muted/30
                        ${result.result === 'Strong Hit' ? 'text-disco-cyan' :
                            result.result === 'Weak Hit' ? 'text-disco-yellow' : 'text-disco-red'}
                    `}>
                        <div className="text-5xl font-serif font-bold">
                            {result.action_score} vs {result.challenge_dice[0]}/{result.challenge_dice[1]}
                        </div>
                        {result.result === 'Strong Hit' && (
                            <div className="mt-2 font-mono text-sm uppercase tracking-widest opacity-80">
                                ✦ The Forge favors you ✦
                            </div>
                        )}
                        {result.result === 'Weak Hit' && (
                            <div className="mt-2 font-mono text-sm uppercase tracking-widest opacity-80">
                                ◈ Success, with complications ◈
                            </div>
                        )}
                        {result.result === 'Miss' && (
                            <div className="mt-2 font-mono text-sm uppercase tracking-widest opacity-80">
                                ✕ Fate turns against you ✕
                            </div>
                        )}
                    </div>
                )}

                {/* Roll Button (only in ready state) */}
                {stage === 'ready' && (
                    <div className="text-center relative z-10">
                        <button
                            onClick={handleRoll}
                            className="btn-disco w-full py-4 text-xl bg-disco-accent/20 hover:bg-disco-accent/40 border-disco-accent hover:border-disco-paper group"
                        >
                            <span className="group-hover:scale-110 inline-block transition-transform">
                                🎲 Roll Dice [1d6 + {stat}]
                            </span>
                        </button>
                        <div className="mt-4 flex justify-between text-xs font-mono text-disco-muted uppercase">
                            <span className="text-disco-cyan">Strong: {Math.round(odds.strong_hit * 100)}%</span>
                            <span className="text-disco-yellow">Weak: {Math.round(odds.weak_hit * 100)}%</span>
                            <span className="text-disco-red">Miss: {Math.round(odds.miss * 100)}%</span>
                        </div>
                    </div>
                )}

                {/* Status during roll */}
                {(stage === 'gather' || stage === 'tumble' || stage === 'reveal') && (
                    <div className="text-center">
                        <div className="flex justify-center gap-2">
                            {[0, 1, 2].map(i => (
                                <div
                                    key={i}
                                    className="w-2 h-2 bg-disco-accent rounded-full animate-pulse"
                                    style={{ animationDelay: `${i * 0.2}s` }}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-3 right-3 text-disco-muted hover:text-white text-xl transition-colors"
                    title="Close (Esc)"
                >
                    ✕
                </button>

                {/* Hint text */}
                <div className="absolute bottom-2 left-0 right-0 text-center text-[10px] font-mono text-disco-muted/50 uppercase">
                    Press ESC to close
                </div>
            </div>
        </div>
    );
};

export default SkillCheck;
