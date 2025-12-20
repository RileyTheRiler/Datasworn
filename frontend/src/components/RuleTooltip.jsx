import React, { useState, useEffect, useRef } from 'react';

/**
 * RuleTooltip - Contextual tooltips for game rules
 *
 * Features:
 * - Hover-triggered rule explanations
 * - Detailed move breakdowns
 * - Stat descriptions
 * - Keyboard accessible
 */

// Built-in rule definitions for quick access
const RULES = {
    // Stats
    edge: {
        title: 'Edge',
        description: 'Quickness, agility, and prowess in ranged combat.',
        examples: ['Dodging attacks', 'Shooting accurately', 'Quick reflexes']
    },
    heart: {
        title: 'Heart',
        description: 'Courage, willpower, empathy, sociability, and loyalty.',
        examples: ['Inspiring others', 'Resisting fear', 'Building connections']
    },
    iron: {
        title: 'Iron',
        description: 'Physical strength, endurance, and prowess in close combat.',
        examples: ['Melee fighting', 'Enduring hardship', 'Feats of strength']
    },
    shadow: {
        title: 'Shadow',
        description: 'Sneakiness, deceptiveness, and cunning.',
        examples: ['Stealth', 'Lying convincingly', 'Trickery']
    },
    wits: {
        title: 'Wits',
        description: 'Expertise, knowledge, and observation.',
        examples: ['Gathering info', 'Noticing details', 'Technical knowledge']
    },

    // Conditions
    health: {
        title: 'Health',
        description: 'Physical condition. At 0, you are wounded and must Endure Harm.',
        warning: 'At 0 health, take -1 momentum after any action.'
    },
    spirit: {
        title: 'Spirit',
        description: 'Mental and emotional state. At 0, you are shaken and must Endure Stress.',
        warning: 'At 0 spirit, take -1 momentum after any action.'
    },
    supply: {
        title: 'Supply',
        description: 'Your preparedness and resources for the journey.',
        warning: 'At 0 supply, you are unprepared and must make Sacrifice or Sacrilege.'
    },
    momentum: {
        title: 'Momentum',
        description: 'Represents luck, confidence, and preparation. Burn to improve roll results.',
        max: '+10',
        min: '-6',
        reset: '+2'
    },

    // Moves
    face_danger: {
        title: 'Face Danger',
        description: 'When you attempt something risky or react to an imminent threat.',
        stat: 'Appropriate stat',
        strong_hit: 'You succeed. Take +1 momentum.',
        weak_hit: 'You succeed but face a troublesome cost.',
        miss: 'You fail or face a dramatic setback. Pay the Price.'
    },
    secure_advantage: {
        title: 'Secure an Advantage',
        description: 'When you assess a situation, make preparations, or position yourself for success.',
        stat: 'Appropriate stat',
        strong_hit: 'Take +2 momentum.',
        weak_hit: 'Take +1 momentum.',
        miss: 'You fail or your assumptions betray you. Pay the Price.'
    },
    gather_information: {
        title: 'Gather Information',
        description: 'When you search an area, ask questions, or investigate.',
        stat: 'Wits',
        strong_hit: 'You discover something helpful and specific. Take +2 momentum.',
        weak_hit: 'The info complicates your quest or introduces new danger.',
        miss: 'Your investigation reveals an unwelcome truth or triggers danger.'
    },
    compel: {
        title: 'Compel',
        description: 'When you attempt to persuade someone or make them do what you want.',
        stat: 'Heart (charm), Shadow (deceive), or Iron (threaten)',
        strong_hit: 'They do what you want.',
        weak_hit: 'They do it but ask something in return.',
        miss: 'They refuse and your relationship worsens.'
    },

    // Roll Results
    strong_hit: {
        title: 'Strong Hit',
        description: 'Your action score beats BOTH challenge dice. You succeed with full effect!',
        color: 'cyan'
    },
    weak_hit: {
        title: 'Weak Hit',
        description: 'Your action score beats ONE challenge die. Success with a complication.',
        color: 'yellow'
    },
    miss: {
        title: 'Miss',
        description: 'Your action score beats NEITHER challenge die. Something goes wrong.',
        color: 'red'
    },

    // Progress
    progress: {
        title: 'Progress Track',
        description: 'Track advancement toward completing vows, journeys, and challenges.',
        ranks: [
            'Troublesome: 3 progress per mark',
            'Dangerous: 2 progress per mark',
            'Formidable: 1 progress per mark',
            'Extreme: 2 ticks per mark',
            'Epic: 1 tick per mark'
        ]
    }
};

