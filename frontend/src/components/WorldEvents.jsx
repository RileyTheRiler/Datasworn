import React, { useState, useEffect } from 'react';
import './WorldEvents.css';

const WorldEvents = ({ sessionId }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const response = await fetch(`/api/world/simulation/events/${sessionId}`);
                if (response.ok) {
                    const data = await response.json();
                    setEvents(data.events.reverse()); // Show newest first
                }
            } catch (error) {
                console.error("Error fetching world events:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchEvents();

        // Polling for updates every minute
        const interval = setInterval(fetchEvents, 10000); // Poll every 10s for more responsive updates
        return () => clearInterval(interval);
    }, [sessionId]);

    const getEventIcon = (type) => {
        // Handle both simple strings and strings that might contain the type
        const t = type.toLowerCase();

        if (t.includes('traffic')) return '🚀';
        if (t.includes('patrol')) return '🚨';
        if (t.includes('crime') || t.includes('suspicion')) return '🕵️';
        if (t.includes('pursuit') || t.includes('blockade')) return '🚔';
        if (t.includes('wildlife') || t.includes('predator') || t.includes('prey')) return '🐾';
        if (t.includes('weather') || t.includes('hazard')) return '⚡';

        switch (t) {
            case 'faction_update': return '⚖️';
            case 'faction_war': return '⚔️';
            case 'faction_peace': return '🕊️';
            case 'faction_expansion': return '🚩';
            case 'faction_contraction': return '📉';
            case 'npc_birth': return '👶';
            case 'npc_death': return '💀';
            case 'discovery': return '🔭';
            case 'crisis': return '⚠️';
            case 'distress_signal': return '🆘';
            case 'npc_witnessed': return '👁️';
            default: return '📢';
        }
    };

    if (loading) return <div className="world-events-loading">Monitoring subspace transmissions...</div>;

    return (
        <div className="world-events-container">
            <h3 className="world-events-title">Sector Intelligence Log</h3>
            <div className="world-events-list">
                {events.length === 0 ? (
                    <div className="no-events">No significant sector developments reported.</div>
                ) : (
                    events.map(event => (
                        <div key={event.id} className={`world-event-item ${event.event_type}`}>
                            <div className="event-icon">{getEventIcon(event.event_type)}</div>
                            <div className="event-details">
                                <div className="event-header">
                                    <span className="event-type">{event.event_type.replace('_', ' ')}</span>
                                    <span className="event-timestamp">
                                        {new Date(event.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                                <div className="event-description">{event.description}</div>
                                <div className="event-location">📍 {event.location}</div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default WorldEvents;
