import React, { useState, useEffect, useCallback } from 'react';
import './PracticeCards.css';
import { useVoice } from '../contexts/VoiceContext';
import api from '../utils/api';

const PracticeCards = ({ onClose }) => {
    const [sets, setSets] = useState([]);
    const [selectedSet, setSelectedSet] = useState(null);
    const [currentCardIndex, setCurrentCardIndex] = useState(0);
    const [inSession, setInSession] = useState(false);
    const [showCreateSet, setShowCreateSet] = useState(false);
    const [showActivity, setShowActivity] = useState(null); // set_id or null
    const [progress, setProgress] = useState({});
    const [loading, setLoading] = useState(true);
    const [newSetTitle, setNewSetTitle] = useState("");
    const [newSetCards, setNewSetCards] = useState("");

    const { isListening, startListening, stopListening } = useVoice();
    const [startTime, setStartTime] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [setsData, progressData] = await Promise.all([
                api.get('/practice/sets'),
                api.get('/practice/progress')
            ]);
            setSets(setsData.sets);
            setProgress(progressData);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch practice data:", err);
            setLoading(false);
        }
    };

    const startSession = (set) => {
        setSelectedSet(set);
        setCurrentCardIndex(0);
        setInSession(true);
        setStartTime(Date.now());
    };

    const nextCard = useCallback(async () => {
        if (!selectedSet) return;

        // Track usage for current card
        const card = selectedSet.cards[currentCardIndex];
        const duration = Date.now() - startTime;

        if (duration > 1000) { // Only save if used for more than 1 second
            await api.post('/track', {
                card_id: card.id,
                is_recording: isListening,
                time_ms: duration
            });
        }

        if (currentCardIndex < selectedSet.cards.length - 1) {
            setCurrentCardIndex(prev => prev + 1);
            setStartTime(Date.now());
        } else {
            // End session
            setInSession(false);
            fetchData(); // Refresh progress
        }
    }, [selectedSet, currentCardIndex, isListening, startTime]);

    const prevCard = () => {
        if (currentCardIndex > 0) {
            setCurrentCardIndex(prev => prev - 1);
            setStartTime(Date.now());
        }
    };

    const handleToggleRecording = () => {
        if (isListening) stopListening();
        else startListening();
    };

    const handleCreateSet = async () => {
        if (!newSetTitle || !newSetCards) return;
        try {
            await api.post('/practice/sets', {
                title: newSetTitle,
                difficulty: 'beginner',
                cards: newSetCards.split('\n').filter(line => line.trim())
            });
            setShowCreateSet(false);
            setNewSetTitle("");
            setNewSetCards("");
            fetchData();
        } catch (err) {
            console.error("Failed to create set:", err);
        }
    };

    if (loading) return <div className="p-20 text-center text-disco-cyan animate-pulse">Loading Card Sets...</div>;

    if (inSession && selectedSet) {
        const currentCard = selectedSet.cards[currentCardIndex];
        return (
            <div className="practice-session-overlay">
                <div className="absolute top-8 left-8 flex items-center gap-4">
                    <button onClick={() => setInSession(false)} className="text-white/60 hover:text-white">✕ Exit Session</button>
                    <div className="h-1 w-32 bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-disco-cyan transition-all duration-300"
                            style={{ width: `${((currentCardIndex + 1) / selectedSet.cards.length) * 100}%` }}
                        />
                    </div>
                    <span className="text-xs font-mono text-white/40">{currentCardIndex + 1} / {selectedSet.cards.length}</span>
                </div>

                <div className="active-practice-card">
                    {currentCard.text}
                </div>

                <div className="practice-controls">
                    <button
                        onClick={prevCard}
                        disabled={currentCardIndex === 0}
                        className="btn-practice btn-nav disabled:opacity-30"
                    >
                        PREV
                    </button>

                    <div
                        className={`record-button-container ${isListening ? 'active' : ''}`}
                        onClick={handleToggleRecording}
                        title={isListening ? "Stop Recording" : "Start Recording"}
                    >
                        {isListening ? (
                            <div className="flex items-center justify-center">
                                <span className="text-white text-xs font-bold">REC</span>
                            </div>
                        ) : (
                            <div className="w-4 h-4 rounded-full bg-red-500" />
                        )}
                    </div>

                    <button onClick={nextCard} className="btn-practice bg-disco-cyan text-black">
                        {currentCardIndex === selectedSet.cards.length - 1 ? 'FINISH' : 'NEXT CARD'}
                    </button>
                </div>

                <div className="mt-8 text-white/30 text-sm font-serif italic">
                    {isListening ? "Recording in progress..." : "Listening paused."}
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-disco-bg p-8 pt-24 overflow-y-auto">
            <div className="max-w-6xl mx-auto">
                <div className="flex justify-between items-end mb-12 border-b border-white/10 pb-6">
                    <div>
                        <h1 className="text-4xl font-serif text-white tracking-tight">Practice Cards</h1>
                        <p className="text-slate-400 mt-2">Master your voice with structured reading material.</p>
                    </div>
                    <button
                        onClick={() => setShowCreateSet(true)}
                        className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-full text-sm font-bold transition-all"
                    >
                        + Add your own
                    </button>
                </div>

                {showCreateSet && (
                    <div className="mb-12 bg-slate-800/50 p-8 rounded-2xl border border-white/10 animate-fadeIn">
                        <h3 className="text-xl font-bold text-white mb-6">Create Custom Card Set</h3>
                        <div className="space-y-4">
                            <input
                                type="text"
                                placeholder="Set Title (e.g., My Daily Affirmations)"
                                className="w-full bg-black/40 border border-white/10 p-4 rounded-lg text-white"
                                value={newSetTitle}
                                onChange={e => setNewSetTitle(e.target.value)}
                            />
                            <textarea
                                placeholder="Enter each card text on a new line..."
                                className="w-full h-40 bg-black/40 border border-white/10 p-4 rounded-lg text-white font-serif"
                                value={newSetCards}
                                onChange={e => setNewSetCards(e.target.value)}
                            />
                            <div className="flex gap-4">
                                <button onClick={handleCreateSet} className="bg-indigo-600 px-8 py-3 rounded-lg font-bold text-white">Save Set</button>
                                <button onClick={() => setShowCreateSet(false)} className="bg-white/5 px-8 py-3 rounded-lg font-bold text-white/60">Cancel</button>
                            </div>
                        </div>
                    </div>
                )}

                {['beginner', 'intermediate', 'advanced'].map(difficulty => (
                    <div key={difficulty} className="mb-16">
                        <h2 className="text-xs font-mono uppercase tracking-[0.3em] text-white/40 mb-8 flex items-center gap-4">
                            {difficulty}
                            <div className="h-px flex-1 bg-white/5" />
                        </h2>
                        <div className="practice-grid">
                            {sets.filter(s => s.difficulty === difficulty).map(set => (
                                <div
                                    key={set.id}
                                    className={`card-set-tile difficulty-${difficulty}`}
                                    onClick={() => startSession(set)}
                                >
                                    <h3 className="card-set-title">{set.title}</h3>

                                    <div className="flex-1 flex flex-col justify-center items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <div className="text-xs font-mono bg-black/40 px-3 py-1 rounded">
                                            {progress.practice_counts?.[set.cards[0]?.id] || 0} Practices
                                        </div>
                                    </div>

                                    <div className="card-set-info">
                                        <span>{set.card_count} {set.card_count === 1 ? 'card' : 'cards'}</span>
                                        <div className="flex items-center gap-2 bg-white/20 px-3 py-1 rounded-full text-xs">
                                            Start →
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PracticeCards;
