
import React, { useRef, useEffect, useState } from 'react';

const GameCanvas = () => {
    const canvasRef = useRef(null);
    const [entities, setEntities] = useState([]);
    const [psycheData, setPsycheData] = useState(null);
    const [psycheEffects, setPsycheEffects] = useState('');
    const [shakeAnimation, setShakeAnimation] = useState('');

    // Load assets
    const [bgImage, setBgImage] = useState(null);
    const [playerImage, setPlayerImage] = useState(null);

    // Load images
    useEffect(() => {
        const bg = new Image();
        bg.src = "http://localhost:8000/assets/room_start.png";
        bg.onload = () => setBgImage(bg);

        const ply = new Image();
        ply.src = "http://localhost:8000/assets/player.png";
        ply.onload = () => setPlayerImage(ply);
    }, []);

    // Mock entity for now
    useEffect(() => {
        setEntities([
            { id: 'player', x: 368, y: 268, color: 'cyan', size: 64 }, // Centered(ish)
        ]);
    }, []);

    // Poll psyche data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/psyche/default');
                if (res.ok) {
                    const json = await res.json();
                    setPsycheData(json);
                }
            } catch (err) {
                // Silently fail
            }
        };

        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    // Calculate visual effects from psyche
    useEffect(() => {
        if (!psycheData) return;

        const profile = psycheData.profile || {};
        const sanity = profile.sanity !== undefined ? profile.sanity : 1.0;
        const traumaCount = profile.trauma_scars?.length || 0;
        const emotion = profile.current_emotion || 'neutral';

        let filters = [];

        // Chromatic aberration at low sanity
        if (sanity < 0.3) {
            const intensity = (0.3 - sanity) * 10;
            filters.push(`drop-shadow(${intensity}px 0 0 red) drop-shadow(-${intensity}px 0 0 cyan)`);
        }

        // Vignette from trauma
        if (traumaCount > 0) {
            const darkness = Math.min(0.5, traumaCount * 0.15);
            filters.push(`brightness(${1 - darkness})`);
        }

        // Desaturation at low sanity
        if (sanity < 0.3) {
            const desaturation = (0.3 - sanity) * 100;
            filters.push(`saturate(${100 - desaturation}%)`);
        }

        setPsycheEffects(filters.join(' '));

        // Shake animation when afraid
        if (emotion === 'afraid') {
            setShakeAnimation('shake 0.5s infinite');
        } else {
            setShakeAnimation('');
        }

    }, [psycheData]);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        let animationFrameId;

        const render = () => {
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw Background
            if (bgImage) {
                // Scale to fit or fill? Let's fill coverage.
                ctx.drawImage(bgImage, 0, 0, canvas.width, canvas.height);
            } else {
                // Fallback Grid
                ctx.strokeStyle = '#333';
                ctx.lineWidth = 1;
                for (let i = 0; i < canvas.width; i += 50) {
                    ctx.beginPath();
                    ctx.moveTo(i, 0);
                    ctx.lineTo(i, canvas.height);
                    ctx.stroke();
                }
                for (let i = 0; i < canvas.height; i += 50) {
                    ctx.beginPath();
                    ctx.moveTo(0, i);
                    ctx.lineTo(canvas.width, i);
                    ctx.stroke();
                }

                // Fallback text
                ctx.fillStyle = '#666';
                ctx.font = '20px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText("Upload 'room_start.png' to see background", canvas.width / 2, canvas.height / 2);
                ctx.textAlign = 'start'; // Reset
            }

            // Draw entities
            entities.forEach(entity => {
                if (entity.id === 'player' && playerImage) {
                    ctx.drawImage(playerImage, entity.x, entity.y, entity.size, entity.size);
                } else {
                    // Fallback box
                    ctx.fillStyle = entity.color;
                    ctx.fillRect(entity.x, entity.y, entity.size, entity.size);
                }

                // Draw label
                ctx.fillStyle = 'white';
                ctx.font = '12px sans-serif';
                ctx.fillText(entity.id, entity.x, entity.y - 5);
            });

            animationFrameId = requestAnimationFrame(render);
        };

        render();

        return () => {
            cancelAnimationFrame(animationFrameId);
        };
    }, [entities]);

    return (
        <div className="w-full h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden relative">
            <canvas
                ref={canvasRef}
                width={800}
                height={600}
                className="block bg-gray-950"
                style={{
                    filter: psycheEffects,
                    animation: shakeAnimation,
                }}
            />
            <div className="absolute top-2 left-2 text-white bg-black/50 p-2 rounded pointer-events-none">
                <h3 className="text-sm font-bold">2D Viewport</h3>
                <p className="text-xs">React + Canvas</p>
            </div>
        </div>
    );
};

export default GameCanvas;
