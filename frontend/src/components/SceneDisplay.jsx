import React, { useState, useEffect, useRef } from 'react';

/**
 * Enhanced SceneDisplay with:
 * - Ken Burns effect (slow zoom/pan when idle)
 * - Smooth crossfade between scene changes
 * - Parallax effect on mouse movement
 * - Enhanced loading states
 */
const SceneDisplay = ({ imageUrl, isLoading, locationName }) => {
    const [localImage, setLocalImage] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [previousImage, setPreviousImage] = useState(null);
    const [isTransitioning, setIsTransitioning] = useState(false);
    const [mousePosition, setMousePosition] = useState({ x: 0.5, y: 0.5 });
    const containerRef = useRef(null);

    // Handle image transitions with crossfade
    useEffect(() => {
        if (imageUrl && imageUrl !== previousImage) {
            setIsTransitioning(true);
            const timer = setTimeout(() => {
                setPreviousImage(imageUrl);
                setIsTransitioning(false);
            }, 1000); // Crossfade duration
            return () => clearTimeout(timer);
        }
    }, [imageUrl, previousImage]);

    // Parallax effect on mouse move
    const handleMouseMove = (e) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;
        const y = (e.clientY - rect.top) / rect.height;
        setMousePosition({ x, y });
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                setLocalImage(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    // Use local image if dropped, otherwise backend URL, otherwise placeholder
    const displaySrc = localImage || imageUrl || '/assets/defaults/location_placeholder.png';

    // Construct full URL if relative
    const finalSrc = displaySrc.startsWith('http') || displaySrc.startsWith('data:')
        ? displaySrc
        : `http://localhost:8000${displaySrc}`;

    // Calculate parallax transform
    const parallaxX = (mousePosition.x - 0.5) * 10;
    const parallaxY = (mousePosition.y - 0.5) * 10;

    return (
        <div
            ref={containerRef}
            className={`w-full h-full relative group transition-colors duration-300 overflow-hidden ${isDragging ? 'bg-disco-accent/20' : 'bg-black'}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onMouseMove={handleMouseMove}
        >
            {/* Previous Image Layer (for crossfade) */}
            {previousImage && isTransitioning && (
                <div className="absolute inset-0 z-0">
                    <img
                        src={previousImage.startsWith('http') || previousImage.startsWith('data:')
                            ? previousImage
                            : `http://localhost:8000${previousImage}`}
                        alt="Previous scene"
                        className="w-full h-full object-cover opacity-100"
                    />
                </div>
            )}

            {/* Current Image Layer with Ken Burns */}
            <div
                className="absolute inset-[-20px] z-1 transition-transform duration-300 ease-out"
                style={{
                    transform: `translate(${parallaxX}px, ${parallaxY}px)`,
                }}
            >
                <img
                    src={finalSrc}
                    alt={locationName}
                    className={`
                        w-full h-full object-cover transition-all duration-1000
                        ${isLoading ? 'opacity-50 blur-sm scale-110' : 'opacity-100 scale-100'}
                        ${isTransitioning ? 'opacity-0' : 'opacity-100'}
                        animate-kenburns
                    `}
                    style={{
                        animationPlayState: isLoading ? 'paused' : 'running',
                    }}
                />
            </div>

            {/* Loading Overlay */}
            {isLoading && (
                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-black/50 backdrop-blur-sm">
                    <div className="w-16 h-16 border-4 border-disco-accent border-t-transparent rounded-full animate-spin mb-4"></div>
                    <div className="font-mono text-disco-cyan text-xs uppercase tracking-widest">
                        Rendering scene...
                    </div>
                </div>
            )}

            {/* Drag Hint */}
            <div className={`absolute inset-0 z-20 flex items-center justify-center pointer-events-none transition-opacity duration-300
                ${isDragging ? 'opacity-100' : 'opacity-0 group-hover:opacity-30'}`}
            >
                <div className="bg-black/70 px-6 py-3 rounded-lg text-disco-paper font-mono text-sm border border-disco-muted backdrop-blur-sm">
                    {isDragging ? '📥 DROP TO SET SCENE' : '🖼️ DRAG IMAGE HERE'}
                </div>
            </div>

            {/* Vignette with dynamic intensity */}
            <div
                className="absolute inset-0 pointer-events-none z-10 transition-opacity duration-500"
                style={{
                    background: 'radial-gradient(ellipse at center, transparent 30%, rgba(0,0,0,0.8) 100%)',
                    opacity: isLoading ? 0.9 : 0.7,
                }}
            />

            {/* Film grain overlay for atmosphere */}
            <div
                className="absolute inset-0 pointer-events-none z-15 opacity-10 mix-blend-overlay"
                style={{
                    backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noise\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noise)\'/%3E%3C/svg%3E")',
                }}
            />

            {/* Scene transition flash */}
            {isTransitioning && (
                <div className="absolute inset-0 z-30 bg-white/10 animate-pulse pointer-events-none" />
            )}
        </div>
    );
};

export default SceneDisplay;

