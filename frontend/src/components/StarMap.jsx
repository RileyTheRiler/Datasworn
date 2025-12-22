import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import DraggableModal from './DraggableModal';

const StarMap = ({ sessionId, visible, onClose }) => {
    const [systems, setSystems] = useState([]);
    const [lockedRegions, setLockedRegions] = useState({}); // Map of region_id -> reason
    const [loading, setLoading] = useState(false);
    const [currentSector, setCurrentSector] = useState("The Forge");
    const [error, setError] = useState(null);

    useEffect(() => {
        if (visible) {
            fetchNearby();
            fetchRegionLocks();
        }
    }, [visible]);

    const fetchRegionLocks = async () => {
        try {
            const data = await api.get(`/chapter/regions?session_id=${sessionId}`);
            // Transform locked list into a map for easier lookup
            const locks = {};
            if (data.locked) {
                data.locked.forEach(region => {
                    locks[region.id] = region.reason || "Region Locked";
                });
            }
            setLockedRegions(locks);
        } catch (err) {
            console.error("Failed to fetch region locks:", err);
        }
    };

    const fetchNearby = async () => {
        setLoading(true);
        setError(null);
        try {
            // Check if we need to generate first
            const data = await api.get(`/starmap/nearby/${sessionId}?count=10`);
            if (data.systems && data.systems.length > 0) {
                setSystems(data.systems);
            } else {
                // Auto-generate if empty
                await api.post(`/starmap/generate?session_id=${sessionId}&sector_name=${currentSector}`);
                const newData = await api.get(`/starmap/nearby/${sessionId}?count=10`);
                setSystems(newData.systems || []);
            }
        } catch (err) {
            console.error("Failed to fetch systems:", err);
            setError("Navigation systems offline.");
        } finally {
            setLoading(false);
        }
    };

    const handleTravel = async (system) => {
        // Check locks first
        // Systems are grouped by region ID in backend, but for MVP we might map system names or properties
        // For now, let's assume 'region_id' or 'sector' property matches our chapter regions
        // If system doesn't have explicit region_id, we might check its name or tags

        // Simpler approach: Check if system ID or Name matches any locked region keywords
        // Or if the backend adds 'region_id' to system data. 
        // Let's assume the 'system.id' or 'system.region' corresponds to our lockable regions.

        // Since we don't have explicit region mapping in starmap yet, 
        // we'll try to match exact IDs or assume all these systems are in 'local_sector' or 'frontier_worlds'
        // based on tags/name. 

        // Fallback: If 'frontier_worlds' is locked, and this system looks frontier-like...
        // For accurate behavior, backend starmap generation should arguably tag systems with region_id.
        // But for this MVP integration:
        const systemRegion = system.region_id || "local_sector";

        if (lockedRegions[systemRegion]) {
            // Shake effect or sound?
            return; // Locked
        }

        setLoading(true);
        try {
            const result = await api.post('/starmap/travel', {
                session_id: sessionId,
                system_id: system.id
            });

            if (result.success) {
                onClose();
                // Ideally trigger a toast or notification here
            }
        } catch (err) {
            console.error("Travel failed:", err);
        } finally {
            setLoading(false);
        }
    };

    // Helper to determine if a system is locked
    const getLockReason = (system) => {
        const region = system.region_id || "local_sector";
        // Special case for outer rim / frontier based on keywords for demo
        if (system.name.includes("Outer") || system.tags?.includes("Frontier")) {
            return lockedRegions["outer_rim"] || lockedRegions["frontier_worlds"];
        }
        return lockedRegions[region];
    };

    return (
        <DraggableModal
            isOpen={visible}
            onClose={onClose}
            title="🌌 Star Map"
            defaultWidth={900}
            defaultHeight={600}
            className="p-6"
        >
            {/* Sector Info */}
            <div className="mb-6 border-b border-disco-cyan/30 pb-4 flex justify-between items-end">
                <div>
                    <p className="text-disco-paper/60 font-mono text-xs uppercase tracking-[0.2em]">Sector: {currentSector}</p>
                    {Object.keys(lockedRegions).length > 0 && (
                        <p className="text-disco-red font-mono text-[10px] animate-pulse mt-1">
                            ⚠ NAVIGATIONAL HAZARDS DETECTED
                        </p>
                    )}
                </div>
                <div className="text-right">
                    <button
                        onClick={() => { fetchNearby(); fetchRegionLocks(); }}
                        className="text-disco-cyan hover:text-white text-xs font-mono border border-disco-cyan/30 px-2 py-1 rounded hover:bg-disco-cyan/10 transition-colors"
                    >
                        REFRESH SENSORS
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="h-64 flex flex-col items-center justify-center gap-4">
                    <div className="w-12 h-12 border-2 border-disco-cyan border-t-transparent rounded-full animate-spin" />
                    <span className="text-disco-cyan font-mono animate-pulse">Calculating Trajectories...</span>
                </div>
            ) : error ? (
                <div className="h-full flex items-center justify-center text-disco-red font-mono">
                    {error}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-12">
                    {systems.map(system => {
                        const lockReason = getLockReason(system);
                        const isLocked = !!lockReason;

                        return (
                            <div
                                key={system.id}
                                className={`
                                group relative p-4 border transition-all duration-300 overflow-hidden
                                ${isLocked
                                        ? 'bg-red-900/10 border-red-900/30 opacity-70 cursor-not-allowed grayscale-[0.5]'
                                        : system.discovered
                                            ? 'bg-disco-cyan/5 border-disco-cyan hover:bg-disco-cyan/10 cursor-pointer'
                                            : 'bg-black/40 border-disco-muted/50 hover:border-disco-muted cursor-pointer'
                                    }
                            `}
                                onClick={() => !isLocked && handleTravel(system)}
                            >
                                {/* Background Grid Effect */}
                                <div className={`absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] ${isLocked ? 'from-red-500/50' : 'from-disco-cyan/50'} to-transparent group-hover:opacity-20 transition-opacity`} />

                                {/* Locked Overlay Pattern */}
                                {isLocked && (
                                    <div className="absolute inset-0 bg-[url('/assets/patterns/diagonal-stripes.png')] opacity-10 pointer-events-none" />
                                )}

                                <div className="relative z-10 flex justify-between items-start">
                                    <h3 className={`text-xl font-bold transition-colors ${isLocked ? 'text-red-400/80' : 'text-disco-paper group-hover:text-disco-cyan'}`}>
                                        {system.name}
                                    </h3>
                                    {system.has_station && (
                                        <span className="text-xs px-1.5 py-0.5 border border-disco-accent text-disco-accent rounded bg-disco-accent/10">
                                            STATION
                                        </span>
                                    )}
                                    {isLocked && (
                                        <span className="text-[10px] px-1.5 py-0.5 border border-red-500 text-red-500 rounded bg-red-500/10 font-mono animate-pulse">
                                            LOCKED
                                        </span>
                                    )}
                                </div>

                                <div className="relative z-10 mt-3 space-y-1 font-mono text-xs text-disco-paper/70">
                                    <div className="flex justify-between">
                                        <span>Type:</span>
                                        <span className="text-disco-cyan">{system.star_type}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Planets:</span>
                                        <span>{system.planets}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Danger:</span>
                                        <span className={system.danger_level > 0.7 ? "text-disco-red" : "text-disco-green"}>
                                            {Math.round(system.danger_level * 100)}%
                                        </span>
                                    </div>
                                    {system.controlling_faction && (
                                        <div className="flex justify-between">
                                            <span>Control:</span>
                                            <span className="text-disco-accent">{system.controlling_faction.replace('_', ' ').toUpperCase()}</span>
                                        </div>
                                    )}
                                    {system.hazard && (
                                        <div className="mt-2 p-1.5 bg-disco-red/10 border border-disco-red/30 rounded text-disco-red animate-pulse flex items-center gap-1">
                                            <span className="text-[10px]">⚠️ HAZARD: {system.hazard.name.toUpperCase()}</span>
                                        </div>
                                    )}

                                    {/* Lock Reason Display */}
                                    {isLocked && (
                                        <div className="mt-3 p-2 bg-red-950/40 border border-red-900/50 rounded text-red-400 text-[10px] leading-tight flex items-start gap-2">
                                            <span className="text-base">⛔</span>
                                            <span>{lockReason.toUpperCase()}</span>
                                        </div>
                                    )}
                                </div>

                                {/* Resource Tags - Hide if locked to reduce clutter? Or keep visible? Keeping visible. */}
                                {system.resources && system.resources.length > 0 && !isLocked && (
                                    <div className="relative z-10 mt-4 flex flex-wrap gap-1">
                                        {system.resources.map(res => (
                                            <span key={res} className="text-[10px] px-1.5 py-0.5 bg-black/50 border border-disco-muted/30 rounded text-disco-muted">
                                                {res}
                                            </span>
                                        ))}
                                    </div>
                                )}

                                {/* Hover "Travel" Indicator */}
                                {!isLocked && (
                                    <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity transform translate-y-2 group-hover:translate-y-0 text-disco-accent font-bold text-xs uppercase tracking-widest">
                                        ENGAGE &gt;&gt;
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            )}

            <div className="mt-6 pt-4 border-t border-disco-muted/20 flex justify-between items-center text-xs text-disco-muted font-mono">
                <span>Targeting System Online</span>
                <div className="flex gap-4">
                    <span>FUEL: OPTIMAL</span>
                    <span>HYPERDRIVE: {Object.keys(lockedRegions).length > 0 ? 'RESTRICTED' : 'READY'}</span>
                </div>
            </div>
        </DraggableModal>
    );
};

export default StarMap;
