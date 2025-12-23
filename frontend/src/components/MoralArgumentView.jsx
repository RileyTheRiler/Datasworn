import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8001/api';

const MoralArgumentView = ({ sessionId = 'default' }) => {
    const [moralData, setMoralData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMoralArgument();
    }, []);

    const fetchMoralArgument = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/narrative/moral-argument`);
            if (response.ok) {
                const data = await response.json();
                setMoralData(data);
            }
        } catch (err) {
            console.error("Moral Argument fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-disco-cyan font-mono text-sm animate-pulse">
                    Loading Moral Arc...
                </div>
            </div>
        );
    }

    if (!moralData) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-disco-muted font-mono text-sm">
                    Moral Arc data unavailable
                </div>
            </div>
        );
    }

    const getEscalationColor = (level) => {
        if (level === 1) return 'disco-yellow';
        if (level === 2) return 'disco-orange';
        return 'disco-red';
    };

    return (
        <div className="flex-1 overflow-y-auto p-8 bg-black/20">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Thematic Insight - Prominent Display */}
                <div className="bg-gradient-to-r from-disco-cyan/10 to-disco-purple/10 p-6 rounded-lg border-2 border-disco-cyan/30 shadow-lg">
                    <div className="text-disco-cyan font-mono text-xs uppercase tracking-[0.3em] mb-3 text-center">
                        Thematic Insight
                    </div>
                    <p className="text-2xl font-serif text-disco-paper text-center italic leading-relaxed">
                        "{moralData.thematic_insight}"
                    </p>
                </div>

                {/* Moral Weakness */}
                <div className="bg-black/40 p-6 rounded border border-disco-red/30">
                    <h3 className="font-mono text-xs text-disco-red uppercase tracking-wider mb-4">
                        Moral Weakness
                    </h3>
                    <div className="space-y-3">
                        <div>
                            <div className="text-disco-muted text-xs font-mono mb-1">Type</div>
                            <div className="text-disco-paper font-bold text-lg">
                                {moralData.moral_weakness?.type?.replace(/_/g, ' ').toUpperCase()}
                            </div>
                        </div>
                        <div>
                            <div className="text-disco-muted text-xs font-mono mb-1">Description</div>
                            <div className="text-disco-paper/90">
                                {moralData.moral_weakness?.description}
                            </div>
                        </div>
                        <div>
                            <div className="text-disco-muted text-xs font-mono mb-1">Root Fear</div>
                            <div className="text-disco-red/90 italic">
                                "{moralData.moral_weakness?.root_fear}"
                            </div>
                        </div>
                        <div>
                            <div className="text-disco-muted text-xs font-mono mb-1">Manifestation</div>
                            <div className="text-disco-paper/80">
                                {moralData.moral_weakness?.manifestation}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Escalation Meter */}
                <div className="bg-black/40 p-6 rounded border border-disco-muted/30">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider">
                            Moral Escalation
                        </h3>
                        <span className="text-disco-cyan font-mono text-sm">
                            Level {moralData.current_escalation_level} / 3
                        </span>
                    </div>
                    <div className="flex gap-2">
                        {[1, 2, 3].map(level => (
                            <div
                                key={level}
                                className={`flex-1 h-3 rounded transition-all ${level <= moralData.current_escalation_level
                                        ? `bg-${getEscalationColor(level)}`
                                        : 'bg-disco-muted/20'
                                    }`}
                            />
                        ))}
                    </div>
                </div>

                {/* First Immoral Act */}
                <div className="bg-disco-yellow/5 p-6 rounded border-l-4 border-disco-yellow">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="bg-disco-yellow/20 text-disco-yellow px-2 py-1 rounded text-xs font-mono font-bold">
                            LEVEL 1
                        </span>
                        <h3 className="font-mono text-xs text-disco-yellow uppercase tracking-wider">
                            First Immoral Act (Scene {moralData.first_immoral_act?.scene})
                        </h3>
                    </div>
                    <div className="space-y-3">
                        <div>
                            <div className="text-disco-muted text-xs font-mono mb-1">Action</div>
                            <div className="text-disco-paper/90">
                                {moralData.first_immoral_act?.description}
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-disco-muted text-xs font-mono mb-1">Justification</div>
                                <div className="text-disco-yellow/80 italic text-sm">
                                    "{moralData.first_immoral_act?.justification}"
                                </div>
                            </div>
                            <div>
                                <div className="text-disco-muted text-xs font-mono mb-1">Actual Harm</div>
                                <div className="text-disco-red/80 text-sm">
                                    {moralData.first_immoral_act?.harm}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Escalating Choices */}
                {moralData.immoral_choices?.map((choice, idx) => (
                    <div
                        key={idx}
                        className={`bg-${getEscalationColor(choice.escalation_level)}/5 p-6 rounded border-l-4 border-${getEscalationColor(choice.escalation_level)}`}
                    >
                        <div className="flex items-center gap-2 mb-3">
                            <span className={`bg-${getEscalationColor(choice.escalation_level)}/20 text-${getEscalationColor(choice.escalation_level)} px-2 py-1 rounded text-xs font-mono font-bold`}>
                                LEVEL {choice.escalation_level}
                            </span>
                            <h3 className={`font-mono text-xs text-${getEscalationColor(choice.escalation_level)} uppercase tracking-wider`}>
                                Escalation {idx + 1} (Scene {choice.scene})
                            </h3>
                        </div>
                        <div className="space-y-3">
                            <div>
                                <div className="text-disco-muted text-xs font-mono mb-1">Action</div>
                                <div className="text-disco-paper/90">
                                    {choice.description}
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className="text-disco-muted text-xs font-mono mb-1">Justification</div>
                                    <div className={`text-${getEscalationColor(choice.escalation_level)}/80 italic text-sm`}>
                                        "{choice.justification}"
                                    </div>
                                </div>
                                <div>
                                    <div className="text-disco-muted text-xs font-mono mb-1">Actual Harm</div>
                                    <div className="text-disco-red/80 text-sm">
                                        {choice.harm}
                                    </div>
                                </div>
                            </div>
                            {choice.witnesses && choice.witnesses.length > 0 && (
                                <div>
                                    <div className="text-disco-muted text-xs font-mono mb-1">Witnesses</div>
                                    <div className="flex gap-2">
                                        {choice.witnesses.map((witness, widx) => (
                                            <span
                                                key={widx}
                                                className="px-2 py-1 bg-disco-muted/10 border border-disco-muted/30 rounded text-disco-muted text-xs"
                                            >
                                                {witness}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {/* Ally Criticisms */}
                {moralData.ally_criticisms && moralData.ally_criticisms.length > 0 && (
                    <div className="bg-black/40 p-6 rounded border border-disco-cyan/30">
                        <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider mb-4">
                            Ally Criticism
                        </h3>
                        <div className="space-y-4">
                            {moralData.ally_criticisms.map((criticism, idx) => (
                                <div key={idx} className="bg-disco-cyan/5 p-4 rounded border-l-2 border-disco-cyan">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="font-bold text-disco-cyan">{criticism.ally}</span>
                                        <span className="text-xs font-mono text-disco-muted">
                                            Scene {criticism.scene}
                                        </span>
                                    </div>
                                    <div className="mb-2">
                                        <div className="text-disco-muted text-xs font-mono mb-1">Value Defended</div>
                                        <div className="text-disco-cyan uppercase text-sm font-bold">
                                            {criticism.value}
                                        </div>
                                    </div>
                                    <div className="mb-2">
                                        <div className="text-disco-muted text-xs font-mono mb-1">Criticism</div>
                                        <div className="text-disco-paper/90 italic">
                                            "{criticism.criticism}"
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-disco-muted text-xs font-mono mb-1">Why It Stings</div>
                                        <div className="text-disco-red/80 text-sm">
                                            {criticism.why_it_stings}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Competing Values */}
                {moralData.competing_values && moralData.competing_values.length > 0 && (
                    <div className="bg-black/40 p-6 rounded border border-disco-muted/30">
                        <h3 className="font-mono text-xs text-disco-cyan uppercase tracking-wider mb-3">
                            Competing Values
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {moralData.competing_values.map((value, idx) => (
                                <span
                                    key={idx}
                                    className="px-4 py-2 bg-disco-purple/10 border border-disco-purple/30 rounded text-disco-purple font-mono uppercase text-sm"
                                >
                                    {value}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MoralArgumentView;
