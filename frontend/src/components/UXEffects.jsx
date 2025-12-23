import React, { useState, useEffect, useCallback } from 'react';

/**
 * UXEffects - Central component for dramatic visual effects
 * 
 * Provides:
 * - Screen shake on critical events
 * - Tension vignette that pulses with intensity
 * - Mood-based color overlays
 * - Hijack takeover animation
 */

// ============================================================================
// SCREEN SHAKE EFFECT
// ============================================================================
export const ScreenShake = ({ children, trigger, intensity = 'medium' }) => {
    const [shaking, setShaking] = useState(false);

    const intensityMap = {
        light: { duration: 200, class: 'shake-light' },
        medium: { duration: 300, class: 'shake-medium' },
        heavy: { duration: 500, class: 'shake-heavy' },
    };

    useEffect(() => {
        if (trigger) {
            setShaking(true);
            const timer = setTimeout(() => setShaking(false), intensityMap[intensity].duration);
            return () => clearTimeout(timer);
        }
    }, [trigger, intensity]);

    return (
        <div className={shaking ? intensityMap[intensity].class : ''}>
            {children}
        </div>
    );
};

// ============================================================================
// TENSION VIGNETTE
// ============================================================================
export const TensionVignette = ({ tension = 0, isActive = true }) => {
    // Tension ranges from 0 to 1
    // At 0: barely visible vignette
    // At 1: intense pulsing red vignette

    if (!isActive) return null;

    const baseOpacity = 0.2 + (tension * 0.5);
    const pulseSpeed = tension > 0.7 ? '1s' : tension > 0.4 ? '2s' : '4s';
    const color = tension > 0.7
        ? 'rgba(185, 63, 63, VAR)' // disco-red
        : tension > 0.4
            ? 'rgba(212, 93, 53, VAR)' // disco-accent (orange)
            : 'rgba(0, 0, 0, VAR)';

    return (
        <div
            className="fixed inset-0 pointer-events-none z-40"
            style={{
                background: `radial-gradient(ellipse at center, transparent 40%, ${color.replace('VAR', baseOpacity.toString())} 100%)`,
                animation: tension > 0.3 ? `tensionPulse ${pulseSpeed} ease-in-out infinite` : 'none',
            }}
        />
    );
};

// ============================================================================
// MOOD TINT OVERLAY
// ============================================================================
export const MoodTint = ({ emotion = 'neutral', intensity = 0.1 }) => {
    const emotionColors = {
        fear: 'rgba(125, 111, 184, INTENSITY)',      // purple
        anger: 'rgba(185, 63, 63, INTENSITY)',       // red
        hope: 'rgba(107, 228, 227, INTENSITY)',      // cyan
        despair: 'rgba(90, 90, 106, INTENSITY)',     // muted gray
        curiosity: 'rgba(224, 174, 66, INTENSITY)',  // yellow
        neutral: 'rgba(0, 0, 0, 0)',
    };

    const color = emotionColors[emotion] || emotionColors.neutral;

    return (
        <div
            className="fixed inset-0 pointer-events-none z-30 transition-all duration-2000 ease-in-out"
            style={{
                backgroundColor: color.replace('INTENSITY', intensity.toString()),
                mixBlendMode: 'overlay',
            }}
        />
    );
};

// ============================================================================
// HIJACK TAKEOVER ANIMATION
// ============================================================================
export const HijackOverlay = ({ isActive, aspect, onComplete }) => {
    const [phase, setPhase] = useState('idle'); // idle, flicker, takeover, stabilize

    useEffect(() => {
        if (isActive) {
            setPhase('flicker');

            // Flicker phase
            const flickerTimer = setTimeout(() => setPhase('takeover'), 500);

            // Full takeover
            const takeoverTimer = setTimeout(() => setPhase('stabilize'), 2000);

            // Stabilize and callback
            const stableTimer = setTimeout(() => {
                setPhase('idle');
                onComplete?.();
            }, 4000);

            return () => {
                clearTimeout(flickerTimer);
                clearTimeout(takeoverTimer);
                clearTimeout(stableTimer);
            };
        }
    }, [isActive, onComplete]);

    if (phase === 'idle') return null;

    const aspectColors = {
        amygdala: '#b93f3f',      // Fear/Aggression - Red
        cortex: '#6be4e3',        // Logic - Cyan
        hippocampus: '#7d6fb8',   // Memory - Purple
        brain_stem: '#e0ae42',    // Survival - Yellow
        temporal: '#4a7a96',      // Identity - Blue
    };

    const color = aspectColors[aspect] || '#b93f3f';

    return (
        <div className={`fixed inset-0 z-50 flex items-center justify-center transition-all
            ${phase === 'flicker' ? 'animate-flicker' : ''}
            ${phase === 'takeover' ? 'bg-black' : 'bg-black/80'}
        `}>
            {/* Static noise overlay */}
            <div className="absolute inset-0 opacity-20 bg-noise animate-static" />

            {/* Central message */}
            <div className={`text-center transition-all duration-500 
                ${phase === 'takeover' ? 'scale-110' : 'scale-100'}
            `}>
                <div
                    className="font-mono text-6xl font-bold uppercase tracking-widest mb-4"
                    style={{ color, textShadow: `0 0 20px ${color}, 0 0 40px ${color}` }}
                >
                    {aspect?.replace('_', ' ')}
                </div>
                <div className="font-serif text-2xl text-disco-paper/80 italic">
                    SYSTEM OVERRIDE
                </div>

                {/* Glitch lines */}
                <div className="mt-8 space-y-1">
                    {[...Array(5)].map((_, i) => (
                        <div
                            key={i}
                            className="h-0.5 bg-current animate-glitch"
                            style={{
                                color,
                                width: `${Math.random() * 200 + 100}px`,
                                marginLeft: `${Math.random() * 100}px`,
                                animationDelay: `${i * 0.1}s`
                            }}
                        />
                    ))}
                </div>
            </div>

            {/* Scanlines */}
            <div className="absolute inset-0 pointer-events-none opacity-20"
                style={{
                    background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.3) 2px, rgba(0,0,0,0.3) 4px)',
                }}
            />
        </div>
    );
};