const RuleTooltip = ({ ruleId, children, position = 'top' }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
    const triggerRef = useRef(null);
    const tooltipRef = useRef(null);

    const rule = RULES[ruleId];

    useEffect(() => {
        if (isVisible && triggerRef.current && tooltipRef.current) {
            const triggerRect = triggerRef.current.getBoundingClientRect();
            const tooltipRect = tooltipRef.current.getBoundingClientRect();

            let top, left;

            switch (position) {
                case 'top':
                    top = triggerRect.top - tooltipRect.height - 8;
                    left = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2);
                    break;
                case 'bottom':
                    top = triggerRect.bottom + 8;
                    left = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2);
                    break;
                case 'left':
                    top = triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2);
                    left = triggerRect.left - tooltipRect.width - 8;
                    break;
                case 'right':
                    top = triggerRect.top + (triggerRect.height / 2) - (tooltipRect.height / 2);
                    left = triggerRect.right + 8;
                    break;
                default:
                    top = triggerRect.top - tooltipRect.height - 8;
                    left = triggerRect.left;
            }

            // Keep tooltip in viewport
            if (left < 8) left = 8;
            if (left + tooltipRect.width > window.innerWidth - 8) {
                left = window.innerWidth - tooltipRect.width - 8;
            }
            if (top < 8) top = triggerRect.bottom + 8;

            setTooltipPosition({ top, left });
        }
    }, [isVisible, position]);

    if (!rule) {
        return children;
    }

    return (
        <>
            <span
                ref={triggerRef}
                onMouseEnter={() => setIsVisible(true)}
                onMouseLeave={() => setIsVisible(false)}
                onFocus={() => setIsVisible(true)}
                onBlur={() => setIsVisible(false)}
                tabIndex={0}
                className="cursor-help border-b border-dotted border-disco-muted hover:border-disco-cyan transition-colors"
            >
                {children}
            </span>

            {isVisible && (
                <div
                    ref={tooltipRef}
                    className="fixed z-[150] w-72 p-4 bg-disco-panel border border-disco-muted rounded-lg shadow-2xl backdrop-blur-sm"
                    style={{
                        top: tooltipPosition.top,
                        left: tooltipPosition.left,
                    }}
                >
                    {/* Title */}
                    <h4 className="font-serif text-lg text-disco-paper mb-2 uppercase tracking-wider">
                        {rule.title}
                    </h4>

                    {/* Description */}
                    <p className="text-disco-paper/80 text-sm mb-3">
                        {rule.description}
                    </p>

                    {/* Stat (for moves) */}
                    {rule.stat && (
                        <div className="text-xs font-mono text-disco-cyan mb-2">
                            Roll: +{rule.stat}
                        </div>
                    )}

                    {/* Outcomes (for moves) */}
                    {rule.strong_hit && (
                        <div className="space-y-1 text-xs font-mono mb-2">
                            <div className="text-disco-cyan">
                                <span className="opacity-60">Strong Hit:</span> {rule.strong_hit}
                            </div>
                            <div className="text-disco-yellow">
                                <span className="opacity-60">Weak Hit:</span> {rule.weak_hit}
                            </div>
                            <div className="text-disco-red">
                                <span className="opacity-60">Miss:</span> {rule.miss}
                            </div>
                        </div>
                    )}

                    {/* Examples */}
                    {rule.examples && (
                        <div className="mt-2 pt-2 border-t border-disco-muted/30">
                            <div className="text-[10px] text-disco-muted uppercase mb-1">Examples</div>
                            <ul className="text-xs text-disco-paper/60 space-y-0.5">
                                {rule.examples.map((ex, i) => (
                                    <li key={i}>• {ex}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Warning */}
                    {rule.warning && (
                        <div className="mt-2 p-2 bg-disco-red/10 border border-disco-red/30 rounded text-xs text-disco-red">
                            ⚠ {rule.warning}
                        </div>
                    )}

                    {/* Progress Ranks */}
                    {rule.ranks && (
                        <ul className="text-xs text-disco-paper/60 space-y-0.5">
                            {rule.ranks.map((rank, i) => (
                                <li key={i}>• {rank}</li>
                            ))}
                        </ul>
                    )}

                    {/* Momentum specifics */}
                    {rule.max && (
                        <div className="text-xs font-mono text-disco-muted mt-2">
                            Max: {rule.max} | Min: {rule.min} | Reset: {rule.reset}
                        </div>
                    )}
                </div>
            )}
        </>
    );
};

/**
 * QuickReferencePanel - Full reference panel overlay
 */
export const QuickReferencePanel = ({ isOpen, onClose }) => {
    const [activeTab, setActiveTab] = useState('moves');

    if (!isOpen) return null;

    const tabs = [
        { id: 'moves', label: 'Moves' },
        { id: 'stats', label: 'Stats' },
        { id: 'progress', label: 'Progress' },
    ];

    const moveRules = ['face_danger', 'secure_advantage', 'gather_information', 'compel'];
    const statRules = ['edge', 'heart', 'iron', 'shadow', 'wits'];
    const conditionRules = ['health', 'spirit', 'supply', 'momentum'];

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm"
            onClick={onClose}
        >
            <div
                className="bg-disco-panel border-2 border-disco-muted p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto shadow-2xl"
                onClick={e => e.stopPropagation()}
            >
                <h2 className="font-serif text-2xl text-disco-paper mb-4 text-center uppercase tracking-widest">
                    Quick Reference
                </h2>

                {/* Tabs */}
                <div className="flex gap-2 mb-6 border-b border-disco-muted/30 pb-2">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`
                                px-4 py-2 font-mono text-sm uppercase transition-colors
                                ${activeTab === tab.id
                                    ? 'text-disco-cyan border-b-2 border-disco-cyan'
                                    : 'text-disco-muted hover:text-disco-paper'
                                }
                            `}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="space-y-4">
                    {activeTab === 'moves' && moveRules.map(ruleId => {
                        const rule = RULES[ruleId];
                        return (
                            <div key={ruleId} className="p-4 bg-disco-dark/50 rounded-lg">
                                <h4 className="font-serif text-lg text-disco-paper mb-2">{rule.title}</h4>
                                <p className="text-disco-paper/80 text-sm mb-2">{rule.description}</p>
                                <div className="text-xs font-mono text-disco-cyan mb-2">Roll: +{rule.stat}</div>
                                <div className="grid grid-cols-3 gap-2 text-xs">
                                    <div className="text-disco-cyan">
                                        <div className="font-bold mb-1">Strong Hit</div>
                                        {rule.strong_hit}
                                    </div>
                                    <div className="text-disco-yellow">
                                        <div className="font-bold mb-1">Weak Hit</div>
                                        {rule.weak_hit}
                                    </div>
                                    <div className="text-disco-red">
                                        <div className="font-bold mb-1">Miss</div>
                                        {rule.miss}
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {activeTab === 'stats' && (
                        <>
                            <h3 className="font-serif text-lg text-disco-muted uppercase">Character Stats</h3>
                            <div className="grid grid-cols-2 gap-3">
                                {statRules.map(ruleId => {
                                    const rule = RULES[ruleId];
                                    return (
                                        <div key={ruleId} className="p-3 bg-disco-dark/50 rounded-lg">
                                            <h4 className="font-serif text-disco-cyan mb-1">{rule.title}</h4>
                                            <p className="text-disco-paper/80 text-xs">{rule.description}</p>
                                        </div>
                                    );
                                })}
                            </div>

                            <h3 className="font-serif text-lg text-disco-muted uppercase mt-6">Condition Meters</h3>
                            <div className="grid grid-cols-2 gap-3">
                                {conditionRules.map(ruleId => {
                                    const rule = RULES[ruleId];
                                    return (
                                        <div key={ruleId} className="p-3 bg-disco-dark/50 rounded-lg">
                                            <h4 className="font-serif text-disco-accent mb-1">{rule.title}</h4>
                                            <p className="text-disco-paper/80 text-xs">{rule.description}</p>
                                            {rule.warning && (
                                                <p className="text-disco-red text-xs mt-1">⚠ {rule.warning}</p>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </>
                    )}

                    {activeTab === 'progress' && (
                        <div className="p-4 bg-disco-dark/50 rounded-lg">
                            <h4 className="font-serif text-lg text-disco-paper mb-2">{RULES.progress.title}</h4>
                            <p className="text-disco-paper/80 text-sm mb-4">{RULES.progress.description}</p>
                            <div className="space-y-2">
                                {RULES.progress.ranks.map((rank, i) => (
                                    <div key={i} className="text-xs font-mono text-disco-paper/60">
                                        • {rank}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                <div className="mt-6 text-center">
                    <button onClick={onClose} className="btn-disco px-6 py-2">
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RuleTooltip;
