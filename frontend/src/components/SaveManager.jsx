import React, { useState, useEffect, useCallback } from 'react';

const API_URL = 'http://localhost:8000/api';

/**
 * SaveManager - Modal component for managing game saves
 * Features: List saves, create, load, delete, quick save/load
 */
const SaveManager = ({ isOpen, onClose, sessionId = "default", onLoadComplete }) => {
    const [saves, setSaves] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [newSaveName, setNewSaveName] = useState('');
    const [newSaveDesc, setNewSaveDesc] = useState('');
    const [showNewSaveForm, setShowNewSaveForm] = useState(false);
    const [recoveryInfo, setRecoveryInfo] = useState(null);

    // Fetch saves on open
    useEffect(() => {
        if (isOpen) {
            fetchSaves();
            checkRecovery();
        }
    }, [isOpen]);

    const fetchSaves = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_URL}/saves`);
            const data = await res.json();
            setSaves(data.saves || []);
        } catch (err) {
            setError('Failed to load saves');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const checkRecovery = async () => {
        try {
            const res = await fetch(`${API_URL}/save/recovery/check`);
            const data = await res.json();
            if (data.recovery_available) {
                setRecoveryInfo(data.info);
            }
        } catch (err) {
            console.error('Recovery check failed:', err);
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_URL}/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    slot_name: newSaveName || null,
                    description: newSaveDesc || 'Manual save'
                })
            });
            const data = await res.json();
            if (data.success) {
                await fetchSaves();
                setNewSaveName('');
                setNewSaveDesc('');
                setShowNewSaveForm(false);
            } else {
                setError('Save failed');
            }
        } catch (err) {
            setError('Failed to create save');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleLoad = async (slotName) => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_URL}/save/${slotName}`);
            const data = await res.json();
            if (data.success) {
                if (onLoadComplete) {
                    onLoadComplete(data.state);
                }
                onClose();
            } else {
                setError('Load failed');
            }
        } catch (err) {
            setError('Failed to load save');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (slotName) => {
        if (!confirm(`Delete save "${slotName}"? This cannot be undone.`)) return;

        setLoading(true);
        try {
            await fetch(`${API_URL}/save/${slotName}`, { method: 'DELETE' });
            await fetchSaves();
        } catch (err) {
            setError('Failed to delete save');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleQuickSave = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/save/quicksave`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            const data = await res.json();
            if (data.success) {
                await fetchSaves();
            }
        } catch (err) {
            setError('Quick save failed');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleQuickLoad = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/save/quickload`);
            const data = await res.json();
            if (data.success) {
                if (onLoadComplete) {
                    onLoadComplete(data.state);
                }
                onClose();
            }
        } catch (err) {
            setError('Quick load failed');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleString();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="panel-glass w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col m-4">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-disco-muted/30">
                    <h2 className="text-2xl font-serif text-disco-paper flex items-center gap-2">
                        <span className="text-disco-cyan">💾</span> Save Manager
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-paper text-2xl transition-colors"
                    >
                        ✕
                    </button>
                </div>

                {/* Error Banner */}
                {error && (
                    <div className="bg-disco-red/20 border-l-4 border-disco-red px-4 py-2 text-disco-red">
                        {error}
                    </div>
                )}

                {/* Recovery Banner */}
                {recoveryInfo && (
                    <div className="bg-disco-yellow/20 border-l-4 border-disco-yellow px-4 py-2 text-disco-yellow">
                        <p className="text-sm">⚠️ {recoveryInfo}</p>
                        <button
                            onClick={() => handleLoad('autosave')}
                            className="text-xs underline mt-1"
                        >
                            Recover now
                        </button>
                    </div>
                )}

                {/* Quick Actions */}
                <div className="flex gap-2 p-4 border-b border-disco-muted/30">
                    <button
                        onClick={handleQuickSave}
                        disabled={loading}
                        className="btn-disco text-sm flex-1 disabled:opacity-50"
                    >
                        ⚡ Quick Save (F5)
                    </button>
                    <button
                        onClick={handleQuickLoad}
                        disabled={loading}
                        className="btn-disco text-sm flex-1 disabled:opacity-50"
                    >
                        ⚡ Quick Load (F9)
                    </button>
                    <button
                        onClick={() => setShowNewSaveForm(!showNewSaveForm)}
                        className="btn-disco text-sm flex-1"
                    >
                        ➕ New Save
                    </button>
                </div>

                {/* New Save Form */}
                {showNewSaveForm && (
                    <form onSubmit={handleSave} className="p-4 bg-disco-bg/50 border-b border-disco-muted/30">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                placeholder="Save name (optional)"
                                value={newSaveName}
                                onChange={(e) => setNewSaveName(e.target.value)}
                                className="flex-1 bg-disco-bg border border-disco-muted/50 px-3 py-2 text-disco-paper 
                                         focus:border-disco-cyan focus:outline-none"
                            />
                            <input
                                type="text"
                                placeholder="Description"
                                value={newSaveDesc}
                                onChange={(e) => setNewSaveDesc(e.target.value)}
                                className="flex-1 bg-disco-bg border border-disco-muted/50 px-3 py-2 text-disco-paper
                                         focus:border-disco-cyan focus:outline-none"
                            />
                            <button
                                type="submit"
                                disabled={loading}
                                className="btn-disco disabled:opacity-50"
                            >
                                Save
                            </button>
                        </div>
                    </form>
                )}

                {/* Saves List */}
                <div className="flex-1 overflow-y-auto p-4 space-y-2">
                    {loading && saves.length === 0 ? (
                        <div className="text-center text-disco-muted py-8">
                            <div className="loading-text">Loading saves...</div>
                        </div>
                    ) : saves.length === 0 ? (
                        <div className="text-center text-disco-muted py-8">
                            <p className="text-lg">No saves yet</p>
                            <p className="text-sm mt-2">Create your first save to protect your progress</p>
                        </div>
                    ) : (
                        saves.map((save) => (
                            <div
                                key={`${save.slot_name}-${save.version}`}
                                className="bg-disco-bg/50 border border-disco-muted/30 p-3 hover:border-disco-cyan/50 
                                         transition-colors group"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <span className="font-mono text-disco-cyan">
                                                {save.slot_name}
                                            </span>
                                            {save.is_auto && (
                                                <span className="text-xs bg-disco-muted/30 px-2 py-0.5 rounded">
                                                    AUTO
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-disco-paper/80 mt-1">
                                            <span className="text-disco-accent">{save.character_name}</span>
                                            {' '}&middot;{' '}
                                            {save.location}
                                            {' '}&middot;{' '}
                                            {save.description}
                                        </p>
                                        <p className="text-xs text-disco-muted mt-1">
                                            {formatDate(save.save_time)}
                                        </p>
                                    </div>
                                    <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={() => handleLoad(save.slot_name)}
                                            className="text-disco-cyan hover:text-disco-paper text-sm px-2 py-1 
                                                     border border-disco-cyan/50 hover:bg-disco-cyan/20"
                                            disabled={loading}
                                        >
                                            Load
                                        </button>
                                        {!save.is_auto && (
                                            <button
                                                onClick={() => handleDelete(save.slot_name)}
                                                className="text-disco-red hover:text-white text-sm px-2 py-1
                                                         border border-disco-red/50 hover:bg-disco-red/20"
                                                disabled={loading}
                                            >
                                                Delete
                                            </button>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="p-3 border-t border-disco-muted/30 text-center text-xs text-disco-muted">
                    Auto-saves every turn &middot; {saves.length} save{saves.length !== 1 ? 's' : ''} stored
                </div>
            </div>
        </div>
    );
};

export default SaveManager;
