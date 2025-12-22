import React, { useState, useEffect } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';
import FactionDashboard from './FactionDashboard';

const API_URL = 'http://localhost:8001/api';

const JournalModal = ({ isOpen, onClose, sessionId = 'default' }) => {
    const [activeTab, setActiveTab] = useState('journal'); // 'journal' or 'objectives'
    const [entries, setEntries] = useState([]);
    const [selectedEntry, setSelectedEntry] = useState(null);
    const [progressData, setProgressData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (isOpen) {
            fetchJournalEntries();
            fetchChapterProgress();
        }
    }, [isOpen]);

    const fetchJournalEntries = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/narrative/reyes/journal?session_id=${sessionId}`);
            if (!response.ok) {
                // If 404 or backend not ready, degrade gracefully
                console.warn('Journal entries API unavailable');
            } else {
                const data = await response.json();
                setEntries(data.entries || []);
                if (data.entries && data.entries.length > 0) {
                    setSelectedEntry(data.entries[0]);
                }
            }
        } catch (err) {
            console.error("Journal fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    const fetchChapterProgress = async () => {
        try {
            const response = await fetch(`${API_URL}/chapter/progress?session_id=${sessionId}`);
            if (response.ok) {
                const data = await response.json();
                setProgressData(data);
            }
        } catch (err) {
            console.error("Chapter progress fetch error:", err);
        }
    };

    if (!isOpen) return null;

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={onClose}
            title="Captain's Personal Log"
            defaultWidth={800}
            defaultHeight={600}
            className="bg-disco-bg flex flex-col"
        >
            {/* Tab Navigation */}
            <div className="flex border-b border-disco-muted/30 bg-black/40">
                <button
                    onClick={() => setActiveTab('journal')}
                    className={`px-6 py-3 font-mono text-xs uppercase tracking-wider transition-colors ${activeTab === 'journal'
                        ? 'bg-disco-cyan/10 text-disco-cyan border-b-2 border-disco-cyan'
                        : 'text-disco-muted hover:text-disco-paper hover:bg-white/5'
                        }`}
                >
                    Encrypted Logs
                </button>
                <button
                    onClick={() => setActiveTab('objectives')}
                    className={`px-6 py-3 font-mono text-xs uppercase tracking-wider transition-colors ${activeTab === 'objectives'
                        ? 'bg-disco-cyan/10 text-disco-cyan border-b-2 border-disco-cyan'
                        : 'text-disco-muted hover:text-disco-paper hover:bg-white/5'
                        }`}
                >
                    Current Objectives
                </button>
                <button
                    onClick={() => setActiveTab('factions')}
                    className={`px-6 py-3 font-mono text-xs uppercase tracking-wider transition-colors ${activeTab === 'factions'
                        ? 'bg-disco-cyan/10 text-disco-cyan border-b-2 border-disco-cyan'
                        : 'text-disco-muted hover:text-disco-paper hover:bg-white/5'
                        }`}
                >
                    Factions
                </button>
            </div>

            <div className="flex-1 flex overflow-hidden">
                {activeTab === 'journal' ? (
                    <>
                        {/* Left Sidebar: Entry List */}
                        <div className="w-1/3 bg-disco-dark/50 border-r border-disco-muted/30 flex flex-col">
                            <div className="flex-1 overflow-y-auto p-2 space-y-1">
                                {loading && entries.length === 0 ? (
                                    <div className="p-4 text-disco-muted text-xs font-mono animate-pulse">Decrypting...</div>
                                ) : entries.length === 0 ? (
                                    <div className="p-4 text-disco-muted text-xs font-mono italic">No entries found.</div>
                                ) : (
                                    entries.map(entry => (
                                        <button
                                            key={entry.id}
                                            onClick={() => setSelectedEntry(entry)}
                                            className={`w-full text-left p-3 rounded transition-all border ${selectedEntry?.id === entry.id
                                                ? 'bg-disco-cyan/10 border-disco-cyan text-disco-cyan'
                                                : 'bg-transparent border-transparent text-disco-paper/70 hover:bg-disco-muted/10 hover:text-disco-paper'
                                                }`}
                                        >
                                            <div className="font-mono text-xs opacity-70 mb-1">{entry.time_period || 'Unknown Date'}</div>
                                            <div className="font-bold text-sm truncate">{entry.title}</div>
                                        </button>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Right Content: Entry Details */}
                        <div className="flex-1 flex flex-col bg-black/20">
                            {selectedEntry ? (
                                <div className="flex-1 flex flex-col h-full">
                                    <div className="p-6 border-b border-disco-muted/10">
                                        <h2 className="text-2xl font-serif text-disco-paper mb-2">{selectedEntry.title}</h2>
                                        <div className="flex items-center gap-3">
                                            <span className="text-disco-cyan font-mono text-xs px-2 py-0.5 border border-disco-cyan/30 rounded">
                                                ID: {selectedEntry.id.toUpperCase()}
                                            </span>
                                            <span className="text-disco-muted font-mono text-xs">
                                                {selectedEntry.time_period}
                                            </span>
                                        </div>
                                    </div>

                                    <div className="flex-1 overflow-y-auto p-8 relative">
                                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 border-4 border-disco-muted/5 rounded-full opacity-20 pointer-events-none flex items-center justify-center">
                                            <span className="text-6xl font-black text-disco-muted/10 rotate-12">REYES</span>
                                        </div>

                                        <div className="relative z-10 font-serif text-lg leading-loose text-disco-paper/90 whitespace-pre-wrap">
                                            <TypewriterText
                                                key={selectedEntry.id}
                                                text={selectedEntry.content}
                                                baseSpeed={5}
                                                className=""
                                            />
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex-1 flex items-center justify-center text-disco-muted/50 font-mono text-sm">
                                    Select a log entry to read
                                </div>
                            )}
                        </div>
                    </>
                ) : activeTab === 'objectives' ? (
                    // Objectives Tab Content
                    <div className="flex-1 p-8 bg-black/20 overflow-y-auto">
                        {progressData ? (
                            <div className="max-w-2xl mx-auto space-y-8">
                                {/* Chapter Header */}
                                <div className="text-center pb-6 border-b border-disco-muted/20">
                                    <div className="text-disco-cyan font-mono text-xs uppercase tracking-[0.3em] mb-2">Current Operation</div>
                                    <h2 className="text-3xl font-serif font-bold text-disco-paper mb-2">{progressData.chapter_name}</h2>
                                    <p className="text-disco-muted/80 italic max-w-lg mx-auto">
                                        Complete critical objectives to advance the investigation.
                                    </p>
                                </div>

                                {/* Mission List */}
                                <div className="space-y-4">
                                    <h3 className="font-mono text-xs text-disco-muted uppercase tracking-wider mb-4">Mission Status</h3>

                                    {progressData.critical_missions.map((mission, idx) => {
                                        const isCompleted = progressData.completed_missions.includes(mission);
                                        return (
                                            <div
                                                key={idx}
                                                className={`
                                                    p-4 border rounded-lg flex items-center gap-4 transition-all
                                                    ${isCompleted
                                                        ? 'bg-disco-green/5 border-disco-green/30 opacity-70'
                                                        : 'bg-black/40 border-disco-cyan/30 shadow-lg'}
                                                `}
                                            >
                                                <div className={`
                                                    w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0
                                                    ${isCompleted ? 'border-disco-green bg-disco-green/20' : 'border-disco-muted bg-transparent'}
                                                `}>
                                                    {isCompleted && (
                                                        <svg className="w-3 h-3 text-disco-green" fill="currentColor" viewBox="0 0 20 20">
                                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                        </svg>
                                                    )}
                                                </div>
                                                <div className="flex-1">
                                                    <h4 className={`font-bold ${isCompleted ? 'text-disco-muted line-through' : 'text-disco-paper'}`}>
                                                        {mission.replace(/_/g, ' ').toUpperCase()}
                                                    </h4>
                                                </div>
                                                {isCompleted && (
                                                    <span className="text-xs font-mono text-disco-green uppercase tracking-wide">
                                                        COMPLETED
                                                    </span>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>

                                {/* Status Footer */}
                                <div className="mt-8 p-4 bg-disco-cyan/5 border border-disco-cyan/20 rounded text-center">
                                    <div className="flex justify-between items-center text-xs font-mono text-disco-cyan/80">
                                        <span>PROGRESS: {progressData.completed_missions.length} / {progressData.critical_missions.length}</span>
                                        <span className={progressData.is_complete ? "text-disco-green animate-pulse" : "text-disco-muted"}>
                                            {progressData.is_complete ? "READY TO ADVANCE" : "AWAITING COMPLETION"}
                                        </span>
                                    </div>
                                    <div className="mt-2 w-full bg-black/50 h-1.5 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-disco-cyan transition-all duration-1000 ease-out"
                                            style={{ width: `${(progressData.completed_missions.length / progressData.critical_missions.length) * 100}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-full text-disco-muted font-mono text-sm">
                                Loading objectives...
                            </div>
                        )}
                    </div>
                ) : (
                    // Factions Tab Content
                    <FactionDashboard sessionId={sessionId} />
                )}
            </div>
        </DraggableModal>
    );
};

export default JournalModal;
