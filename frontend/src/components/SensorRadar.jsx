import React, { useState, useEffect, useCallback, useRef } from 'react';
import api from '../utils/api';
import DraggableModal from './DraggableModal';

const SensorRadar = ({ visible, onClose, sessionId = "default", playerLocation = { x: 0, y: 0 } }) => {
    const [pois, setPois] = useState([]);
    const [loading, setLoading] = useState(false);
    const [scanning, setScanning] = useState(false);
    const [discoveryRadius, setDiscoveryRadius] = useState(100);
    const canvasRef = useRef(null);
    const [hoveredPoi, setHoveredPoi] = useState(null);

    const fetchPois = useCallback(async () => {
        setLoading(true);
        try {
            const data = await api.get(`/poi/nearby?session_id=${sessionId}&x=${playerLocation.x}&y=${playerLocation.y}&radius=500`);
            setPois(data.pois || []);
        } catch (err) {
            console.error("Failed to fetch POIs:", err);
        } finally {
            setLoading(false);
        }
    }, [sessionId, playerLocation]);

    useEffect(() => {
        if (visible) {
            fetchPois();
        }
    }, [visible, fetchPois]);

    const handleDiscover = async (x, y) => {
        setScanning(true);
        try {
            const result = await api.post('/poi/discover', {
                session_id: sessionId,
                x,
                y
            });
            // Refresh POIs to show discovery state
            fetchPois();
            return result.discovered;
        } catch (err) {
            console.error("Discovery failed:", err);
        } finally {
            setScanning(false);
        }
    };

    // Radar Drawing Logic
    useEffect(() => {
        if (!visible || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let animationFrame;
        let angle = 0;

        const render = () => {
            const width = canvas.width;
            const height = canvas.height;
            const centerX = width / 2;
            const centerY = height / 2;
            const maxRadius = Math.min(centerX, centerY) - 20;

            ctx.clearRect(0, 0, width, height);

            // Draw Background Rings
            ctx.strokeStyle = 'rgba(34, 211, 238, 0.2)';
            ctx.lineWidth = 1;
            for (let i = 1; i <= 4; i++) {
                ctx.beginPath();
                ctx.arc(centerX, centerY, (maxRadius / 4) * i, 0, Math.PI * 2);
                ctx.stroke();
            }

            // Draw Crosshair
            ctx.beginPath();
            ctx.moveTo(centerX - maxRadius, centerY);
            ctx.lineTo(centerX + maxRadius, centerY);
            ctx.moveTo(centerX, centerY - maxRadius);
            ctx.lineTo(centerX, centerY + maxRadius);
            ctx.stroke();

            // Draw Sweep
            const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, maxRadius);
            gradient.addColorStop(0, 'rgba(34, 211, 238, 0)');
            gradient.addColorStop(1, 'rgba(34, 211, 238, 0.1)');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, maxRadius, angle, angle + 0.5);
            ctx.lineTo(centerX, centerY);
            ctx.fill();

            // Draw Sweep Edge
            ctx.strokeStyle = 'rgba(34, 211, 238, 0.8)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            const edgeX = centerX + Math.cos(angle + 0.5) * maxRadius;
            const edgeY = centerY + Math.sin(angle + 0.5) * maxRadius;
            ctx.lineTo(edgeX, edgeY);
            ctx.stroke();

            // Draw POIs
            pois.forEach(poi => {
                // Map coordinates from world to radar
                // World is (x, y), Center is (playerLocation.x, playerLocation.y)
                // Offset = (poi.x - player.x, poi.y - player.y)
                const dx = poi.location[0] - playerLocation.x;
                const dy = poi.location[1] - playerLocation.y;

                // Scale factor: maxRadius on screen = 500 units in world
                const scale = maxRadius / 500;
                const screenX = centerX + dx * scale;
                const screenY = centerY + dy * scale;

                const isDiscovered = poi.discovered;

                // Draw Dot
                ctx.fillStyle = isDiscovered ? '#22d3ee' : '#94a3b8';
                ctx.shadowBlur = isDiscovered ? 10 : 0;
                ctx.shadowColor = '#22d3ee';

                ctx.beginPath();
                ctx.arc(screenX, screenY, 4, 0, Math.PI * 2);
                ctx.fill();

                ctx.shadowBlur = 0;

                // Draw label if hovered
                if (hoveredPoi && hoveredPoi.id === poi.id) {
                    ctx.fillStyle = '#fff';
                    ctx.font = '10px monospace';
                    ctx.fillText(poi.name || 'Unknown Contact', screenX + 10, screenY - 10);
                }
            });

            angle += 0.02;
            animationFrame = requestAnimationFrame(render);
        };

        render();
        return () => cancelAnimationFrame(animationFrame);
    }, [visible, pois, playerLocation, hoveredPoi]);

    const handleCanvasClick = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const maxRadius = Math.min(centerX, centerY) - 20;

        // Find clicked POI
        const scale = maxRadius / 500;

        const clickedPoi = pois.find(poi => {
            const dx = poi.location[0] - playerLocation.x;
            const dy = poi.location[1] - playerLocation.y;
            const screenX = centerX + dx * scale;
            const screenY = centerY + dy * scale;

            const dist = Math.sqrt((mouseX - screenX) ** 2 + (mouseY - screenY) ** 2);
            return dist < 10;
        });

        if (clickedPoi) {
            handleDiscover(clickedPoi.location[0], clickedPoi.location[1]);
        }
    };

    const handleCanvasMouseMove = (e) => {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const maxRadius = Math.min(centerX, centerY) - 20;
        const scale = maxRadius / 500;

        const found = pois.find(poi => {
            const dx = poi.location[0] - playerLocation.x;
            const dy = poi.location[1] - playerLocation.y;
            const screenX = centerX + dx * scale;
            const screenY = centerY + dy * scale;

            const dist = Math.sqrt((mouseX - screenX) ** 2 + (mouseY - screenY) ** 2);
            return dist < 10;
        });

        setHoveredPoi(found || null);
    };

    return (
        <DraggableModal
            isOpen={visible}
            onClose={onClose}
            title="🛰️ SENSOR RADAR"
            defaultWidth={800}
            defaultHeight={600}
        >
            <div className="flex h-full bg-black/60 font-mono">
                {/* Radar Area */}
                <div className="flex-1 relative flex items-center justify-center p-4 border-r border-disco-cyan/20">
                    <canvas
                        ref={canvasRef}
                        width={500}
                        height={500}
                        onClick={handleCanvasClick}
                        onMouseMove={handleCanvasMouseMove}
                        className="cursor-crosshair"
                    />

                    {scanning && (
                        <div className="absolute inset-x-0 bottom-10 flex flex-col items-center gap-2 pointer-events-none">
                            <div className="w-48 h-1 bg-disco-muted/30 overflow-hidden">
                                <div className="h-full bg-disco-cyan animate-progressBar" />
                            </div>
                            <span className="text-[10px] text-disco-cyan animate-pulse tracking-[0.3em]">ANALYZING SIGNATURE...</span>
                        </div>
                    )}

                    <div className="absolute top-4 left-4 text-[10px] text-disco-cyan/60 flex flex-col gap-1">
                        <span>LAT: {playerLocation.x.toFixed(2)}</span>
                        <span>LONG: {playerLocation.y.toFixed(2)}</span>
                        <span>MODE: TACTICAL_RECON</span>
                    </div>
                </div>

                {/* Sidebar Info */}
                <div className="w-64 flex flex-col p-4 bg-black/40 overflow-hidden">
                    <h3 className="text-xs font-bold text-disco-paper border-b border-disco-cyan/30 pb-2 mb-4 tracking-widest uppercase">
                        Nearby Signals ({pois.length})
                    </h3>

                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin">
                        {pois.map(poi => (
                            <div
                                key={poi.id}
                                className={`
                                    p-2 border transition-all cursor-pointer text-xs
                                    ${hoveredPoi && hoveredPoi.id === poi.id ? 'border-disco-cyan bg-disco-cyan/10' : 'border-disco-muted/20 hover:border-disco-cyan/50'}
                                    ${poi.discovered ? 'opacity-100' : 'opacity-60'}
                                `}
                                onClick={() => handleDiscover(poi.location[0], poi.location[1])}
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className={`font-bold ${poi.discovered ? 'text-disco-cyan' : 'text-disco-paper'}`}>
                                        {poi.discovered ? (poi.name || 'Unknown') : '?? UNKNOWN ??'}
                                    </span>
                                    <span className="text-[10px] uppercase">{poi.poi_type}</span>
                                </div>
                                {poi.discovered && (
                                    <p className="text-[10px] text-disco-paper/70 leading-tight">
                                        {poi.description}
                                    </p>
                                )}
                                {!poi.discovered && (
                                    <div className="text-[9px] text-disco-red animate-pulse">
                                        [SCAN REQUIRED]
                                    </div>
                                )}
                            </div>
                        ))}

                        {pois.length === 0 && !loading && (
                            <div className="text-center py-10 text-disco-muted italic text-[10px]">
                                No signatures detected in immediate vicinity.
                            </div>
                        )}
                    </div>

                    <div className="mt-4 pt-4 border-t border-disco-cyan/20">
                        <button
                            onClick={fetchPois}
                            disabled={loading || scanning}
                            className="w-full py-2 bg-disco-cyan/10 border border-disco-cyan text-disco-cyan text-[10px] hover:bg-disco-cyan hover:text-black transition-all font-bold uppercase tracking-widest"
                        >
                            {loading ? 'Refreshing...' : 'Refresh Sensors'}
                        </button>
                    </div>
                </div>
            </div>

            <style jsx>{`
                @keyframes progressBar {
                    0% { width: 0%; transform: translateX(-100%); }
                    100% { width: 100%; transform: translateX(100%); }
                }
                .animate-progressBar {
                    animation: progressBar 2s infinite linear;
                }
            `}</style>
        </DraggableModal>
    );
};

export default SensorRadar;
