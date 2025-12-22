import React, { useState, useEffect, useCallback } from 'react';
import { useAccessibility } from '../contexts/AccessibilityContext';
import { useSoundEffects } from '../contexts/SoundEffectsContext';
import api from '../utils/api';
import './CampStyles.css';

// --- Subcomponents ---

const CampZone = ({ zone, activities, onInteract, onAffordance }) => {
    return (
        <div className="camp-zone">
            <h3>{zone.name}</h3>
            <p className="description">{zone.description || "A quiet spot in the camp."}</p>

            <div className="camp-spots">
                {/* Interaction Spots (Affordances) */}
                {zone.interaction_spots && zone.interaction_spots.map(spot => (
                    <div
                        key={spot.id}
                        className={`spot-marker ${spot.occupied ? 'occupied' : ''}`}
                        onClick={() => !spot.occupied && onAffordance(spot.id, spot.type)}
                        title={`${spot.type} (${spot.current_occupants}/${spot.max_occupancy})`}
                    >
                        {getSpotIcon(spot.type)} {spot.id.split('_').pop()}
                    </div>
                ))}
            </div>

            <div className="camp-occupants mt-4">
                {activities.map(act => (
                    <NPCAvatar
                        key={act.npc_id}
                        npcId={act.npc_id}
                        activity={act}
                        onInteract={() => onInteract(act.npc_id)}
                    />
                ))}
            </div>
        </div>
    );
};

const NPCAvatar = ({ npcId, activity, onInteract }) => {
    const statusColor = getStatusColor(activity.intent);

    // Placeholder avatar images - replace with real assets later
    const avatarUrl = `/assets/avatars/${npcId}.png`;

    return (
        <div className="npc-container" onClick={onInteract}>
            <div
                className="npc-avatar"
                style={{ backgroundImage: `url(${avatarUrl}), url(/assets/defaults/avatar_placeholder.png)` }}
            >
                <div className={`npc-status ${statusColor}`} />
            </div>

            <div className="npc-activity-tooltip">
                <div className="npc-name">{npcId.charAt(0).toUpperCase() + npcId.slice(1)}</div>
                <div className="npc-action">{activity.activity}</div>
                <div className="text-xs opacity-70 mt-1 capitalize">{activity.intent}</div>
                {activity.dialogue_available && (
                    <div className="text-xs text-disco-cyan mt-1">💬 Chat Available</div>
                )}
            </div>
        </div>
    );
};

// --- Helpers ---

const getSpotIcon = (type) => {
    switch (type) {
        case 'seat': return '🪑';
        case 'work': return '🔨';
        case 'lookout': return '🔭';
        case 'rest': return '🛌';
        default: return '📍';
    }
};

const getStatusColor = (intent) => {
    switch (intent) {
        case 'social': return 'status-social';
        case 'work': return 'status-work';
        case 'rest': return 'status-rest';
        default: return '';
    }
};

// --- Main Component ---

