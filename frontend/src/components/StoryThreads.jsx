import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const StoryThreads = ({ onClose }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/api/narrative/state')
            .then(res => res.json())
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Failed to load narrative state:", err);
                setLoading(false);
            });
    }, []);

    if (loading) return null;

    const { plants, tension, themes, active_subplots } = data || {};

    // Helper to get color for plant type
    const getTypeColor = (type) => {
        switch (type.toLowerCase()) {
            case 'promise': return 'border-blue-500 text-blue-400';
            case 'threat': return 'border-red-500 text-red-400';
            case 'mystery': return 'border-purple-500 text-purple-400';
            case 'object': return 'border-yellow-500 text-yellow-400';
            default: return 'border-gray-500 text-gray-400';
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" onClick={onClose}>
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-gray-900 border border-cyan-800/50 rounded-lg shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden flex flex-col"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="p-4 border-b border-cyan-800/30 flex justify-between items-center bg-gray-800/50">
                    <h2 className="text-xl font-orbitron text-cyan-400 tracking-wider">NARRATIVE COPROCESSOR</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
                        ✕
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-8">

                    {/* Tension Gauge */}
                    <div className="space-y-2">
                        <div className="flex justify-between text-sm text-cyan-300 font-mono">
                            <span>NARRATIVE TENSION</span>
                            <span>{Math.round((tension || 0) * 100)}%</span>
                        </div>
                        <div className="h-4 bg-gray-800 rounded-full overflow-hidden border border-gray-700 relative">
                            <motion.div
                                className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-900 via-cyan-500 to-white"
                                initial={{ width: 0 }}
                                animate={{ width: `${(tension || 0) * 100}%` }}
                                transition={{ duration: 1, ease: "easeOut" }}
                            />
                        </div>
                        <p className="text-xs text-gray-500 italic">
                            {(tension || 0) > 0.8 ? "CRITICAL FLASHPOINT IMMINENT" :
                                (tension || 0) > 0.5 ? "RISING ACTION DETECTED" : "ESTABLISHING BASELINE"}
                        </p>
                    </div>

                    {/* Active Threads Grid */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-orbitron text-cyan-300 border-b border-gray-700 pb-2">ACTIVE THREADS ({plants?.length || 0})</h3>

                        {plants && plants.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {plants.map(plant => (
                                    <div key={plant.plant_id} className={`p-4 bg-gray-800/50 border-l-4 rounded-r ${getTypeColor(plant.plant_type)}`}>
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="text-xs font-bold uppercase tracking-widest opacity-80">{plant.plant_type}</span>
                                            <span className="text-xs font-mono text-gray-500">IMPORTANCE: {Math.round(plant.importance * 10)}</span>
                                        </div>
                                        <p className="text-gray-200 font-medium leading-relaxed">"{plant.description}"</p>
                                        <div className="mt-3 flex gap-2 flex-wrap">
                                            {plant.involved_characters.map(char => (
                                                <span key={char} className="px-2 py-0.5 bg-black/40 rounded text-xs text-gray-400">{char}</span>
                                            ))}
                                            {plant.scene_introduced && (
                                                <span className="px-2 py-0.5 bg-black/40 rounded text-xs text-gray-500 ml-auto">
                                                    SCENE {plant.scene_introduced}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-600 italic border border-dashed border-gray-700 rounded-lg">
                                No active narrative threads detected.
                            </div>
                        )}
                    </div>

                    {/* Themes */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-orbitron text-cyan-300 border-b border-gray-700 pb-2">THEMATIC RESONANCE</h3>
                        <div className="flex flex-wrap gap-3">
                            {themes && themes.length > 0 ? themes.map((theme, i) => (
                                <span key={i} className="px-3 py-1 bg-cyan-900/20 border border-cyan-800/50 text-cyan-300 rounded-full text-sm font-mono">
                                    #{theme}
                                </span>
                            )) : (
                                <span className="text-gray-500 italic">Analysis pending...</span>
                            )}
                        </div>
                    </div>

                </div>
            </motion.div>
        </div>
    );
};

export default StoryThreads;
