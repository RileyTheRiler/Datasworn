import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import './PhotoAlbum.css';

const PhotoAlbum = ({ sessionId, visible, onClose }) => {
    const [photos, setPhotos] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedPhoto, setSelectedPhoto] = useState(null);

    useEffect(() => {
        if (visible) {
            fetchAlbum();
        }
    }, [visible, sessionId]);

    const fetchAlbum = async () => {
        try {
            setLoading(true);
            const data = await api.get(`/album?session_id=${sessionId}`);
            setPhotos(data.photos || []);
        } catch (error) {
            console.error('Failed to fetch album:', error);
        } finally {
            setLoading(false);
        }
    };

    const openLightbox = (photo) => {
        setSelectedPhoto(photo);
    };

    const closeLightbox = () => {
        setSelectedPhoto(null);
    };

    if (!visible) return null;

    return (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-sm flex items-center justify-center animate-fadeIn">
            <div className="bg-disco-panel border-2 border-disco-cyan p-6 rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-hard relative photo-album-modal">

                {/* Header */}
                <div className="flex justify-between items-center mb-8 border-b border-disco-cyan/30 pb-4">
                    <div>
                        <h2 className="text-4xl font-serif font-bold text-disco-cyan tracking-wider">MEMORY ARCHIVE</h2>
                        <p className="text-disco-paper/60 font-mono text-xs uppercase tracking-[0.2em]">
                            {photos.length} cinematic moments memorialized
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-red text-3xl transition-colors"
                    >
                        ×
                    </button>
                </div>

                {loading ? (
                    <div className="h-96 flex flex-col items-center justify-center gap-4">
                        <div className="w-12 h-12 border-2 border-disco-cyan border-t-transparent rounded-full animate-spin" />
                        <span className="text-disco-cyan font-mono animate-pulse uppercase tracking-widest">Accessing Neural Logs...</span>
                    </div>
                ) : photos.length === 0 ? (
                    <div className="h-96 flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-disco-muted/20 rounded-lg">
                        <span className="text-6xl mb-4 opacity-20">📷</span>
                        <h3 className="text-2xl font-serif text-disco-paper/80 mb-2">No Memories Recorded</h3>
                        <p className="text-disco-muted max-w-md font-mono text-sm">
                            Significant dramatic peaks, major vows, and critical confrontations will be automatically archived as your story unfolds.
                        </p>
                    </div>
                ) : (
                    <div className="photo-grid">
                        {photos.map((photo) => (
                            <div
                                key={photo.id}
                                className="photo-card-container group"
                                onClick={() => openLightbox(photo)}
                            >
                                <div className="polaroid-wrapper">
                                    <div className="polaroid-content">
                                        <div className="photo-frame">
                                            <img
                                                src={`http://localhost:8000${photo.image_url}`}
                                                alt={photo.caption}
                                                className="photo-img"
                                                loading="lazy"
                                                onError={(e) => {
                                                    e.target.src = '/assets/defaults/location_placeholder.png';
                                                }}
                                            />
                                            <div className="photo-overlay" />
                                        </div>
                                        <div className="polaroid-caption">
                                            <p className="caption-text font-serif italic">{photo.caption}</p>
                                            <div className="photo-metadata">
                                                <span className="photo-date font-mono text-[10px]">
                                                    {new Date(photo.timestamp).toLocaleDateString()}
                                                </span>
                                                <div className="photo-tags-compact">
                                                    {photo.tags.slice(0, 2).map((tag, idx) => (
                                                        <span key={idx} className="tag-mini">{tag}</span>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Lightbox / Detail View */}
                {selectedPhoto && (
                    <div className="lightbox-overlay" onClick={closeLightbox}>
                        <div className="lightbox-container" onClick={(e) => e.stopPropagation()}>
                            <div className="lightbox-image-wrapper">
                                <img
                                    src={`http://localhost:8000${selectedPhoto.image_url}`}
                                    alt={selectedPhoto.caption}
                                    className="lightbox-img"
                                />
                                <button className="lightbox-close-btn" onClick={closeLightbox}>×</button>
                            </div>
                            <div className="lightbox-details bg-disco-panel p-6 border-t border-disco-cyan/30">
                                <h3 className="text-2xl font-serif font-bold text-disco-cyan mb-2">{selectedPhoto.caption}</h3>
                                <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-disco-paper/60 mb-4">
                                    <span className="flex items-center gap-1">🕒 {new Date(selectedPhoto.timestamp).toLocaleString()}</span>
                                    {selectedPhoto.scene_id && <span className="flex items-center gap-1">📍 {selectedPhoto.scene_id}</span>}
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {selectedPhoto.tags.map((tag, idx) => (
                                        <span key={idx} className="px-2 py-0.5 border border-disco-cyan/40 bg-disco-cyan/10 text-disco-cyan text-[10px] uppercase tracking-wider rounded">
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PhotoAlbum;