const CampView = ({ visible, onClose, gameState }) => {
    const [layout, setLayout] = useState(null);
    const [routines, setRoutines] = useState(null);
    const [activeEvent, setActiveEvent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [interaction, setInteraction] = useState(null); // Active interaction sequence

    // Polling for camp state
    const fetchCampState = useCallback(async () => {
        if (!visible) return;

        try {
            // 1. Get Layout
            if (!layout) {
                const layoutData = await api.get('/camp/layout');
                setLayout(layoutData.layout);
            }

            // 2. Get Routines (Activities)
            // Use current game time if available, else default
            const hour = gameState?.world?.current_time_hour || 12;
            const routineData = await api.get(`/camp/routines?hour=${hour}`);
            setRoutines(routineData);

            // 3. Check for Events
            const eventData = await api.get('/camp/events/check');
            if (eventData.event_available) {
                setActiveEvent(eventData.event);
            } else {
                setActiveEvent(null);
            }

            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch camp state:", err);
            setLoading(false);
        }
    }, [visible, layout, gameState]);

    useEffect(() => {
        if (visible) {
            fetchCampState();
            const interval = setInterval(fetchCampState, 5000); // Poll every 5s
            return () => clearInterval(interval);
        }
    }, [visible, fetchCampState]);

    // Handlers
    const handleInteract = async (npcId) => {
        try {
            // Only allow one interaction at a time for now
            const res = await api.post('/camp/interact', {
                npc_id: npcId,
                player_location: "common_area" // Simplification: assume player is central
            });

            if (res.triggered) {
                setInteraction(res);
                // Maybe open a modal or overlay for the dialogue?
                // For now, we'll just log it or show a simple alert/toast
                console.log("Interaction started:", res);
                // TODO: Wire up to main narrative log or dedicated dialogue modal
            } else {
                console.log("No interaction available:", res.message);
            }
        } catch (err) {
            console.error("Interaction failed:", err);
        }
    };

    const handleAffordance = async (spotId, type) => {
        try {
            // Derive affordance type from spot type for MVP
            // In full mapping: seat -> sit, work -> chore, etc.
            const affordanceMap = {
                'seat': 'sit',
                'work': 'chore',
                'lookout': 'contemplate', // maybe?
                'rest': 'nap'
            };
            const affordance = affordanceMap[type] || 'sit';

            const res = await api.post('/camp/affordance', {
                affordance_type: affordance,
                spot_id: spotId
            });

            console.log("Affordance result:", res);
            // Trigger visual feedback / XP gain
            fetchCampState(); // Refresh to show occupied spot
        } catch (err) {
            console.error("Affordance failed:", err);
        }
    };

    if (!visible) return null;

    return (
        <div className="camp-overlay">
            <div className="camp-header">
                <div>
                    <h2>🏕️ CAMP HUB</h2>
                    <div className="text-sm text-disco-cyan/60 font-mono">
                        {routines?.season.toUpperCase()} | {routines?.weather.toUpperCase()} | {routines?.hour}:00
                    </div>
                </div>
                <div className="camp-controls">
                    <button onClick={onClose} title="Close Camp View">✕</button>
                </div>
            </div>

            <div className="camp-container custom-scrollbar">
                {activeEvent && (
                    <div className="active-event-banner">
                        <span>🔥 EVENT: {activeEvent.name.toUpperCase()}</span>
                        <button className="join-event-btn">JOIN IN</button>
                    </div>
                )}

                {loading ? (
                    <div className="flex items-center justify-center h-full text-disco-cyan">
                        Scanning Camp Perimeter...
                    </div>
                ) : (
                    <div className="camp-grid">
                        {layout && Object.values(layout).map(zone => {
                            // Filter activities for this zone
                            const zoneActivities = routines?.activities
                                ? Object.entries(routines.activities)
                                    .filter(([id, act]) => act.location === zone.zone_id)
                                    .map(([id, act]) => ({ npc_id: id, ...act }))
                                : [];

                            return (
                                <CampZone
                                    key={zone.zone_id}
                                    zone={zone}
                                    activities={zoneActivities}
                                    onInteract={handleInteract}
                                    onAffordance={handleAffordance}
                                />
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Interaction Overlay (Simple MVP) */}
            {interaction && (
                <div className="absolute bottom-0 left-0 right-0 bg-black/90 border-t border-disco-cyan p-6 p-8 animate-slide-up">
                    <div className="max-w-4xl mx-auto flex gap-6">
                        <div
                            className="w-16 h-16 rounded-full border-2 border-disco-cyan bg-cover bg-center"
                            style={{ backgroundImage: `url(/assets/avatars/${interaction.npc_id}.png)` }}
                        />
                        <div className="flex-1">
                            <h4 className="text-disco-cyan font-serif text-xl mb-2 capitalize">{interaction.npc_id}</h4>
                            <p className="text-lg text-disco-paper font-serif italic">"{interaction.dialogue}"</p>
                            <div className="mt-4 flex gap-4">
                                <button
                                    className="px-4 py-2 bg-disco-cyan/20 border border-disco-cyan text-disco-cyan hover:bg-disco-cyan/40 rounded transition-colors"
                                    onClick={async () => {
                                        const res = await api.post(`/camp/interact/${interaction.npc_id}/advance`);
                                        if (res.completed) setInteraction(null);
                                        else setInteraction({ ...interaction, dialogue: res.dialogue });
                                    }}
                                >
                                    Continue
                                </button>
                                <button
                                    className="px-4 py-2 border border-disco-red/50 text-disco-red hover:bg-disco-red/10 rounded transition-colors"
                                    onClick={() => setInteraction(null)}
                                >
                                    End Conversation
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CampView;