// ============================================================================
// AMBIENT PARTICLES
// ============================================================================
export const AmbientParticles = ({ type = 'dust', count = 20 }) => {
    const [particles, setParticles] = useState([]);

    useEffect(() => {
        const newParticles = [...Array(count)].map((_, i) => ({
            id: i,
            x: Math.random() * 100,
            y: Math.random() * 100,
            size: Math.random() * 3 + 1,
            duration: Math.random() * 20 + 10,
            delay: Math.random() * 10,
        }));
        setParticles(newParticles);
    }, [count]);

    const typeStyles = {
        dust: 'bg-disco-paper/20',
        sparks: 'bg-disco-accent',
        static: 'bg-disco-cyan/30',
    };

    return (
        <div className="fixed inset-0 pointer-events-none z-20 overflow-hidden">
            {particles.map(p => (
                <div
                    key={p.id}
                    className={`absolute rounded-full ${typeStyles[type]} animate-float`}
                    style={{
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        width: `${p.size}px`,
                        height: `${p.size}px`,
                        animationDuration: `${p.duration}s`,
                        animationDelay: `${p.delay}s`,
                    }}
                />
            ))}
        </div>
    );
};

// ============================================================================
// MOMENTUM BURST (for momentum changes)
// ============================================================================
export const MomentumBurst = ({ trigger, isPositive = true }) => {
    const [active, setActive] = useState(false);

    useEffect(() => {
        if (trigger) {
            setActive(true);
            const timer = setTimeout(() => setActive(false), 1000);
            return () => clearTimeout(timer);
        }
    }, [trigger]);

    if (!active) return null;

    const color = isPositive ? 'disco-cyan' : 'disco-red';

    return (
        <div className="fixed inset-0 pointer-events-none z-50 flex items-center justify-center">
            <div className={`w-4 h-4 rounded-full bg-${color} animate-ping`} />
            <div className={`absolute w-32 h-32 rounded-full border-2 border-${color} animate-ripple`} />
        </div>
    );
};

// ============================================================================
// REACTIVE STATIC (Health/Spirit Warning)
// ============================================================================
export const ReactiveStatic = ({ health = 5, spirit = 5, max = 5 }) => {
    // Calculate critical status (below 20% = 1/5)
    // 0 = no static, 1 = full static
    const healthFactor = Math.max(0, (1 - (health / max)) * 2); // Starts ramping up at 50% health, severe at 0
    const spiritFactor = Math.max(0, (1 - (spirit / max)) * 2);

    const intensity = Math.max(0, (healthFactor + spiritFactor) - 1.5); // Only show if critically low (e.g. sum > 1.5)

    // Or simpler logic: if either is <= 1 (20%), show static
    const isCritical = health <= 1 || spirit <= 1;
    const staticOpacity = isCritical ? 0.15 : 0;

    if (!isCritical) return null;

    return (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden mix-blend-screen">
            <div
                className="absolute inset-0 bg-noise animate-static"
                style={{ opacity: staticOpacity }}
            />
            {/* Occasional flicker handled by parent or CSS animation keyframes variation */}
        </div>
    );
};

// ============================================================================
// SCANLINE TRANSITION WRAPPER
// ============================================================================
export const ScanlineTransition = ({ children, trigger }) => {
    const [active, setActive] = useState(false);

    useEffect(() => {
        if (trigger) {
            setActive(true);
            const timer = setTimeout(() => setActive(false), 600);
            return () => clearTimeout(timer);
        }
    }, [trigger]);

    return (
        <div className={`relative ${active ? 'animate-scanline' : ''}`}>
            {children}
        </div>
    );
};

export default {
    ScreenShake,
    TensionVignette,
    MoodTint,
    HijackOverlay,
    AmbientParticles,
    MomentumBurst,
    ReactiveStatic,
    ScanlineTransition
};
