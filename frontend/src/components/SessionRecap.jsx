import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000/api';

/**
 * SessionRecap - Shows "Previously on..." recaps and story summaries
 */
const SessionRecap = ({ isOpen, onClose, sessionId = "default", defaultTab = 'what', focusSection = '' }) => {
    const [recap, setRecap] = useState(null);
    const [storySoFar, setStorySoFar] = useState(null);
    const [digest, setDigest] = useState(null);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState(defaultTab);
    const [recapStyle, setRecapStyle] = useState('dramatic');

    useEffect(() => {
        if (isOpen) {
            setActiveTab(defaultTab);
            fetchDigest();
            fetchRecap();
        }
    }, [isOpen, recapStyle, defaultTab]);

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

    const fetchDigest = async () => {
        try {
            const res = await fetch(`${API_URL}/session/what-happened/${sessionId}`);
            const data = await res.json();
            setDigest(data);
        } catch (err) {
            console.error('Failed to fetch digest:', err);
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
        if (tab === 'recap' && !recap) {
            fetchRecap();
        }
        if (tab === 'what' && !digest) {
            fetchDigest();
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
                        onClick={() => handleTabChange('what')}
                        className={`flex-1 py-3 text-sm font-mono uppercase transition-colors
                            ${activeTab === 'what'
                                ? 'text-disco-cyan border-b-2 border-disco-cyan bg-disco-cyan/5'
                                : 'text-disco-muted hover:text-disco-paper'}`}
                    >
                        What Happened?
                    </button>
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
                    ) : activeTab === 'what' ? (
                        digest ? (
                            <div className="space-y-6">
                                <div className="font-serif text-lg text-disco-paper/90 leading-relaxed whitespace-pre-wrap">
                                    {digest.recap}
                                </div>
                                {digest.highlights?.length > 0 && (
                                    <div>
                                        <div className="text-xs uppercase font-mono text-disco-muted tracking-[0.2em] mb-2">Memory captures</div>
                                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                            {digest.highlights.map((h) => (
                                                <div key={h.id} className="bg-disco-dark border border-disco-cyan/30 rounded p-3">
                                                    <div className="text-sm font-serif text-disco-paper/90">{h.caption}</div>
                                                    <div className="text-[10px] font-mono text-disco-muted mt-1">{new Date(h.timestamp).toLocaleString()}</div>
                                                    <div className="flex flex-wrap gap-1 mt-2">
                                                        {h.tags?.slice(0, 3).map((tag, idx) => (
                                                            <span key={idx} className="px-2 py-0.5 bg-disco-cyan/10 border border-disco-cyan/30 text-[10px] uppercase text-disco-cyan rounded">
                                                                {tag}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {digest.memory && (
                                    <div className="bg-disco-panel/40 border border-disco-muted/30 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="font-serif text-disco-accent text-lg">Memory log</h4>
                                            {focusSection === 'memory' && <span className="text-[10px] uppercase text-disco-cyan">Focused</span>}
                                        </div>
                                        <div className="text-sm text-disco-paper/80 space-y-2">
                                            {digest.memory.recent_summaries?.map((s, idx) => (
                                                <div key={idx}>• {s}</div>
                                            ))}
                                            {digest.memory.recent_decisions?.map((d, idx) => (
                                                <div key={`d-${idx}`}>• Decision: {d}</div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                                {digest.vows?.length > 0 && (
                                    <div className="bg-disco-panel/40 border border-disco-muted/30 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="font-serif text-disco-accent text-lg">Vows</h4>
                                            {focusSection === 'vows' && <span className="text-[10px] uppercase text-disco-cyan">Focused</span>}
                                        </div>
                                        <div className="space-y-2">
                                            {digest.vows.map((vow) => (
                                                <div key={vow.name} className="flex items-center justify-between text-sm text-disco-paper/80">
                                                    <div>
                                                        <div className="font-serif">{vow.name}</div>
                                                        <div className="text-[10px] uppercase text-disco-muted">{vow.rank}</div>
                                                    </div>
                                                    <div className="font-mono text-disco-cyan">{vow.progress}</div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-12 text-disco-muted">
                                <p className="text-lg">No highlights recorded yet.</p>
                                <p className="text-sm mt-2">Play a scene or capture a moment to seed the recap.</p>
                            </div>
                        )
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
