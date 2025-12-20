import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

/**
 * SessionRecap - Shows "Previously on..." recaps and story summaries
 */
const SessionRecap = ({ isOpen, onClose, sessionId = "default" }) => {
    const [recap, setRecap] = useState(null);
    const [storySoFar, setStorySoFar] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('recap');
    const [recapStyle, setRecapStyle] = useState('dramatic');

    useEffect(() => {
        if (isOpen) {
            fetchRecap();
        }
    }, [isOpen, recapStyle]);

    const fetchRecap = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/session/recap/${sessionId}?style=${recapStyle}`);
            const data = await res.json();
            setRecap(data);
        } catch (err) {
            console.error('Failed to fetch recap:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchStorySoFar = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/session/story-so-far/${sessionId}?length=medium`);
            const data = await res.json();
            setStorySoFar(data);
        } catch (err) {
            console.error('Failed to fetch story:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        if (tab === 'story' && !storySoFar) {
            fetchStorySoFar();
        }
    };

    if (!isOpen) return null;

    const styles = [
        { id: 'dramatic', label: '🎭 Dramatic', desc: 'Epic, cinematic' },
        { id: 'noir', label: '🕵️ Noir', desc: 'Hard-boiled' },
        { id: 'mysterious', label: '🌙 Mysterious', desc: 'Atmospheric' },
        { id: 'urgent', label: '⚡ Urgent', desc: 'Action-focused' },
        { id: 'reflective', label: '💭 Reflective', desc: 'Character-focused' },
    ];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="panel-glass w-full max-w-3xl max-h-[85vh] overflow-hidden flex flex-col m-4">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-disco-muted/30">
                    <h2 className="text-2xl font-serif text-disco-paper flex items-center gap-2">
                        <span className="text-disco-accent">📜</span> Session Recap
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-paper text-2xl transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-disco-muted/30">
                    <button
                        onClick={() => handleTabChange('recap')}
                        className={`flex-1 py-3 text-sm font-mono uppercase transition-colors
                            ${activeTab === 'recap'
                                ? 'text-disco-cyan border-b-2 border-disco-cyan bg-disco-cyan/5'
                                : 'text-disco-muted hover:text-disco-paper'}`}
                    >
                        Previously On...
                    </button>
                    <button
                        onClick={() => handleTabChange('story')}
                        className={`flex-1 py-3 text-sm font-mono uppercase transition-colors
                            ${activeTab === 'story'
                                ? 'text-disco-cyan border-b-2 border-disco-cyan bg-disco-cyan/5'
                                : 'text-disco-muted hover:text-disco-paper'}`}
                    >
                        Story So Far
                    </button>
                </div>

                {/* Style Selector (for recap tab) */}
                {activeTab === 'recap' && (
                    <div className="flex gap-2 p-3 border-b border-disco-muted/20 bg-disco-bg/30 overflow-x-auto">
                        {styles.map(s => (
                            <button
                                key={s.id}
                                onClick={() => setRecapStyle(s.id)}
                                className={`flex-shrink-0 px-3 py-1.5 text-xs rounded transition-colors
                                    ${recapStyle === s.id
                                        ? 'bg-disco-cyan/20 text-disco-cyan border border-disco-cyan/50'
                                        : 'text-disco-muted hover:text-disco-paper border border-transparent'}`}
                                title={s.desc}
                            >
                                {s.label}
                            </button>
                        ))}
                    </div>
                )}

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="loading-text text-disco-cyan">
                                {activeTab === 'recap' ? 'Generating recap...' : 'Compiling story...'}
                            </div>
                        </div>
                    ) : activeTab === 'recap' ? (
                        recap ? (
                            <div className="space-y-4">
                                <div className="font-serif text-lg text-disco-paper/90 leading-relaxed whitespace-pre-wrap">
                                    {recap.recap}
                                </div>
                                {recap.session_count > 0 && (
                                    <div className="text-xs text-disco-muted mt-4 pt-4 border-t border-disco-muted/20">
                                        {recap.session_count} session{recap.session_count !== 1 ? 's' : ''} recorded
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-disco-muted">
                                <p className="text-lg">No previous sessions to recap.</p>
                                <p className="text-sm mt-2">Your story begins now...</p>
                            </div>
                        )
                    ) : (
                        storySoFar ? (
                            <div className="space-y-4">
                                <h3 className="font-serif text-xl text-disco-accent mb-4">The Story So Far</h3>
                                <div className="font-serif text-lg text-disco-paper/90 leading-relaxed">
                                    {storySoFar.summary}
                                </div>
                                {storySoFar.session_count > 0 && (
                                    <div className="text-xs text-disco-muted mt-4 pt-4 border-t border-disco-muted/20">
                                        Across {storySoFar.session_count} session{storySoFar.session_count !== 1 ? 's' : ''}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-disco-muted">
                                <p className="text-lg">No story recorded yet.</p>
                                <p className="text-sm mt-2">Play more to build your legend...</p>
                            </div>
                        )
                    )}
                </div>

                {/* Footer */}
                <div className="p-3 border-t border-disco-muted/30 flex justify-between items-center">
                    <div className="text-xs text-disco-muted">
                        Recaps are generated from your gameplay
                    </div>
                    <button
                        onClick={() => fetchRecap()}
                        className="text-xs text-disco-cyan hover:text-disco-paper transition-colors"
                        disabled={loading}
                    >
                        🔄 Regenerate
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SessionRecap;
