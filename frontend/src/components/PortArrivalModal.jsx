import React, { useState, useEffect } from 'react';
import DraggableModal from './DraggableModal';
import TypewriterText from './TypewriterText';

const API_URL = 'http://localhost:8001/api';

/**
 * PortArrivalModal - Handles the final Port Arrival sequence
 * - Day 8 Approach (NPC conversations)
 * - Docking (arrival scenario)
 * - Dispersal (crew fates)
 * - Epilogue (final reflection)
 */
const PortArrivalModal = ({ isOpen, onClose, sessionId = 'default' }) => {
    const [stage, setStage] = useState('approach'); // approach, docking, dispersal, epilogue
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [selectedNPC, setSelectedNPC] = useState(null);
    const [error, setError] = useState(null);

    // Load initial approach scene
    useEffect(() => {
        if (isOpen && stage === 'approach') {
            loadApproachScene();
        }
    }, [isOpen, stage]);

    const loadApproachScene = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/narrative/port-arrival/approach?session_id=${sessionId}`);
            if (response.ok) {
                const result = await response.json();
                setData(result);
            } else {
                setError('Failed to load approach scene');
            }
        } catch (err) {
            console.error('Error loading approach:', err);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    const loadNPCConversation = async (npcId) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/narrative/port-arrival/approach?session_id=${sessionId}&npc_id=${npcId}`);
            if (response.ok) {
                const result = await response.json();
                setSelectedNPC(result);
            } else {
                setError(`Failed to load ${npcId} conversation`);
            }
        } catch (err) {
            console.error(`Error loading ${npcId}:`, err);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    const loadDocking = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/narrative/port-arrival/docking?session_id=${sessionId}`);
            if (response.ok) {
                const result = await response.json();
                setData(result);
                setStage('docking');
            } else {
                setError('Failed to load docking scene');
            }
        } catch (err) {
            console.error('Error loading docking:', err);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    const loadDispersal = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/narrative/port-arrival/dispersal?session_id=${sessionId}`);
            if (response.ok) {
                const result = await response.json();
                setData(result);
                setStage('dispersal');
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to load dispersal');
            }
        } catch (err) {
            console.error('Error loading dispersal:', err);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    const loadEpilogue = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/narrative/port-arrival/epilogue?session_id=${sessionId}`);
            if (response.ok) {
                const result = await response.json();
                setData(result);
                setStage('epilogue');
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to load epilogue');
            }
        } catch (err) {
            console.error('Error loading epilogue:', err);
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    const renderApproach = () => {
        if (!data) return null;

        if (selectedNPC) {
            return (
                <>
                    <div className="mb-6">
                        <button
                            onClick={() => setSelectedNPC(null)}
                            className="text-disco-cyan hover:text-disco-paper font-mono text-sm"
                        >
                            ← Back to Approach
                        </button>
                    </div>
                    <div className="border-l-4 border-disco-cyan/30 pl-6 mb-8">
                        <h3 className="text-disco-cyan font-mono text-sm uppercase mb-4">
                            {selectedNPC.npc_id}
                        </h3>
                        <TypewriterText
                            text={selectedNPC.conversation}
                            baseSpeed={15}
                            className="font-serif text-lg leading-relaxed text-disco-paper whitespace-pre-line"
                        />
                    </div>
                    <div className="flex justify-end">
                        <button
                            onClick={() => setSelectedNPC(null)}
                            className="px-6 py-2 border border-disco-cyan text-disco-cyan hover:bg-disco-cyan hover:text-black transition-all font-mono uppercase text-sm"
                        >
                            Continue
                        </button>
                    </div>
                </>
            );
        }

        return (
            <>
                <div className="mb-8">
                    <TypewriterText
                        text={data.narration}
                        baseSpeed={15}
                        className="font-serif text-lg leading-relaxed text-disco-paper whitespace-pre-line mb-6"
                    />
                    <div className="border-l-4 border-disco-purple/30 pl-6 mt-6">
                        <TypewriterText
                            text={data.torres_prompt}
                            baseSpeed={15}
                            startDelay={2000}
                            className="font-serif text-disco-purple italic whitespace-pre-line"
                        />
                    </div>
                </div>

                <div className="mb-8">
                    <h3 className="text-disco-cyan font-mono text-sm uppercase mb-4">Final Conversations</h3>
                    <div className="grid grid-cols-2 gap-3">
                        {data.available_conversations?.map(npc => (
                            <button
                                key={npc}
                                onClick={() => loadNPCConversation(npc)}
                                disabled={loading}
                                className="p-4 border border-disco-muted text-disco-muted hover:border-disco-cyan hover:text-disco-cyan transition-all font-mono uppercase text-sm"
                            >
                                {npc}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        onClick={loadDocking}
                        disabled={loading}
                        className="px-8 py-3 bg-disco-cyan/20 border border-disco-cyan text-disco-cyan hover:bg-disco-cyan hover:text-black transition-all font-mono uppercase tracking-widest"
                    >
                        {loading ? 'Loading...' : 'Proceed to Docking'}
                    </button>
                </div>
            </>
        );
    };

    const renderDocking = () => {
        if (!data) return null;

        return (
            <>
                <div className="mb-8">
                    <TypewriterText
                        text={data.arrival_description}
                        baseSpeed={15}
                        className="font-serif text-lg leading-relaxed text-disco-paper whitespace-pre-line mb-6"
                    />
                    <div className="bg-disco-red/10 border border-disco-red/30 p-6 rounded">
                        <h3 className="text-disco-red font-mono text-sm uppercase mb-2">Authority Presence</h3>
                        <p className="font-serif text-disco-paper/90">{data.authority_presence}</p>
                    </div>
                    {data.yuki_handoff && (
                        <div className="border-l-4 border-disco-purple/30 pl-6 mt-6">
                            <TypewriterText
                                text={data.yuki_handoff}
                                baseSpeed={15}
                                startDelay={2000}
                                className="font-serif text-disco-purple italic whitespace-pre-line"
                            />
                        </div>
                    )}
                </div>

                <div className="flex justify-end">
                    <button
                        onClick={loadDispersal}
                        disabled={loading}
                        className="px-8 py-3 bg-disco-cyan/20 border border-disco-cyan text-disco-cyan hover:bg-disco-cyan hover:text-black transition-all font-mono uppercase tracking-widest"
                    >
                        {loading ? 'Loading...' : 'Crew Dispersal'}
                    </button>
                </div>
            </>
        );
    };

    const renderDispersal = () => {
        if (!data || !data.dispersals) return null;

        return (
            <>
                <div className="mb-8">
                    <h3 className="text-disco-cyan font-mono text-sm uppercase mb-4">
                        The Crew Departs ({data.ending_type})
                    </h3>
                    <div className="space-y-6">
                        {Object.entries(data.dispersals).map(([npcId, outcome]) => (
                            <div key={npcId} className="border-l-4 border-disco-muted/30 pl-6">
                                <h4 className="text-disco-cyan font-mono text-xs uppercase mb-2">{npcId}</h4>
                                <TypewriterText
                                    text={outcome}
                                    baseSpeed={15}
                                    className="font-serif text-disco-paper whitespace-pre-line"
                                />
                            </div>
                        ))}
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        onClick={loadEpilogue}
                        disabled={loading}
                        className="px-8 py-3 bg-disco-purple/20 border border-disco-purple text-disco-purple hover:bg-disco-purple hover:text-black transition-all font-mono uppercase tracking-widest"
                    >
                        {loading ? 'Loading...' : 'Final Reflection'}
                    </button>
                </div>
            </>
        );
    };

    const renderEpilogue = () => {
        if (!data) return null;

        return (
            <>
                <div className="mb-8 space-y-6">
                    <div>
                        <p className="font-mono text-xs text-disco-purple mb-2">ARCHETYPE: {data.archetype}</p>
                        <p className="font-mono text-xs text-disco-cyan mb-4">PATH: {data.ending_type}</p>
                    </div>

                    <div className="bg-disco-dark/50 border border-disco-cyan/30 p-6 rounded">
                        <h3 className="text-disco-cyan font-mono text-sm uppercase mb-3">Setting</h3>
                        <TypewriterText
                            text={data.setting}
                            baseSpeed={15}
                            className="font-serif text-disco-paper whitespace-pre-line"
                        />
                    </div>

                    <div className="border-l-4 border-disco-purple/30 pl-6">
                        <h3 className="text-disco-purple font-mono text-sm uppercase mb-3">Reflection</h3>
                        <TypewriterText
                            text={data.reflection}
                            baseSpeed={15}
                            startDelay={2000}
                            className="font-serif text-disco-paper italic whitespace-pre-line"
                        />
                    </div>

                    <div className="bg-disco-dark/50 border border-disco-muted/30 p-6 rounded">
                        <TypewriterText
                            text={data.closing_image}
                            baseSpeed={15}
                            startDelay={4000}
                            className="font-serif text-lg text-disco-paper whitespace-pre-line"
                        />
                    </div>

                    <div className="border-l-4 border-disco-cyan/30 pl-6">
                        <h3 className="text-disco-cyan font-mono text-sm uppercase mb-3">Wisdom</h3>
                        <TypewriterText
                            text={data.wisdom}
                            baseSpeed={15}
                            startDelay={6000}
                            className="font-serif text-disco-cyan whitespace-pre-line"
                        />
                    </div>

                    <div className="text-center mt-8 pt-8 border-t border-disco-muted/20">
                        <TypewriterText
                            text={data.final_question}
                            baseSpeed={20}
                            startDelay={8000}
                            className="font-serif text-xl text-disco-purple italic"
                        />
                    </div>
                </div>

                <div className="flex justify-center">
                    <button
                        onClick={onClose}
                        className="px-12 py-4 bg-disco-purple/20 border border-disco-purple text-disco-purple hover:bg-disco-purple hover:text-black transition-all font-mono uppercase tracking-widest"
                    >
                        End Journey
                    </button>
                </div>
            </>
        );
    };

    const renderContent = () => {
        if (loading && !data) {
            return <div className="text-center text-disco-cyan font-mono">Loading...</div>;
        }

        if (error) {
            return (
                <div className="text-center">
                    <p className="text-disco-red font-mono mb-4">{error}</p>
                    <button
                        onClick={() => setError(null)}
                        className="px-6 py-2 border border-disco-cyan text-disco-cyan hover:bg-disco-cyan hover:text-black transition-all font-mono uppercase text-sm"
                    >
                        Dismiss
                    </button>
                </div>
            );
        }

        switch (stage) {
            case 'approach':
                return renderApproach();
            case 'docking':
                return renderDocking();
            case 'dispersal':
                return renderDispersal();
            case 'epilogue':
                return renderEpilogue();
            default:
                return <div className="text-disco-red">Unknown stage: {stage}</div>;
        }
    };

    const getTitle = () => {
        switch (stage) {
            case 'approach':
                return selectedNPC ? `Day 8 - ${selectedNPC.npc_id}` : 'Day 8: Approach';
            case 'docking':
                return 'Meridian Station';
            case 'dispersal':
                return 'Dispersal';
            case 'epilogue':
                return 'Epilogue';
            default:
                return 'Port Arrival';
        }
    };

    if (!isOpen) return null;

    return (
        <DraggableModal
            isOpen={isOpen}
            onClose={onClose}
            title={getTitle()}
            defaultWidth={800}
            defaultHeight={stage === 'epilogue' ? 700 : 600}
        >
            <div className="h-full flex flex-col bg-disco-bg/95 p-8 overflow-y-auto">
                {renderContent()}
            </div>
        </DraggableModal>
    );
};

export default PortArrivalModal;
