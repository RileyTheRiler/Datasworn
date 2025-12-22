import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNPCCache } from '../contexts/NPCCacheContext';
import ScheduleVisualizer from './ScheduleVisualizer';
import DialogueInterface from './DialogueInterface';

/**
 * NPCHoverCard - Displays NPC info on hover over names in narrative text
 * 
 * Features:
 * - Fetches NPC data from cache or API on hover
 * - Shows portrait, trust/suspicion bars, known facts
 * - Click to expand for full character sheet modal
 * - Border color based on disposition
 * - Viewport-aware positioning
 */

const API_URL = 'http://localhost:8000/api';

// Disposition color mappings
const dispositionColors = {
    hostile: 'border-disco-red',
    suspicious: 'border-disco-yellow',
    neutral: 'border-disco-muted',
    friendly: 'border-disco-cyan',
    loyal: 'border-disco-accent'
};

const dispositionTextColors = {
    hostile: 'text-disco-red',
    suspicious: 'text-disco-yellow',
    neutral: 'text-disco-muted',
    friendly: 'text-disco-cyan',
    loyal: 'text-disco-accent'
};

const dispositionBgColors = {
    hostile: 'bg-disco-red/10',
    suspicious: 'bg-disco-yellow/10',
    neutral: 'bg-disco-muted/10',
    friendly: 'bg-disco-cyan/10',
    loyal: 'bg-disco-accent/10'
};

/**
 * Full Character Sheet Modal
 */
