import React, { useState, useEffect, useRef } from 'react';

/**
 * Enhanced SceneDisplay with:
 * - Ken Burns effect (slow zoom/pan when idle)
 * - Smooth crossfade between scene changes
 * - Parallax effect on mouse movement
 * - Weather overlays (rain, fog, dust, snow)
 * - Time of day filters (day, night, twilight)
 * - Enhanced loading states
 */
const SceneDisplay = ({ imageUrl, isLoading, locationName, weather = 'Clear', timeOfDay = 'Day' }) => {
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

    // Time of day filter styles
    const getTimeFilter = () => {
        switch (timeOfDay) {
            case 'Night':
                return 'brightness(0.4) contrast(1.2) saturate(0.8) hue-rotate(200deg)';
            case 'Twilight':
                return 'brightness(0.7) contrast(1.1) saturate(1.2) sepia(0.3) hue-rotate(-10deg)';
            case 'Dawn':
                return 'brightness(0.8) contrast(1.05) saturate(1.1) hue-rotate(10deg)';
            case 'Day':
            default:
                return 'brightness(1) contrast(1) saturate(1)';
        }
    };

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

            {/* Current Image Layer with Ken Burns and Time Filter */}
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
                        filter: getTimeFilter()
                    }}
                />
            </div>

            {/* Weather Overlays */}
            {(weather === 'Rain' || weather === 'acid_rain') && (
                <div className="absolute inset-0 z-5 pointer-events-none">
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-blue-900/10 to-blue-900/20" />
                    {[...Array(50)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute w-px bg-gradient-to-b from-transparent via-white/60 to-transparent animate-rain"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `-${Math.random() * 20}%`,
                                height: `${20 + Math.random() * 30}px`,
                                animationDelay: `${Math.random() * 2}s`,
                                animationDuration: `${0.5 + Math.random() * 0.5}s`
                            }}
                        />
                    ))}
                </div>
            )}

            {(weather === 'Fog' || weather === 'dense_nebula' || weather === 'light_nebula') && (
                <div className="absolute inset-0 z-5 pointer-events-none">
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-300/40 via-gray-400/20 to-transparent backdrop-blur-sm animate-pulse" />
                    {weather === 'dense_nebula' && (
                        <div className="absolute inset-0 bg-purple-900/20 mix-blend-overlay" />
                    )}
                </div>
            )}

            {(weather === 'Dust Storm' || weather === 'debris_field') && (
                <div className="absolute inset-0 z-5 pointer-events-none">
                    <div className="absolute inset-0 bg-gradient-to-br from-orange-900/30 via-yellow-900/20 to-transparent animate-pulse" />
                    {[...Array(30)].map((_, i) => (
                        <div
                            key={i}
                            className={`absolute rounded-full animate-dust ${weather === 'debris_field' ? 'w-2 h-2 bg-gray-600/60' : 'w-1 h-1 bg-yellow-700/40'}`}
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                animationDelay: `${Math.random() * 3}s`,
                                animationDuration: `${3 + Math.random() * 2}s`
                            }}
                        />
                    ))}
                </div>
            )}

            {(weather === 'Snow' || weather === 'ice_storm') && (
                <div className="absolute inset-0 z-5 pointer-events-none">
                    {[...Array(40)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute w-1 h-1 bg-white rounded-full animate-snow"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `-${Math.random() * 20}%`,
                                animationDelay: `${Math.random() * 3}s`,
                                animationDuration: `${3 + Math.random() * 2}s`
                            }}
                        />
                    ))}
                </div>
            )}

            {(weather === 'Storm' || weather === 'ion_storm' || weather === 'solar_flare') && (
                <div className="absolute inset-0 z-5 pointer-events-none">
                    <div className={`absolute inset-0 bg-gradient-to-b animate-pulse ${weather === 'solar_flare' ? 'from-orange-500/20 to-transparent' : 'from-gray-900/40 to-transparent'}`} />
                    <div className={`absolute inset-0 ${weather === 'solar_flare' ? 'animate-flare' : 'animate-lightning'}`} />
                </div>
            )}

            {(weather === 'asteroid_field') && (
                <div className="absolute inset-0 z-5 pointer-events-none">
                    {[...Array(15)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute bg-stone-700/80 rounded-full animate-float"
                            style={{
                                width: `${4 + Math.random() * 12}px`,
                                height: `${4 + Math.random() * 12}px`,
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                animationDelay: `${Math.random() * 5}s`,
                                animationDuration: `${10 + Math.random() * 20}s`,
                                opacity: 0.7
                            }}
                        />
                    ))}
                </div>
            )}

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

