import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

const SkillCheck = ({ stat, statName, character, onRollComplete, onClose }) => {
    const [odds, setOdds] = useState(null);
    const [rolling, setRolling] = useState(false);
    const [result, setResult] = useState(null);

    useEffect(() => {
        // Fetch odds when component mounts
        const fetchOdds = async () => {
            try {
                const res = await fetch(`${API_URL}/roll/calculate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ stat: stat, adds: 0 })
                });
                const data = await res.json();
                setOdds(data);
            } catch (err) {
                console.error("Failed to fetch odds", err);
            }
        };
        fetchOdds();
    }, [stat]);

    const handleRoll = async () => {
        setRolling(true);
        try {
            // Commit the roll
            // We need session_id, here passed via props or context? 
            // For MVP assuming parent handles the actual API call or we pass session_id down.
            // Let's assume parent passed a callback `onCommit` that returns the result.
            // Actually, let's implement the fetch here for self-containment if we have session_id.
            // But we don't have session_id prop yet. Let's make the parent pass the result future.

            const res = await onRollComplete(); // This should return the JSON from /api/roll/commit

            // Mock delay for tension
            setTimeout(() => {
                setResult(res.roll);
                setRolling(false);
                // Auto close after result?
                setTimeout(() => onClose(), 3000);
            }, 1500);

        } catch (err) {
            console.error("Roll failed", err);
            setRolling(false);
        }
    };

    if (!odds) return null;

    const successChance = Math.round((odds.strong_hit + odds.weak_hit) * 100);

    return (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
            <div className={`
                relative bg-disco-panel border-2 p-8 w-[500px] shadow-2xl overflow-hidden
                ${result ? (
                    result.result === 'Strong Hit' ? 'border-disco-accent' :
                        result.result === 'Weak Hit' ? 'border-disco-yellow' :
                            'border-disco-red'
                ) : 'border-disco-paper'}
            `}>
                {/* Header */}
                <div className="text-center mb-8">
                    <h2 className="font-serif text-3xl text-disco-paper uppercase tracking-widest mb-1 text-glow">
                        {result ? result.result : "Skill Check"}
                    </h2>
                    <div className="font-mono text-disco-cyan text-sm uppercase">Checking {statName} [{stat}]</div>
                </div>

                {/* Main Visual */}
                <div className="flex justify-center items-center mb-8 relative h-32">
                    {rolling ? (
                        <div className="animate-spin text-disco-accent text-6xl font-serif">🎲</div>
                    ) : result ? (
                        <div className={`text-5xl font-mono font-bold ${result.result === 'Miss' ? 'text-disco-red' : 'text-disco-paper'
                            }`}>
                            {result.action_score} vs {result.challenge_dice[0]}/{result.challenge_dice[1]}
                        </div>
                    ) : (
                        <div className="relative w-32 h-32 flex items-center justify-center border-4 border-disco-muted/30 rounded-full">
                            <div className="text-4xl font-serif font-bold text-white">{successChance}%</div>
                            <div className="absolute inset-0 border-4 border-disco-paper rounded-full opacity-20"></div>
                            {/* Simple visual gauge logic would go here */}
                        </div>
                    )}
                </div>

                {/* Footer / Button */}
                {!result && !rolling && (
                    <div className="text-center">
                        <button
                            onClick={handleRoll}
                            className="btn-disco w-full py-4 text-xl bg-disco-red/20 hover:bg-disco-red/40 border-disco-red hover:border-disco-paper"
                        >
                            Roll Dice [1d6 + {stat}]
                        </button>
                        <div className="mt-4 flex justify-between text-xs font-mono text-disco-muted uppercase">
                            <span>Strong Hit: {Math.round(odds.strong_hit * 100)}%</span>
                            <span>Weak Hit: {Math.round(odds.weak_hit * 100)}%</span>
                            <span>Miss: {Math.round(odds.miss * 100)}%</span>
                        </div>
                    </div>
                )}

                {/* Close Button if stuck */}
                <button onClick={onClose} className="absolute top-2 right-2 text-disco-muted hover:text-white">✕</button>
            </div>
        </div>
    );
};

export default SkillCheck;
