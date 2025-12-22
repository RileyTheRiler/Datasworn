import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../utils/api';

const QuestTracker = ({ sessionId = 'default' }) => {
    const [activeQuests, setActiveQuests] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchQuests = async () => {
            try {
                const data = await api.get(`/quests/list?session_id=${sessionId}`);
                setActiveQuests(data.active || []);
            } catch (err) {
                console.error("Failed to load active quests:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchQuests();

        // Poll for updates every 10 seconds
        const interval = setInterval(fetchQuests, 10000);
        return () => clearInterval(interval);
    }, [sessionId]);

    if (loading || activeQuests.length === 0) return null;

    return (
        <div className="absolute top-24 left-8 z-40 max-w-sm pointer-events-none">
            <div className="space-y-4">
                <AnimatePresence>
                    {activeQuests.map(quest => (
                        <motion.div
                            key={quest.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className={`
                                bg-black/80 backdrop-blur-md border-l-4 p-4 pointer-events-auto shadow-2xl transition-all duration-500
                                ${quest.converges_to
                                    ? 'border-red-600 shadow-[0_0_15px_rgba(220,38,38,0.2)] animate-[pulse_3s_infinite]'
                                    : 'border-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.1)]'}
                            `}
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <h4 className={`font-bold font-serif text-sm uppercase tracking-widest ${quest.converges_to ? 'text-red-400' : 'text-amber-400'}`}>
                                    {quest.title}
                                </h4>
                                {quest.converges_to && (
                                    <span className="text-[9px] bg-red-600 text-white px-1 font-bold animate-pulse">CRITICAL</span>
                                )}
                            </div>

                            <div className="flex items-start gap-2 text-white/90">
                                <span className={`mt-2 w-1.5 h-1.5 rounded-full flex-shrink-0 ${quest.converges_to ? 'bg-red-500' : 'bg-amber-500'}`} />
                                <span className="text-xs italic leading-tight">
                                    {quest.current_objective || "Mission active. Awaiting tactical developments."}
                                </span>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default QuestTracker;
