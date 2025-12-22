import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../utils/api';

const QuestJournal = ({ onClose, sessionId = 'default' }) => {
    const [quests, setQuests] = useState({ active: [], available: [] });
    const [loading, setLoading] = useState(true);
    const [selectedQuest, setSelectedQuest] = useState(null);
    const [filter, setFilter] = useState('active'); // active, available, completed

    useEffect(() => {
        fetchQuests();
    }, []);

    const fetchQuests = async () => {
        try {
            const data = await api.get(`/quests/list?session_id=${sessionId}`);
            setQuests(data);
        } catch (err) {
            console.error("Failed to load quests:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectQuest = async (quest) => {
        setSelectedQuest(quest);
        try {
            const detailData = await api.get(`/quests/${quest.id}?session_id=${sessionId}`);
            // Merge detail data into the selected quest state
            setSelectedQuest(prev => ({
                ...prev,
                ...detailData.quest,
                state: detailData.state,
                prerequisites_met: detailData.prerequisites_met,
                unmet_prerequisites: detailData.unmet_prerequisites
            }));
        } catch (err) {
            console.error("Failed to fetch quest details:", err);
        }
    };

    const handleStartQuest = async (questId) => {
        try {
            await api.post(`/quests/${questId}/start?session_id=${sessionId}`);
            fetchQuests();
            setSelectedQuest(null);
        } catch (err) {
            console.error("Failed to start quest:", err);
        }
    };

    if (loading) return null;

    const displayedQuests = filter === 'active' ? quests.active :
        filter === 'available' ? quests.available : [];

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm" onClick={onClose}>
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-gray-900 border border-amber-900/50 rounded-lg shadow-2xl w-full max-w-5xl h-[80vh] flex overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                {/* Left Sidebar: Quest List */}
                <div className="w-1/3 border-r border-gray-800 bg-black/40 flex flex-col">
                    <div className="p-4 border-b border-gray-800">
                        <h2 className="text-xl font-orbitron text-amber-500 tracking-wider mb-4">QUEST JOURNAL</h2>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setFilter('active')}
                                className={`flex-1 py-1 text-xs font-mono uppercase border transition-colors ${filter === 'active' ? 'bg-amber-900/20 border-amber-500 text-amber-500' : 'border-gray-700 text-gray-500 hover:text-gray-300'}`}
                            >
                                Active
                            </button>
                            <button
                                onClick={() => setFilter('available')}
                                className={`flex-1 py-1 text-xs font-mono uppercase border transition-colors ${filter === 'available' ? 'bg-amber-900/20 border-amber-500 text-amber-500' : 'border-gray-700 text-gray-500 hover:text-gray-300'}`}
                            >
                                Available
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto">
                        {displayedQuests.length > 0 ? (
                            displayedQuests.map(quest => (
                                <div
                                    key={quest.id}
                                    onClick={() => handleSelectQuest(quest)}
                                    className={`p-4 border-b border-gray-800 cursor-pointer transition-colors hover:bg-white/5 ${selectedQuest?.id === quest.id ? 'bg-white/10 border-l-4 border-l-amber-500' : 'border-l-4 border-l-transparent'}`}
                                >
                                    <div className="flex justify-between items-start mb-1">
                                        <h3 className={`font-bold ${selectedQuest?.id === quest.id ? 'text-amber-100' : 'text-gray-400'}`}>{quest.title}</h3>
                                        {quest.converges_to && <span className="text-[10px] bg-red-900/40 text-red-500 px-1.5 py-0.5 border border-red-500/30 font-bold">MILESTONE</span>}
                                    </div>
                                    <p className="text-xs text-gray-600 mt-1 line-clamp-2">{quest.description}</p>
                                    {quest.type && <span className="text-[10px] uppercase tracking-widest text-amber-700 mt-2 block">{quest.type}</span>}
                                </div>
                            ))
                        ) : (
                            <div className="p-8 text-center text-gray-600 italic">
                                No {filter} quests found.
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Content: Quest Details */}
                <div className="flex-1 bg-[url('/assets/paper-texture.png')] bg-cover relative">
                    <div className="absolute inset-0 bg-gray-900/95" /> {/* Dark overlay since we don't assume the texture exists */}

                    <div className="relative h-full p-8 overflow-y-auto">
                        {selectedQuest ? (
                            <div className="space-y-6 animate-fadeIn">
                                <div className="border-b border-gray-700 pb-4">
                                    <h1 className="text-3xl font-serif text-amber-500 mb-2">{selectedQuest.title}</h1>
                                    <div className="flex gap-4 text-xs font-mono text-gray-500 uppercase tracking-widest">
                                        <span>Phase {selectedQuest.phase}</span>
                                        <span>{selectedQuest.type || 'Side Quest'}</span>
                                    </div>
                                </div>

                                <div className="prose prose-invert prose-lg text-gray-300 leading-relaxed max-w-none">
                                    <p>{selectedQuest.description}</p>
                                </div>

                                {selectedQuest.converges_to && (
                                    <div className="p-4 bg-red-900/10 border border-red-500/20 rounded-lg">
                                        <div className="flex items-center gap-2 text-red-400 font-bold text-sm uppercase mb-1">
                                            <span className="animate-pulse">⚠️</span> CRITICAL MILESTONE
                                        </div>
                                        <p className="text-xs text-red-300/70">
                                            This quest is essential for advancing to the next story phase. Completing it will converge multiple plot threads.
                                        </p>
                                    </div>
                                )}

                                {selectedQuest.unmet_prerequisites && selectedQuest.unmet_prerequisites.length > 0 && (
                                    <div className="p-4 bg-black/40 border border-gray-700 rounded-lg">
                                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">Locked Requirements</h3>
                                        <ul className="space-y-2">
                                            {selectedQuest.unmet_prerequisites.map((unmet, i) => (
                                                <li key={i} className="flex items-center gap-2 text-sm text-gray-400">
                                                    <span className="text-red-500">✕</span> {unmet}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {filter === 'active' && (
                                    <div className="mt-8 p-6 bg-black/30 border border-gray-700 rounded-lg">
                                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Current Objectives</h3>
                                        <ul className="space-y-3">
                                            {/* We'd iterate objectives here if the backend returned granular objectives. */}
                                            <li className="flex items-start gap-3 text-amber-200/80">
                                                <span className="mt-1.5 w-1.5 h-1.5 bg-amber-500 rounded-full" />
                                                <span>{selectedQuest.current_objective || "Progress through the story to uncover your next steps."}</span>
                                            </li>
                                        </ul>
                                    </div>
                                )}

                                {filter === 'available' && (
                                    <div className="mt-8">
                                        <button
                                            onClick={() => handleStartQuest(selectedQuest.id)}
                                            className="px-6 py-3 bg-amber-700 hover:bg-amber-600 text-white font-bold rounded transition-colors shadow-lg shadow-amber-900/20"
                                        >
                                            Begin Quest
                                        </button>
                                    </div>
                                )}

                                <div className="mt-12 pt-8 border-t border-gray-800 text-xs text-gray-600 font-mono">
                                    QUEST ID: {selectedQuest.id} | RECOM. PHASE: {selectedQuest.phase}
                                </div>
                            </div>
                        ) : (
                            <div className="h-full flex flex-col items-center justify-center text-gray-600">
                                <span className="text-4xl opacity-20 mb-4">⚔️</span>
                                <p>Select a quest from the journal to view details.</p>
                            </div>
                        )}
                    </div>

                    {/* Close Button */}
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
                    >
                        ✕
                    </button>
                </div>
            </motion.div>
        </div>
    );
};

export default QuestJournal;
