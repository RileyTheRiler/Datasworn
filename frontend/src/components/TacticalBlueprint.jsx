import React, { useState, useEffect, useCallback } from 'react';
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import './TacticalBlueprint.css';

/**
 * TacticalBlueprint - Displays AI-generated tactical map for current scene
 * Shows NPC positions, cover spots, entry points for combat/stealth planning
 */
export function TacticalBlueprint({ sessionId, visible = false, onClose }) {
    const [blueprint, setBlueprint] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [selectedNPC, setSelectedNPC] = useState(null);
    const [hoveredNPC, setHoveredNPC] = useState(null);
    const [showMovement, setShowMovement] = useState(false);
    const [showVision, setShowVision] = useState(false);
    const [showLegend, setShowLegend] = useState(false);

    const generateBlueprint = useCallback(async (forceRegenerate = false, options = {}) => {
        if (!sessionId) return;

        setLoading(true);
        setError(null);

        // Use current state or overrides from options
        const useMovement = options.showMovement !== undefined ? options.showMovement : showMovement;
        const useVision = options.showVision !== undefined ? options.showVision : showVision;

        try {
            const response = await fetch('/api/blueprint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    force_regenerate: forceRegenerate,
                    show_movement: useMovement,
                    show_vision: useVision
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to generate blueprint: ${response.status}`);
            }

            const data = await response.json();
            setBlueprint(data);
        } catch (err) {
            console.error('Blueprint generation failed:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [sessionId, showMovement, showVision]);

    // Handle toggles properly by triggering regeneration
    const toggleMovement = () => {
        const newVal = !showMovement;
        setShowMovement(newVal);
        generateBlueprint(false, { showMovement: newVal });
    };

    const toggleVision = () => {
        const newVal = !showVision;
        setShowVision(newVal);
        generateBlueprint(false, { showVision: newVal });
    };

    const handleExport = () => {
        if (!blueprint) return;

        const link = document.createElement('a');
        link.href = `data:image/png;base64,${blueprint.blueprint}`;
        link.download = `tactical_blueprint_${new Date().toISOString().slice(0, 10)}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Generate on first visible
    useEffect(() => {
        if (visible && !blueprint && !loading) {
            generateBlueprint();
        }
    }, [visible, blueprint, loading, generateBlueprint]);

    if (!visible) return null;

    const metadata = blueprint?.metadata || {};
    const npcs = metadata.npcs || [];

    // Disposition color classes
    const getColorClass = (color) => {
        const colorMap = {
            red: 'npc-hostile',
            orange: 'npc-cautious',
            yellow: 'npc-neutral',
            green: 'npc-friendly'
        };
        return colorMap[color] || 'npc-neutral';
    };

    // Calculate NPC marker positions (matching backend logic)
    const calculateNpcPosition = (npcIndex, totalNpcs) => {
        const width = 600;
        const height = 500;
        const margin = 80;
        const usableWidth = width - 2 * margin;
        const usableHeight = (height / 2) - margin;

        if (totalNpcs === 1) {
            return { x: width / 2, y: height / 3 };
        }

        // Arc from left to right
        const angle = Math.PI * (npcIndex + 1) / (totalNpcs + 1);
        const x = margin + (usableWidth * (1 - Math.cos(angle)) / 2);
        const y = margin + (usableHeight * (1 - Math.sin(angle)));

        return { x, y };
    };

    return (
        <div className="tactical-blueprint-overlay">
            <div className="tactical-blueprint-container">
                {/* Header */}
                <div className="blueprint-header">
                    <h3>📍 Tactical Blueprint</h3>
                    <div className="header-controls">
                        <button
                            className={`btn-toggle ${showMovement ? 'active' : ''}`}
                            onClick={toggleMovement}
                            title="Toggle Movement Range"
                        >
                            🏃
                        </button>
                        <button
                            className={`btn-toggle ${showVision ? 'active' : ''}`}
                            onClick={toggleVision}
                            title="Toggle Vision Cones"
                        >
                            👁️
                        </button>
                        <div className="divider"></div>
                        <button
                            className="btn-toggle-legend"
                            onClick={() => setShowLegend(!showLegend)}
                            title={showLegend ? "Hide Legend" : "Show Legend"}
                        >
                            {showLegend ? '📋' : '📋'}
                        </button>
                        <button
                            className="btn-export"
                            onClick={handleExport}
                            disabled={!blueprint}
                            title="Export to PNG"
                        >
                            💾
                        </button>
                        <button
                            className="btn-regenerate"
                            onClick={() => generateBlueprint(true)}
                            disabled={loading}
                            title="Regenerate Map"
                        >
                            {loading ? '⌛' : '🔄'}
                        </button>
                        <button
                            className="btn-close"
                            onClick={onClose}
                            title="Close"
                        >
                            ✕
                        </button>
                    </div>
                </div>

                {/* Main Content */}
                <div className="blueprint-content">
                    {/* Loading State */}
                    {loading && (
                        <div className="loading-state">
                            <div className="loading-spinner" />
                            <p>Generating tactical blueprint...</p>
                        </div>
                    )}

                    {/* Error State */}
                    {error && (
                        <div className="error-state">
                            <span className="error-icon">⚠️</span>
                            <p>{error}</p>
                            <button onClick={() => generateBlueprint(true)}>
                                Retry
                            </button>
                        </div>
                    )}

                    {/* Blueprint Image */}
                    {blueprint && !loading && (
                        <div className="blueprint-display">
                            <TransformWrapper
                                initialScale={1}
                                minScale={0.5}
                                maxScale={4}
                                centerOnInit={true}
                                wheel={{ step: 0.1 }}
                            >
                                {({ zoomIn, zoomOut, resetTransform }) => (
                                    <>
                                        {/* Zoom Controls Overlay */}
                                        <div className="zoom-controls">
                                            <button onClick={() => zoomIn()} title="Zoom In">+</button>
                                            <button onClick={() => zoomOut()} title="Zoom Out">-</button>
                                            <button onClick={() => resetTransform()} title="Reset View">⟲</button>
                                        </div>

                                        <TransformComponent wrapperClass="zoom-wrapper" contentClass="zoom-content">
                                            <div style={{ position: 'relative', width: '100%', height: '100%' }}>
                                                <img
                                                    src={`data:image/png;base64,${blueprint.blueprint}`}
                                                    alt="Tactical Blueprint"
                                                    className="tactical-map-image"
                                                    style={{ display: 'block', maxWidth: 'none' }}
                                                />

                                                {/* Interactive SVG Overlay */}
                                                <svg
                                                    className="interactive-overlay"
                                                    viewBox="0 0 600 500"
                                                    style={{
                                                        position: 'absolute',
                                                        top: 0,
                                                        left: 0,
                                                        width: '100%',
                                                        height: '100%',
                                                        pointerEvents: 'none'
                                                    }}
                                                >
                                                    {npcs.map((npc, i) => {
                                                        const pos = calculateNpcPosition(i, npcs.length);
                                                        const isHovered = hoveredNPC?.name === npc.name;
                                                        const isSelected = selectedNPC?.name === npc.name;

                                                        return (
                                                            <g key={i}>
                                                                {/* Clickable marker */}
                                                                <circle
                                                                    cx={pos.x}
                                                                    cy={pos.y}
                                                                    r={isHovered || isSelected ? 22 : 18}
                                                                    className={`npc-marker-interactive ${getColorClass(npc.color)}`}
                                                                    style={{
                                                                        cursor: 'pointer',
                                                                        pointerEvents: 'all',
                                                                        opacity: isHovered || isSelected ? 1 : 0.8,
                                                                        transition: 'all 0.2s ease'
                                                                    }}
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        setSelectedNPC(npc);
                                                                    }}
                                                                    onMouseEnter={() => setHoveredNPC(npc)}
                                                                    onMouseLeave={() => setHoveredNPC(null)}
                                                                />

                                                                {/* Hover tooltip */}
                                                                {isHovered && !isSelected && (
                                                                    <g>
                                                                        <rect
                                                                            x={pos.x - 40}
                                                                            y={pos.y - 50}
                                                                            width={80}
                                                                            height={30}
                                                                            fill="rgba(20, 24, 30, 0.95)"
                                                                            stroke="#4a5060"
                                                                            rx={4}
                                                                        />
                                                                        <text
                                                                            x={pos.x}
                                                                            y={pos.y - 30}
                                                                            textAnchor="middle"
                                                                            fill="#e0e0e0"
                                                                            fontSize="12"
                                                                            fontWeight="500"
                                                                        >
                                                                            {npc.name}
                                                                        </text>
                                                                    </g>
                                                                )}
                                                            </g>
                                                        );
                                                    })}
                                                </svg>
                                            </div>
                                        </TransformComponent>
                                    </>
                                )}
                            </TransformWrapper>

                            {/* Cache indicator */}
                            {blueprint.from_cache && (
                                <span className="cache-badge" title="Loaded from cache">
                                    Cached
                                </span>
                            )}

                            {/* NPC Detail Popup */}
                            {selectedNPC && (
                                <div className="npc-detail-popup">
                                    <div className="popup-header">
                                        <h3>{selectedNPC.name}</h3>
                                        <button
                                            className="popup-close"
                                            onClick={() => setSelectedNPC(null)}
                                        >
                                            ✕
                                        </button>
                                    </div>
                                    <div className="popup-content">
                                        <div className="popup-field">
                                            <span className="field-label">Role:</span>
                                            <span className="field-value">{selectedNPC.role}</span>
                                        </div>
                                        <div className="popup-field">
                                            <span className="field-label">Disposition:</span>
                                            <span className={`field-value ${getColorClass(selectedNPC.color)}`}>
                                                {selectedNPC.disposition}
                                            </span>
                                        </div>
                                        <div className="popup-actions">
                                            <button
                                                className="btn-interact"
                                                onClick={() => {
                                                    // Future: trigger interaction
                                                    console.log('Interact with', selectedNPC.name);
                                                }}
                                            >
                                                💬 Interact
                                            </button>
                                            <button
                                                className="btn-observe"
                                                onClick={() => {
                                                    // Future: observe NPC
                                                    console.log('Observe', selectedNPC.name);
                                                }}
                                            >
                                                👁️ Observe
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Side Panel (Legend & Info) */}
                    {showLegend && blueprint && !loading && (
                        <div className="blueprint-legend">
                            {/* Location Info */}
                            <div className="legend-section">
                                <h4>Location</h4>
                                <p className="location-name">{metadata.location || 'Unknown'}</p>
                                <p className="zone-type">{metadata.zone_type || 'Unknown Zone'}</p>
                            </div>

                            {/* NPC Legend */}
                            {npcs.length > 0 && (
                                <div className="legend-section">
                                    <h4>Characters</h4>
                                    <ul className="npc-list">
                                        {npcs.map((npc, i) => (
                                            <li key={i} className={`npc-item ${getColorClass(npc.color)}`}>
                                                <span className="npc-dot" />
                                                <span className="npc-name">{npc.name}</span>
                                                <span className="npc-role">{npc.role}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Cover Spots */}
                            {metadata.cover_spots?.length > 0 && (
                                <div className="legend-section">
                                    <h4>Cover Available</h4>
                                    <ul className="cover-list">
                                        {metadata.cover_spots.slice(0, 4).map((cover, i) => (
                                            <li key={i} className="cover-item">
                                                {cover.includes('full') ? '🟢' : '🟡'} {cover}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Entry Points */}
                            {metadata.entry_points?.length > 0 && (
                                <div className="legend-section">
                                    <h4>Entry/Exit Points</h4>
                                    <ul className="entry-list">
                                        {metadata.entry_points.map((entry, i) => (
                                            <li key={i} className="entry-item">
                                                🚪 {entry}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Combat Status */}
                            {metadata.in_combat && (
                                <div className="legend-section combat-active">
                                    <h4>⚔️ Combat Active</h4>
                                    <p>Use cover wisely!</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Footer Hint */}
                <div className="blueprint-footer">
                    <span className="player-hint">🔵 = You</span>
                    <span className="cover-hint">🟢 Full Cover | 🟡 Half Cover</span>
                </div>
            </div>
        </div>
    );
}

export default TacticalBlueprint;
