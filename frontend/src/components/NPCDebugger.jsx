import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { useNPCCache } from '../contexts/NPCCacheContext';
import ScheduleVisualizer from './ScheduleVisualizer';

const NPCDebugger = ({ sessionId, visible, onClose }) => {
    const { cache } = useNPCCache();
    const [selectedNPC, setSelectedNPC] = useState(null);
    const [debugData, setDebugData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [lastUpdate, setLastUpdate] = useState(null);

    // Get list of known NPCs from cache for the dropdown
    const npcList = Object.values(cache).map(n => n.name).sort();

    // Default to first NPC if none selected
    useEffect(() => {
        if (visible && !selectedNPC && npcList.length > 0) {
            setSelectedNPC(npcList[0]);
        }
    }, [visible, npcList, selectedNPC]);

    // Fetch Debug Data
    useEffect(() => {
        let interval;

        const fetchData = async () => {
            if (!selectedNPC || !visible) return;

            // Don't set loading on poll to avoid flicker, only on first load/change
            if (!debugData || debugData.npc_id !== selectedNPC) setLoading(true);

            try {
                // Map name to ID (heuristic for now, assuming slug or exact name match by API)
                // The API expects an ID. If we only have names, we might need a lookup.
                // For this MVP, let's assume the ID is the lowercased name or handled by backend.
                // Actually, backend uses 'janus_01'. Let's see if cache has ID.
                // Cache currently stores: name, role, etc.
                // We might need to guess the ID or store it. 
                // Let's assume the backend resolves "janus" to "janus_01" or we pass "janus_01".
                // In verify script we used "janus_01".
                // Let's try passing the name, if backend fails, we might need to strictly store IDs.
                // Update: Backend server.py: cognitive_debug(npc_id: str).
                // It likely does not fuzzy match. 
                // Currently our entities in DB are "janus_01". 
                // Let's try to infer ID: lowercase + "_01" if single name? 
                // Or better, just pass the name and let's hope I updated server to handle it?
                // Checking server code... cognitive_debug uses `_ensure_npc_exists(npc_id)`.
                // If I pass "Janus", it will create/look for "Janus".
                // So passing the name directly is safer for now.

                const data = await api.get(`/cognitive/debug/${selectedNPC}?session_id=${sessionId}`);
                setDebugData(data);
                setLastUpdate(new Date().toLocaleTimeString());
            } catch (err) {
                console.error("Debugger Fetch Error:", err);
            } finally {
                setLoading(false);
            }
        };

        if (visible && selectedNPC) {
            fetchData();
            interval = setInterval(fetchData, 5000); // Poll every 5s
        }

        return () => clearInterval(interval);
    }, [visible, selectedNPC, sessionId]);

    if (!visible) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-8" onClick={onClose}>
            <div className="bg-gray-900 border border-disco-purple/50 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()}>

                {/* Header */}
                <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-gray-950">
                    <div className="flex items-center gap-4">
                        <h2 className="text-xl font-serif text-disco-purple tracking-widest flex items-center gap-2">
                            🧠 COGNITIVE ENGINE DEBUGGER
                        </h2>
                        <select
                            className="bg-gray-900 border border-gray-700 text-disco-paper px-2 py-1 rounded text-sm font-mono focus:border-disco-purple outline-none"
                            value={selectedNPC || ''}
                            onChange={(e) => {
                                setSelectedNPC(e.target.value);
                                setDebugData(null); // Clear old data
                            }}
                        >
                            <option value="" disabled>Select NPC Entity...</option>
                            {npcList.map(name => (
                                <option key={name} value={name}>{name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="flex items-center gap-4 text-xs font-mono text-gray-500">
                        {lastUpdate && <span>Last Update: {lastUpdate}</span>}
                        <button onClick={onClose} className="hover:text-white transition-colors text-xl">×</button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-auto p-0 flex divide-x divide-gray-800">

                    {/* Left: Profile & State */}
                    <div className="w-1/3 p-4 space-y-6 bg-gray-900/50 overflow-y-auto">
                        <Section title="Psych Profile">
                            {debugData?.profile ? (
                                <div className="space-y-2 text-sm">
                                    <Field label="Name" value={debugData.profile.name} />
                                    <Field label="Role" value={debugData.profile.role} />
                                    <Field label="Mood" value={debugData.profile.current_mood} highlight />
                                    <Field label="Motivation" value={debugData.profile.motivation} />
                                    <div className="mt-2">
                                        <div className="text-xs text-gray-500 mb-1">TRAITS</div>
                                        <div className="flex flex-wrap gap-1">
                                            {debugData.profile.traits?.map(t => (
                                                <span key={t} className="px-1.5 py-0.5 bg-gray-800 rounded text-xs text-disco-cyan">{t}</span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ) : <Loading />}
                        </Section>

                        <Section title="Current Schedule">
                            {/* Use new visualizer if we have an ID */}
                            {selectedNPC ? (
                                <div className="mt-2">
                                    {/* Note: NPCDebugger needs to import ScheduleVisualizer first */}
                                    {/* Since I can't import in this block, I need to add import at top */}
                                    {/* Assuming I'll add the import in next step */}
                                    <ScheduleVisualizer npcId={selectedNPC} className="text-xs" />
                                </div>
                            ) : (
                                <div className="text-xs text-gray-600 italic">No active schedule.</div>
                            )}
                        </Section>
                    </div>

                    {/* Right: Memory Stream */}
                    <div className="w-2/3 p-4 bg-black/20 overflow-y-auto">
                        <Section title="Live Memory Stream" count={debugData?.recent_memories_db?.length || 0}>
                            {loading && !debugData && <Loading />}
                            <div className="space-y-3 mt-2">
                                {debugData?.recent_memories_db?.map((mem, idx) => (
                                    <div key={idx} className="bg-gray-900 border border-gray-800 p-3 rounded hover:border-disco-cyan/30 transition-colors group">
                                        <div className="flex justify-between items-start mb-1">
                                            <span className={`text-[10px] font-mono px-1.5 rounded uppercase ${getTypeColor(mem.type)}`}>
                                                {mem.type}
                                            </span>
                                            <div className="flex gap-2 text-[10px] font-mono text-gray-500">
                                                <span>imp: <b className="text-white">{mem.importance}</b></span>
                                                <span className="opacity-50">{mem.timestamp}</span>
                                            </div>
                                        </div>
                                        <div className="text-sm text-gray-300 font-serif leading-relaxed">
                                            {mem.content || mem.summary}
                                            {/* Backend schemas differ slightly (content vs summary in retrieval), handling both */}
                                        </div>
                                        {mem.keywords && (
                                            <div className="mt-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                {mem.keywords.map(k => <span key={k} className="text-[9px] text-gray-600 px-1 border border-gray-800 rounded">{k}</span>)}
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {(!debugData?.recent_memories_db || debugData.recent_memories_db.length === 0) && (
                                    <div className="text-center py-10 text-gray-600 text-sm">No recent memories found.</div>
                                )}
                            </div>
                        </Section>
                    </div>

                </div>
            </div>
        </div>
    );
};

// UI Helpers
const Section = ({ title, children, count }) => (
    <div className="flex flex-col h-full">
        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-3 flex justify-between">
            {title}
            {count !== undefined && <span className="bg-gray-800 px-1.5 rounded text-gray-300">{count}</span>}
        </h3>
        {children}
    </div>
);

const Field = ({ label, value, highlight }) => (
    <div className="flex justify-between items-baseline border-b border-gray-800 pb-1">
        <span className="text-xs text-gray-500 uppercase">{label}</span>
        <span className={`font-mono ${highlight ? 'text-disco-cyan' : 'text-gray-300'}`}>{value}</span>
    </div>
);

const Loading = () => (
    <div className="flex gap-1 justify-center py-4">
        <div className="w-1.5 h-1.5 bg-disco-purple rounded-full animate-bounce"></div>
        <div className="w-1.5 h-1.5 bg-disco-purple rounded-full animate-bounce delay-75"></div>
        <div className="w-1.5 h-1.5 bg-disco-purple rounded-full animate-bounce delay-150"></div>
    </div>
);

const getTypeColor = (type) => {
    switch (type) {
        case 'dialogue': return 'bg-blue-900/50 text-blue-300 border border-blue-800';
        case 'observation': return 'bg-yellow-900/30 text-yellow-300 border border-yellow-800';
        case 'reflection': return 'bg-purple-900/50 text-purple-300 border border-purple-800';
        case 'fact': return 'bg-red-900/30 text-red-300 border border-red-800';
        default: return 'bg-gray-800 text-gray-400';
    }
};

export default NPCDebugger;
