
import React, { useRef, useEffect, useState } from 'react';

const GameCanvas = () => {
    const canvasRef = useRef(null);
    const [entities, setEntities] = useState([]);

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
            />
            <div className="absolute top-2 left-2 text-white bg-black/50 p-2 rounded pointer-events-none">
                <h3 className="text-sm font-bold">2D Viewport</h3>
                <p className="text-xs">React + Canvas</p>
            </div>
        </div>
    );
};

export default GameCanvas;