const NPCModal = ({ npcData, onClose, onInterrogate }) => {
    const [activeTab, setActiveTab] = useState('profile'); // 'profile' | 'schedule'
    const [showChat, setShowChat] = useState(false);

    if (!npcData) return null;

    const borderColor = dispositionColors[npcData.disposition] || 'border-disco-muted';
    const textColor = dispositionTextColors[npcData.disposition] || 'text-disco-cyan';
    const bgColor = dispositionBgColors[npcData.disposition] || 'bg-disco-muted/10';

    return (
        <div
            className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fadeIn"
            onClick={onClose}
        >
            <div
                className={`bg-disco-panel border-2 ${borderColor} rounded-lg max-w-lg w-full mx-4 max-h-[85vh] flex flex-col shadow-2xl overflow-hidden`}
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex gap-4 p-6 pb-2 shrink-0">
                    <img
                        src={npcData.image_url}
                        alt={npcData.name}
                        className="w-24 h-24 rounded border-2 border-disco-muted/50 object-cover"
                        onError={(e) => e.target.src = '/assets/defaults/portrait_placeholder.png'}
                    />
                    <div className="flex-1 min-w-0">
                        <h2 className={`text-2xl font-serif font-bold ${textColor} truncate`}>{npcData.name}</h2>
                        <p className="text-disco-muted italic truncate">{npcData.role}</p>
                        <span className={`inline-block mt-2 px-2 py-0.5 text-xs font-mono uppercase ${bgColor} ${textColor} rounded`}>
                            {npcData.disposition}
                        </span>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-paper text-2xl leading-none self-start"
                    >
                        ×
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex px-6 border-b border-white/10 shrink-0">
                    <button
                        onClick={() => setActiveTab('profile')}
                        className={`px-4 py-2 text-sm font-mono uppercase tracking-wider border-b-2 transition-colors ${activeTab === 'profile' ? 'border-disco-cyan text-disco-cyan' : 'border-transparent text-disco-muted hover:text-disco-paper'}`}
                    >
                        Profile
                    </button>
                    <button
                        onClick={() => setActiveTab('schedule')}
                        className={`px-4 py-2 text-sm font-mono uppercase tracking-wider border-b-2 transition-colors ${activeTab === 'schedule' ? 'border-disco-cyan text-disco-cyan' : 'border-transparent text-disco-muted hover:text-disco-paper'}`}
                    >
                        Schedule
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
                    {activeTab === 'profile' ? (
                        <div className="space-y-4 animate-fadeIn">
                            {/* Description */}
                            {npcData.description && (
                                <div className="p-3 bg-black/30 rounded italic text-disco-paper/80">
                                    "{npcData.description}"
                                </div>
                            )}

                            {/* Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className="flex justify-between text-xs font-mono text-disco-paper/70 mb-1">
                                        <span>Trust</span>
                                        <span>{Math.round(npcData.trust * 100)}%</span>
                                    </div>
                                    <div className="w-full bg-black/50 h-2 rounded overflow-hidden">
                                        <div
                                            className="h-full bg-disco-cyan transition-all duration-300"
                                            style={{ width: `${npcData.trust * 100}%` }}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-xs font-mono text-disco-paper/70 mb-1">
                                        <span>Suspicion</span>
                                        <span>{Math.round(npcData.suspicion * 100)}%</span>
                                    </div>
                                    <div className="w-full bg-black/50 h-2 rounded overflow-hidden">
                                        <div
                                            className="h-full bg-disco-red transition-all duration-300"
                                            style={{ width: `${npcData.suspicion * 100}%` }}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Known Facts */}
                            {npcData.known_facts?.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-mono text-disco-cyan uppercase mb-2 border-b border-disco-muted/30 pb-1">
                                        Known Facts
                                    </h3>
                                    <ul className="text-sm text-disco-paper/80 space-y-1">
                                        {npcData.known_facts.map((fact, i) => (
                                            <li key={i} className="flex items-start gap-2">
                                                <span className="text-disco-cyan">•</span>
                                                {fact}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Emotional History */}
                            {npcData.emotional_history?.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-mono text-disco-purple uppercase mb-2 border-b border-disco-muted/30 pb-1">
                                        Recent Interactions
                                    </h3>
                                    <ul className="text-xs text-disco-paper/70 space-y-1">
                                        {npcData.emotional_history.slice(-5).map((memory, i) => (
                                            <li key={i} className="flex items-start gap-2">
                                                <span className="text-disco-purple">▸</span>
                                                <span className="italic">{memory.context || memory.event_type}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="animate-fadeIn h-full">
                            <ScheduleVisualizer npcId={npcData.npc_id || npcData.name.toLowerCase().replace(' ', '_')} />
                        </div>
                    )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 p-6 pt-0 shrink-0">
                    <button
                        onClick={() => setShowChat(true)}
                        className="flex-1 px-6 py-2 bg-disco-cyan/10 border border-disco-cyan text-disco-cyan hover:bg-disco-cyan hover:text-black transition-all font-serif font-bold uppercase tracking-wider"
                    >
                        💬 Chat
                    </button>
                    {onInterrogate && (
                        <button
                            onClick={() => {
                                onInterrogate(npcData);
                                onClose();
                            }}
                            className="flex-1 px-6 py-2 border-2 border-disco-accent text-disco-accent hover:bg-disco-accent hover:text-black transition-all font-serif font-bold uppercase tracking-wider"
                        >
                            🔍 Interrogate
                        </button>
                    )}
                    <button
                        onClick={onClose}
                        className="flex-1 px-6 py-2 border border-disco-muted text-disco-muted hover:text-disco-paper hover:border-disco-paper transition-colors"
                    >
                        Close
                    </button>
                </div>

                {/* Chat Modal */}
                <DialogueInterface
                    isOpen={showChat}
                    onClose={() => setShowChat(false)}
                    npcId={npcData.npc_id || npcData.name.toLowerCase().replace(' ', '_')}
                    npcName={npcData.name}
                    npcPortrait={npcData.image_url}
                />
            </div>
        </div>
    );
};

/**
 * Main NPCHoverCard Component
 */
const NPCHoverCard = ({ name, characters = {}, onInterrogate }) => {
    const [isVisible, setIsVisible] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [npcData, setNpcData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [position, setPosition] = useState({ top: 0, left: 0 });
    const triggerRef = useRef(null);
    const tooltipRef = useRef(null);
    const hoverTimeoutRef = useRef(null);

    // Try to use cache context, fallback to local fetch
    let cacheContext = null;
    try {
        cacheContext = useNPCCache();
    } catch {
        // Context not available, will use local fetch
    }

    // Fetch NPC data (from cache or API)
    const fetchNPCData = useCallback(async () => {
        setLoading(true);
        try {
            // Try cache first
            if (cacheContext) {
                const cached = await cacheContext.getNPC(name);
                if (cached) {
                    setNpcData(cached);
                    setLoading(false);
                    return;
                }
            }

            // Fallback to direct API call
            const res = await fetch(`${API_URL}/npc/${encodeURIComponent(name)}`);
            if (res.ok) {
                const data = await res.json();
                setNpcData(data);
                // Update cache if available
                if (cacheContext) {
                    cacheContext.setNPC(name, data);
                }
            } else {
                // Fallback to local characters data
                const localNpc = Object.values(characters).find(
                    c => c.name?.toLowerCase() === name.toLowerCase()
                );
                if (localNpc) {
                    setNpcData({
                        name: localNpc.name,
                        role: localNpc.role || 'Unknown',
                        trust: localNpc.trust || 0.5,
                        suspicion: localNpc.suspicion || 0,
                        disposition: 'neutral',
                        image_url: localNpc.image_url || '/assets/defaults/portrait_placeholder.png',
                        description: localNpc.description || '',
                        known_facts: localNpc.known_facts || []
                    });
                }
            }
        } catch (err) {
            console.error('Failed to fetch NPC data:', err);
        } finally {
            setLoading(false);
        }
    }, [name, characters, cacheContext]);

    // Position tooltip
    useEffect(() => {
        if (isVisible && triggerRef.current && tooltipRef.current) {
            const triggerRect = triggerRef.current.getBoundingClientRect();
            const tooltipRect = tooltipRef.current.getBoundingClientRect();

            let top = triggerRect.top - tooltipRect.height - 8;
            let left = triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2);

            // Keep in viewport
            if (left < 8) left = 8;
            if (left + tooltipRect.width > window.innerWidth - 8) {
                left = window.innerWidth - tooltipRect.width - 8;
            }
            if (top < 8) {
                top = triggerRect.bottom + 8;
            }

            setPosition({ top, left });
        }
    }, [isVisible, npcData]);

    const handleMouseEnter = () => {
        hoverTimeoutRef.current = setTimeout(() => {
            setIsVisible(true);
            if (!npcData) {
                fetchNPCData();
            }
        }, 200);
    };

    const handleMouseLeave = () => {
        if (hoverTimeoutRef.current) {
            clearTimeout(hoverTimeoutRef.current);
        }
        setIsVisible(false);
    };

    const handleClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!npcData) {
            fetchNPCData();
        }
        setShowModal(true);
        setIsVisible(false);
    };

    const borderColor = npcData ? dispositionColors[npcData.disposition] || 'border-disco-muted' : 'border-disco-muted';
    const textColor = npcData ? dispositionTextColors[npcData.disposition] || 'text-disco-cyan' : 'text-disco-cyan';

    return (
        <>
            <span
                ref={triggerRef}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
                onClick={handleClick}
                className={`cursor-pointer border-b border-dotted ${textColor} hover:opacity-80 transition-opacity`}
                role="button"
                tabIndex={0}
                aria-label={`View info about ${name}`}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        handleClick(e);
                    }
                }}
            >
                {name}
            </span>

            {/* Hover Tooltip */}
            {isVisible && !showModal && (
                <div
                    ref={tooltipRef}
                    className={`fixed z-[150] bg-disco-panel border-2 ${borderColor} p-4 rounded shadow-2xl max-w-xs backdrop-blur-sm animate-fadeIn`}
                    style={{
                        top: position.top,
                        left: position.left,
                    }}
                    onMouseEnter={() => setIsVisible(true)}
                    onMouseLeave={handleMouseLeave}
                >
                    {loading ? (
                        <div className="flex items-center gap-2 text-disco-muted">
                            <span className="w-2 h-2 bg-disco-cyan rounded-full animate-pulse" />
                            <span className="text-sm font-mono">Loading...</span>
                        </div>
                    ) : npcData ? (
                        <>
                            {/* Header with portrait */}
                            <div className="flex gap-3 mb-3">
                                <img
                                    src={npcData.image_url}
                                    alt={npcData.name}
                                    className="w-16 h-16 rounded border border-disco-muted/50 object-cover"
                                    onError={(e) => e.target.src = '/assets/defaults/portrait_placeholder.png'}
                                />
                                <div className="flex-1">
                                    <h3 className={`text-lg font-bold ${textColor}`}>{npcData.name}</h3>
                                    <p className="text-xs text-disco-muted italic">{npcData.role}</p>
                                </div>
                            </div>

                            {/* Trust Bar */}
                            <div className="mb-2">
                                <div className="flex justify-between text-[10px] font-mono text-disco-paper/70 mb-1">
                                    <span>Trust</span>
                                    <span>{Math.round(npcData.trust * 100)}%</span>
                                </div>
                                <div className="w-full bg-black/50 h-1.5 rounded overflow-hidden">
                                    <div
                                        className="h-full bg-disco-cyan transition-all duration-300"
                                        style={{ width: `${npcData.trust * 100}%` }}
                                    />
                                </div>
                            </div>

                            {/* Suspicion Bar */}
                            <div className="mb-3">
                                <div className="flex justify-between text-[10px] font-mono text-disco-paper/70 mb-1">
                                    <span>Suspicion</span>
                                    <span>{Math.round(npcData.suspicion * 100)}%</span>
                                </div>
                                <div className="w-full bg-black/50 h-1.5 rounded overflow-hidden">
                                    <div
                                        className="h-full bg-disco-red transition-all duration-300"
                                        style={{ width: `${npcData.suspicion * 100}%` }}
                                    />
                                </div>
                            </div>

                            {/* Description */}
                            {npcData.description && (
                                <p className="text-xs text-disco-paper/80 italic mb-2 line-clamp-2">
                                    "{npcData.description}"
                                </p>
                            )}

                            {/* Known Facts */}
                            {npcData.known_facts?.length > 0 && (
                                <div className="border-t border-disco-muted/30 pt-2 mt-2">
                                    <h4 className="text-[10px] font-mono text-disco-muted uppercase mb-1">Known Facts</h4>
                                    <ul className="text-xs text-disco-paper/70 space-y-0.5">
                                        {npcData.known_facts.slice(0, 3).map((fact, i) => (
                                            <li key={i}>• {fact}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Click hint */}
                            <div className="mt-3 pt-2 border-t border-disco-muted/20 text-center">
                                <span className="text-[10px] text-disco-muted font-mono">Click for full profile</span>
                            </div>
                        </>
                    ) : (
                        <div className="text-disco-muted text-sm">
                            Unknown character: {name}
                        </div>
                    )}
                </div>
            )}

            {/* Full Modal */}
            {showModal && (
                <NPCModal
                    npcData={npcData}
                    onClose={() => setShowModal(false)}
                    onInterrogate={onInterrogate}
                />
            )}
        </>
    );
};

export default NPCHoverCard;
