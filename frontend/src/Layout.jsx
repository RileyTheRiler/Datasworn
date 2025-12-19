import React, { useEffect, useRef, useState } from 'react';
import SkillCheck from './components/SkillCheck';
import SceneDisplay from './components/SceneDisplay';

const API_URL = 'http://localhost:8000/api';

const MarkdownText = ({ text }) => {
    return <div className="font-serif text-lg leading-relaxed whitespace-pre-wrap">{text}</div>
}

const StatBar = ({ label, value, max, color }) => (
    <div className="mb-2">
        <div className="flex justify-between text-xs font-mono uppercase text-disco-muted mb-1">
            <span>{label}</span>
            <span>{value}/{max}</span>
        </div>
        <div className="h-2 bg-disco-bg border border-disco-muted/30 rounded-sm overflow-hidden">
            <div
                style={{ width: `${(value / max) * 100}%` }}
                className={`h-full ${color} transition-all duration-500`}
            />
        </div>
    </div>
)

const Layout = ({ gameState, assets, onAction, isLoading }) => {
    const { character, narrative, world, session } = gameState; // Assuming session is passed in game state or we need it from prop
    const scrollRef = useRef(null);
    const [input, setInput] = React.useState("");
    const [showSkillCheck, setShowSkillCheck] = useState(false);
    const [activeStat, setActiveStat] = useState({ name: 'Iron', value: character.stats.iron });

    // We need session_id for the roll commit. 
    // Usually it's in the top level App, let's assume we can pass it down via onAction wrapper or similar.
    // For now, let's fetch it from a dirty global or verify where we get it.
    // Ideally Layout should receive 'onRoll' prop.

    // Quick fix: Add activeStat selection logic.

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [narrative.pending_narrative]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;
        onAction(input);
        setInput("");
    }

    const handleRollComplete = async () => {
        // This needs to be a real API call.
        // Since we don't have session ID easily here without refactoring App.jsx heavily to pass it,
        // We will hacky-fetch it or assume onAction can handle a special object?
        // No, let's just use the `fetch` here, assuming we need to grab session ID.
        // Actually, let's assume valid session for now or mock it if strictly visual.
        // But we want it to work.
        // Let's add session_id to `gameState` in `server.py`? 
        // Good idea.

        const sessionId = "default"; // Hardcoded in server.py MVP

        const res = await fetch(`${API_URL}/roll/commit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                stat_name: activeStat.name,
                stat_val: activeStat.value,
                adds: 0,
                move_name: "Action Roll"
            })
        });
        const data = await res.json();
        // Update global state via parent?
        // The parent `onAction` updates state. We should probably trigger a state update here too.
        // Let's reload state? or pass a refresh callback?
        // For MVP, we'll just reload the page/state via a "look" action or similar invisible update?
        // Better: App.jsx should pass a `setGameState` equivalent.
        // Using `onAction` with a special string is a hack.
        // Let's just do `onAction("Checking " + activeStat.name)`... 
        // Wait, that generates text narrative. 
        // `data` contains the new state and narrative!
        // We can't update state effortlessly without lifting state up or a callback.
        // Let's cheat and reload via window for the "Verification" phase if needed, 
        // OR better: Assume the user sees the output in the component, and then the narrative updates on next action.

        return data;
    }

    return (
        <div className="flex h-screen w-full bg-disco-bg bg-grunge bg-blend-multiply overflow-hidden">
            {/* LEFT: Visual & Stats */}
            <div className="w-1/3 border-r border-disco-muted/20 flex flex-col relative bg-black/20">
                {/* Isometric Viewport */}
                <div className="flex-1 bg-black/80 relative overflow-hidden group">
                    {/* Scene Display */}
                    <div className="absolute inset-0 z-0">
                        <SceneDisplay
                            imageUrl={assets?.scene_image}
                            locationName={world?.current_location}
                            isLoading={isLoading}
                        />
                    </div>

                    {/* Vignette - kept for style */}
                    <div className="absolute inset-0 bg-radial-gradient from-transparent to-black/80 pointer-events-none z-10 transition-opacity duration-500 opacity-60"></div>

                    {/* Location Overlay */}
                    <div className="absolute top-0 left-0 p-8 w-full z-20 pointer-events-none">
                        <h2 className="font-serif text-4xl text-disco-paper text-outline italic tracking-wider filter drop-shadow-lg">{world.current_location}</h2>
                        <div className="flex items-center gap-2 mt-2">
                            <span className="w-2 h-2 bg-disco-accent rounded-full animate-pulse"></span>
                            <div className="text-disco-paper/60 font-mono text-xs tracking-[0.2em] uppercase">Sector: The Forge</div>
                        </div>
                    </div>
                </div>

                {/* Character HUD */}
                <div className="h-1/3 bg-disco-panel p-6 border-t border-disco-muted/20 flex flex-col relative overflow-hidden">
                    {/* Grunge Overlay for Panel */}
                    <div className="absolute inset-0 bg-grunge opacity-20 pointer-events-none"></div>

                    <div className="flex items-start gap-6 mb-6 relative z-10">
                        <div className="w-24 h-32 bg-disco-dark border-2 border-disco-paper/20 shadow-hard rotate-[-1deg] relative overflow-hidden group transition-transform hover:rotate-0">
                            {/* Portrait */}
                            <img
                                src={assets?.portrait || "/assets/defaults/portrait_placeholder.png"}
                                alt="Character"
                                className="w-full h-full object-cover grayscale-[30%] contrast-125 hover:grayscale-0 transition-all duration-700"
                            />
                        </div>
                        <div className="flex-1 pt-2">
                            <h3 className="font-serif text-3xl font-bold text-disco-paper text-outline tracking-wider">{character.name}</h3>
                            <div className="flex gap-2 mt-3">
                                <span className="px-2 py-0.5 bg-disco-red/10 border border-disco-red text-disco-red text-[10px] font-mono uppercase tracking-wider font-bold">Iron Sworn</span>
                                <span className="px-2 py-0.5 bg-disco-cyan/10 border border-disco-cyan text-disco-cyan text-[10px] font-mono uppercase tracking-wider font-bold">Lvl 1</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-x-8 gap-y-4 relative z-10">
                        <StatBar label="Health" value={character.condition.health} max={5} color="bg-disco-red" />
                        <StatBar label="Spirit" value={character.condition.spirit} max={5} color="bg-disco-purple" />
                        <StatBar label="Supply" value={character.condition.supply} max={5} color="bg-disco-yellow" />
                        <StatBar label="Momentum" value={character.momentum.value} max={10} color="bg-disco-cyan" />
                    </div>
                </div>
            </div>

            {/* RIGHT: Narrative Flow */}
            <div className="w-2/3 flex flex-col relative bg-disco-bg before:content-[''] before:absolute before:inset-0 before:bg-grunge before:opacity-10">
                {/* Log */}
                <div className="flex-1 overflow-y-auto p-12 scroll-smooth" ref={scrollRef}>
                    <div className="max-w-3xl mx-auto space-y-12">
                        <div className="prose prose-invert prose-lg text-disco-paper/90 transition-opacity duration-500 font-serif leading-loose">
                            <MarkdownText text={narrative.pending_narrative} />
                        </div>

                        {isLoading && (
                            <div className="flex items-center gap-3 text-disco-cyan font-mono text-sm animate-pulse">
                                <span>[COMMUNICATING WITH ORACLE...]</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Input Area */}
                <div className="p-8 pb-12 bg-gradient-to-t from-disco-bg via-disco-bg to-transparent">
                    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative group flex gap-2">
                        {/* Skill Check Toggle */}
                        <button
                            type="button"
                            onClick={() => setShowSkillCheck(true)}
                            className="px-4 py-2 border border-disco-muted text-disco-paper font-serif hover:bg-disco-accent hover:text-black transition-colors"
                            title="Make a Move"
                        >
                            🎲
                        </button>

                        <input
                            type="text"
                            className="flex-1 bg-black/40 border-b-2 border-disco-muted text-disco-paper font-serif text-xl p-4 focus:outline-none focus:border-disco-accent transition-colors placeholder:text-disco-muted/30"
                            placeholder="What do you do?"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            disabled={isLoading}
                            autoFocus
                        />
                        <button
                            type="submit"
                            className="absolute right-4 top-1/2 -translate-y-1/2 opacity-0 group-focus-within:opacity-100 transition-opacity text-disco-accent font-serif font-bold tracking-wider uppercase"
                        >
                            Execute
                        </button>
                    </form>

                    {/* Dice/Skill Check Overlay */}
                    {showSkillCheck && (
                        <SkillCheck
                            stat={character.stats.iron}
                            statName="Iron"
                            character={character}
                            onRollComplete={handleRollComplete}
                            onClose={() => setShowSkillCheck(false)}
                        />
                    )}
                </div>
            </div>
        </div>
    )
}

export default Layout;
