import React, { useState, useEffect } from 'react';
import api from '../utils/api';

/**
 * AreaInfoOverlay - Displays local rumors and events over the scene
 */
const AreaInfoOverlay = ({ areaId, visible = true }) => {
    const [info, setInfo] = useState({ rumors: [], events: [] });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (visible && areaId) {
            fetchAreaInfo();
        }
    }, [visible, areaId]);

    const fetchAreaInfo = async () => {
        setLoading(true);
        try {
            // New endpoint for world memory
            const data = await api.get(`/world/memory/${areaId}`);
            if (data) {
                setInfo({
                    rumors: data.rumors || [],
                    events: data.recent_events || []
                });
            }
        } catch (err) {
            console.error("Failed to fetch area info:", err);
        } finally {
            setLoading(false);
        }
    };

    if (!visible || (info.rumors.length === 0 && info.events.length === 0)) return null;

    return (
        <div className="absolute bottom-4 left-4 right-4 z-20 pointer-events-none">
            <div className="flex flex-col gap-2 items-start">

                {/* Recent Events Ticker */}
                {info.events.length > 0 && (
                    <div className="bg-black/60 backdrop-blur-sm border-l-2 border-disco-red px-3 py-1.5 rounded-r max-w-sm animate-fadeIn">
                        <div className="text-[10px] text-disco-red font-mono uppercase tracking-widest mb-0.5">
                            Recent Activity
                        </div>
                        <div className="text-xs text-disco-paper font-serif italic opacity-90">
                            {info.events[0].description}
                            <span className="text-[10px] text-disco-muted ml-2 not-italic">
                                ({new Date(info.events[0].timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})
                            </span>
                        </div>
                    </div>
                )}

                {/* Local Rumors */}
                {info.rumors.length > 0 && (
                    <div className="bg-black/60 backdrop-blur-sm border-l-2 border-disco-yellow px-3 py-1.5 rounded-r max-w-sm animate-fadeIn delay-100">
                        <div className="text-[10px] text-disco-yellow font-mono uppercase tracking-widest mb-0.5">
                            Local Chatter
                        </div>
                        <div className="text-xs text-disco-paper font-serif italic opacity-90">
                            "{info.rumors[0]}"
                        </div>
                        {info.rumors.length > 1 && (
                            <div className="text-[9px] text-disco-muted mt-1 text-right">
                                +{info.rumors.length - 1} more...
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AreaInfoOverlay;
