import React, { useState, useEffect, useCallback } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import './ShipBlueprintViewer.css';

/**
 * ShipBlueprintViewer - Displays ship schematic with damage states and interior layout
 * Shows hull integrity, damaged systems, and ship modules
 */
export function ShipBlueprintViewer({ sessionId, visible = false, onClose }) {
    const [blueprint, setBlueprint] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showLegend, setShowLegend] = useState(true);

    const generateBlueprint = useCallback(async (forceRegenerate = false) => {
        if (!sessionId) return;

        setLoading(true);
        setError(null);

        try {
            const response = await fetch('/api/ship/blueprint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    force_regenerate: forceRegenerate
                })
            });

            if (!response.ok) {
                throw new Error(`Failed to generate ship blueprint: ${response.status}`);
            }

            const data = await response.json();
            setBlueprint(data);
        } catch (err) {
            console.error('Ship blueprint generation failed:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [sessionId]);

    const handleExport = () => {
        if (!blueprint) return;

        const link = document.createElement('a');
        link.href = `data:image/png;base64,${blueprint.blueprint}`;
        link.download = `ship_schematic_${metadata.name || 'vessel'}_${new Date().toISOString().slice(0, 10)}.png`;
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

    // ESC to close
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape' && visible) {
                onClose();
            }
        };
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [visible, onClose]);

    if (!visible) return null;

    const metadata = blueprint?.metadata || {};
    const integrity = metadata.integrity || {};
    const damageLevel = metadata.damage_level || "none";
    const alerts = metadata.alerts || [];

    // Damage level color
    const getDamageColor = (level) => {
        const colorMap = {
            none: '#4ade80',
            moderate: '#fbbf24',
            heavy: '#f97316',
            critical: '#ef4444'
        };
        return colorMap[level] || '#4ade80';
    };

    return (
        <div className="ship-blueprint-overlay" onClick={onClose}>
            <div className="ship-blueprint-container" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="blueprint-header">
                    <h3>🚀 Ship Schematic</h3>
                    <div className="header-controls">
                        <button
                            className="btn-toggle-legend"
                            onClick={() => setShowLegend(!showLegend)}
                            title={showLegend ? "Hide Info" : "Show Info"}
                        >
                            📋
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
                            title="Regenerate Schematic"
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
                            <p>Generating ship schematic...</p>
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
                                            <img
                                                src={`data:image/png;base64,${blueprint.blueprint}`}
                                                alt="Ship Schematic"
                                                className="ship-schematic-image"
                                            />
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
                        </div>
                    )}

                    {/* Side Panel (Info & Status) */}
                    {showLegend && blueprint && !loading && (
                        <div className="blueprint-legend">
                            {/* Ship Info */}
                            <div className="legend-section">
                                <h4>Vessel</h4>
                                <p className="ship-name">{metadata.name || 'Unknown Ship'}</p>
                                <p className="ship-class">{metadata.class_type || 'Unknown Class'}</p>
                            </div>

                            {/* Hull Integrity */}
                            <div className="legend-section">
                                <h4>Hull Integrity</h4>
                                <div className="integrity-bar">
                                    <div
                                        className="integrity-fill"
                                        style={{
                                            width: `${integrity.percent || 100}%`,
                                            backgroundColor: getDamageColor(damageLevel)
                                        }}
                                    />
                                </div>
                                <p className="integrity-text">
                                    {integrity.hull || 100} / {integrity.max || 100} ({integrity.percent || 100}%)
                                </p>
                                <p className={`damage-status ${damageLevel}`}>
                                    Status: {damageLevel.toUpperCase()}
                                </p>
                            </div>

                            {/* Active Alerts */}
                            {alerts.length > 0 && (
                                <div className="legend-section alerts-section">
                                    <h4>⚠️ Active Alerts</h4>
                                    <ul className="alerts-list">
                                        {alerts.map((alert, i) => (
                                            <li key={i} className="alert-item">
                                                {alert}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Ship Systems */}
                            <div className="legend-section">
                                <h4>Systems</h4>
                                <ul className="systems-list">
                                    <li>🎯 Bridge</li>
                                    <li>⚙️ Engineering</li>
                                    <li>📦 Cargo Bay</li>
                                    <li>🛏️ Crew Quarters</li>
                                    <li>⚕️ Medical Bay</li>
                                </ul>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer Hint */}
                <div className="blueprint-footer">
                    <span className="hint">Grid represents ship interior layout</span>
                </div>
            </div>
        </div>
    );
}

export default ShipBlueprintViewer;
