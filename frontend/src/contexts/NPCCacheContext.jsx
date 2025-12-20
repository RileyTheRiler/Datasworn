import React, { createContext, useContext, useState, useCallback } from 'react';

/**
 * NPCCacheContext - Caches NPC data to avoid repeated API calls
 * 
 * Features:
 * - Stores fetched NPC data in memory
 * - Provides getNPC and setNPC functions
 * - Invalidates cache when session changes
 */

const API_URL = 'http://localhost:8000/api';

const NPCCacheContext = createContext(null);

export const useNPCCache = () => {
    const context = useContext(NPCCacheContext);
    if (!context) {
        throw new Error('useNPCCache must be used within NPCCacheProvider');
    }
    return context;
};

export const NPCCacheProvider = ({ children }) => {
    const [cache, setCache] = useState({});
    const [loading, setLoading] = useState({});

    /**
     * Get NPC from cache or fetch from API
     */
    const getNPC = useCallback(async (name) => {
        const cacheKey = name.toLowerCase();

        // Return cached data if available
        if (cache[cacheKey]) {
            return cache[cacheKey];
        }

        // Check if already loading
        if (loading[cacheKey]) {
            // Wait for existing fetch
            return new Promise((resolve) => {
                const checkCache = setInterval(() => {
                    if (cache[cacheKey]) {
                        clearInterval(checkCache);
                        resolve(cache[cacheKey]);
                    }
                }, 100);
                // Timeout after 5 seconds
                setTimeout(() => {
                    clearInterval(checkCache);
                    resolve(null);
                }, 5000);
            });
        }

        // Fetch from API
        setLoading(prev => ({ ...prev, [cacheKey]: true }));

        try {
            const res = await fetch(`${API_URL}/npc/${encodeURIComponent(name)}`);
            if (res.ok) {
                const data = await res.json();
                setCache(prev => ({ ...prev, [cacheKey]: data }));
                return data;
            }
        } catch (err) {
            console.error('Failed to fetch NPC:', err);
        } finally {
            setLoading(prev => ({ ...prev, [cacheKey]: false }));
        }

        return null;
    }, [cache, loading]);

    /**
     * Manually set NPC in cache (e.g., from game state)
     */
    const setNPC = useCallback((name, data) => {
        const cacheKey = name.toLowerCase();
        setCache(prev => ({ ...prev, [cacheKey]: data }));
    }, []);

    /**
     * Pre-populate cache with crew data from game state
     */
    const populateFromGameState = useCallback((crewData) => {
        if (!crewData) return;

        Object.values(crewData).forEach(npc => {
            if (npc.name) {
                const cacheKey = npc.name.toLowerCase();
                // Calculate disposition
                let disposition = 'neutral';
                if (npc.trust >= 0.7) disposition = 'loyal';
                else if (npc.trust >= 0.5) disposition = 'friendly';
                else if (npc.trust >= 0.3) disposition = 'neutral';
                else if (npc.suspicion >= 0.6) disposition = 'hostile';
                else disposition = 'suspicious';

                setCache(prev => ({
                    ...prev,
                    [cacheKey]: {
                        name: npc.name,
                        role: npc.role || 'Unknown',
                        trust: npc.trust || 0.5,
                        suspicion: npc.suspicion || 0,
                        disposition,
                        image_url: npc.image_url || '/assets/defaults/portrait_placeholder.png',
                        description: npc.description || '',
                        known_facts: npc.known_facts || [],
                        secrets: npc.secrets || [],
                        emotional_history: npc.emotional_history || []
                    }
                }));
            }
        });
    }, []);

    /**
     * Clear all cached data
     */
    const clearCache = useCallback(() => {
        setCache({});
    }, []);

    /**
     * Check if NPC is in cache
     */
    const hasNPC = useCallback((name) => {
        return !!cache[name.toLowerCase()];
    }, [cache]);

    const value = {
        getNPC,
        setNPC,
        populateFromGameState,
        clearCache,
        hasNPC,
        cache
    };

    return (
        <NPCCacheContext.Provider value={value}>
            {children}
        </NPCCacheContext.Provider>
    );
};

export default NPCCacheProvider;
