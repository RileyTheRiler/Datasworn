import React, { useState, useEffect } from 'react';

const CalibrationStep = ({ sessionId, onComplete }) => {
    const [scenario, setScenario] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/api/calibration/scenario')
            .then(res => res.json())
            .then(data => {
                // Backend returns a single scenario object currently
                // We wrap it in an array to support future multi-step calibration
                const scenarios = Array.isArray(data) ? data : [data];
                setScenario(scenarios);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load calibration:", err);
                setLoading(false);
            });
    }, []);

    const handleChoice = async (choiceId) => {
        try {
            const res = await fetch('http://localhost:8000/api/calibrate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    choice_id: choiceId
                })
            });

            if (res.ok) {
                if (currentIndex < scenario.length - 1) {
                    setCurrentIndex(currentIndex + 1);
                } else {
                    onComplete(); // All questions answered
                }
            }
        } catch (err) {
            console.error("Calibration failed:", err);
        }
    };

    if (loading) return <div className="text-cyan-500 animate-pulse">Initializing Psyche Scan...</div>;
    if (!scenario || scenario.length === 0) return null;

    const currentQuestion = scenario[currentIndex];

    return (
        <div className="space-y-6 animate-fadeIn">
            <div className="text-center space-y-2">
                <h3 className="text-xl font-bold text-cyan-400 uppercase tracking-widest">
                    Psychological Calibration
                </h3>
                <p className="text-slate-400 italic">
                    {currentIndex + 1} / {scenario.length}
                </p>
            </div>

            <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-700">
                <p className="text-lg text-slate-200 mb-6 font-serif leading-relaxed">
                    {currentQuestion.description || currentQuestion.text}
                </p>

                <div className="space-y-3">
                    {currentQuestion.choices.map((choice) => (
                        <button
                            key={choice.id}
                            onClick={() => handleChoice(choice.id)}
                            className="w-full text-left p-4 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-500/50 transition-all group"
                        >
                            <span className="text-slate-300 group-hover:text-cyan-300 transition-colors">
                                {choice.text}
                            </span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default CalibrationStep;
