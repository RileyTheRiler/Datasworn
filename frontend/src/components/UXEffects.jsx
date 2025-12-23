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
    // Calculate analog interference based on missing stats
    // 0.0 = perfect condition, 1.0 = near death
    const healthLoss = Math.max(0, (max - health) / max);
    const spiritLoss = Math.max(0, (max - spirit) / max);

    // Composite interference value
    // Heavy weight on health (physical damage causes hardware failure)
    // Spirit flickering (sync issues)
    const interference = (healthLoss * 0.7) + (spiritLoss * 0.3);

    // Thresholds for effects
    // Low interference: Subtle grain
    // High interference: Heavy static + chromatic distortion

    if (interference < 0.1) return null;

    // Opacity scales non-linearly: little bit at first, ramping up quickly near end
    // e.g. 0.2 loss -> 0.04 opacity
    // 0.8 loss -> 0.64 opacity
    // 1.0 loss -> 1.0 opacity
    const baseOpacity = Math.pow(interference, 2.5);

    // Dynamic noise intensity
    const noiseOpacity = Math.min(0.15, baseOpacity * 0.8);

    return (
        <div className="fixed inset-0 pointer-events-none z-[100] overflow-hidden mix-blend-hard-light">
            {/* Base Static Layer */}
            <div
                className="absolute inset-0 bg-noise animate-static"
                style={{ opacity: noiseOpacity }}
            />

            {/* Critical Failure Scanlines (only when very hurt) */}
            {interference > 0.6 && (
                <div
                    className="absolute inset-0 bg-scanlines opacity-30 animate-scanline-drift"
                    style={{ animationDuration: `${2 - interference}s` }}
                />
            )}

            {/* Glitch Slices on Critical */}
            {interference > 0.8 && (
                <div className="absolute inset-0 animate-glitch-slice opacity-20"></div>
            )}
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

// ============================================================================
// STARFIELD ANIMATION
// ============================================================================
export const Starfield = ({ count = 100, speed = 1 }) => {
    // Generate static stars once to avoid hydration mismatches or constant re-renders
    const [layers, setLayers] = useState({ back: [], mid: [], front: [] });

    useEffect(() => {
        const generateStars = (n) => [...Array(n)].map((_, i) => ({
            id: i,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            size: Math.random() < 0.1 ? 2 : 1, // Occasional larger star
            opacity: Math.random() * 0.7 + 0.3,
        }));

        setLayers({
            back: generateStars(Math.floor(count * 0.6)),   // Distant stars (slowest)
            mid: generateStars(Math.floor(count * 0.3)),    // Mid-range stars
            front: generateStars(Math.floor(count * 0.1)),  // Close stars (fastest)
        });
    }, [count]);

    const Layer = ({ stars, duration, sizeModifier = 1, animationClass = 'animate-star-scroll-mid' }) => (
        <div
            className={`absolute inset-0 ${animationClass}`}
            style={{ animationDuration: `${duration / speed}s` }}
        >
            {stars.map(s => (
                <div
                    key={s.id}
                    className="absolute rounded-full bg-white"
                    style={{
                        left: s.left,
                        top: s.top,
                        width: `${s.size * sizeModifier}px`,
                        height: `${s.size * sizeModifier}px`,
                        opacity: s.opacity,
                        boxShadow: s.size > 1.5 ? '0 0 2px rgba(255, 255, 255, 0.8)' : 'none'
                    }}
                />
            ))}
            {/* Duplicate for seamless loop */}
            {stars.map(s => (
                <div
                    key={`dup-${s.id}`}
                    className="absolute rounded-full bg-white"
                    style={{
                        left: s.left,
                        top: `calc(${s.top} - 100vh)`, // Position above for scrolling down
                        width: `${s.size * sizeModifier}px`,
                        height: `${s.size * sizeModifier}px`,
                        opacity: s.opacity,
                        boxShadow: s.size > 1.5 ? '0 0 2px rgba(255, 255, 255, 0.8)' : 'none'
                    }}
                />
            ))}
        </div>
    );

    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0 bg-black">
            {/* Base deep space gradient */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#050510] via-[#0a0a20] to-[#050510] opacity-80" />

            {/* Star Layers with Parallax */}
            <div className="absolute inset-0 opacity-40">
                <Layer stars={layers.back} duration={60} sizeModifier={0.8} animationClass="animate-star-scroll-back" />
            </div>
            <div className="absolute inset-0 opacity-60">
                <Layer stars={layers.mid} duration={40} sizeModifier={1} animationClass="animate-star-scroll-mid" />
            </div>
            <div className="absolute inset-0 opacity-80">
                <Layer stars={layers.front} duration={20} sizeModifier={1.5} animationClass="animate-star-scroll-front" />
            </div>
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
    ScanlineTransition,
    Starfield
};
