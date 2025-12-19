import React, { useState } from 'react';

const SceneDisplay = ({ imageUrl, isLoading, locationName }) => {
    const [localImage, setLocalImage] = useState(null);
    const [isDragging, setIsDragging] = useState(false);

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

    return (
        <div
            className={`w-full h-full relative group transition-colors duration-300 ${isDragging ? 'bg-disco-accent/20' : 'bg-black'}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
        >
            {/* Image Layer */}
            <div className="absolute inset-0 z-0">
                <img
                    src={finalSrc}
                    alt={locationName}
                    className={`w-full h-full object-cover transition-all duration-1000 ${isLoading ? 'opacity-50 blur-sm scale-110' : 'opacity-100 scale-100'}`}
                />
            </div>

            {/* Loading Overlay */}
            {isLoading && (
                <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/40">
                    <div className="w-16 h-16 border-4 border-disco-accent border-t-transparent rounded-full animate-spin"></div>
                </div>
            )}

            {/* Drag Hint */}
            <div className={`absolute inset-0 z-20 flex items-center justify-center pointer-events-none opacity-0 ${isDragging ? 'opacity-100' : 'group-hover:opacity-30'} transition-opacity`}>
                <div className="bg-black/60 px-4 py-2 rounded text-disco-paper font-mono text-sm border border-disco-muted">
                    {isDragging ? 'DROP TO UPLOAD' : 'DRAG IMAGE HERE'}
                </div>
            </div>

            {/* Vignette */}
            <div className="absolute inset-0 bg-radial-gradient from-transparent to-black/80 pointer-events-none z-10"></div>
        </div>
    );
};

export default SceneDisplay;
