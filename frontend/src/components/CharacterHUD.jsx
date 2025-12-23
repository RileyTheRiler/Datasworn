import React from 'react';
import PortraitSettings from './PortraitSettings';

const STAT_ICONS = {
    'Health': '❤',
    'Spirit': '✦',
    'Supply': '▣',
    'Momentum': '⚡'
};

const StatBar = ({ label, value, max, color, isMomentum }) => {
    const percentage = (value / max) * 100;
    const icon = STAT_ICONS[label] || '●';

    // Check if momentum is "burning" (maxed out or high)
    const isBurning = isMomentum && value >= 10;
    const isReset = isMomentum && value <= 2;

    return (
        <div className="mb-3 group relative">
            <div className="flex justify-between text-[10px] font-mono uppercase text-disco-cyan/70 mb-1.5 relative z-10">
                <span className="flex items-center gap-1">
                    <span className={`text-xs ${isBurning ? 'animate-pulse text-disco-accent' : ''}`}>{icon}</span>
                    {label}
                </span>
                <span className={`font-bold ${isBurning ? 'text-disco-accent drop-shadow-[0_0_5px_rgba(107,228,227,0.8)]' : 'text-disco-paper/80'}`}>
                    {value}/{max}
                </span>
            </div>

            <div className={`h-2.5 bg-black/60 border ${isBurning ? 'border-disco-accent' : 'border-disco-cyan/20'} relative overflow-hidden transition-colors duration-500 shadow-[0_0_10px_rgba(0,0,0,0.5)]`}>
                {/* Animated background grid */}
                <div className="absolute inset-0 opacity-20" style={{
                    backgroundImage: 'repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(107, 228, 227, 0.1) 2px, rgba(107, 228, 227, 0.1) 4px)'
                }} />

                {/* Progress bar with gradient */}
                <div
                    style={{ width: `${Math.max(0, Math.min(100, percentage))}%` }}
                    className={`h-full ${color} transition-all duration-700 ease-out relative`}
                >
                    {/* Glow effect */}
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />

                    {/* Burning Momentum Effect */}
                    {isBurning && (
                        <div className="absolute inset-0 bg-disco-accent/50 animate-[pulse_0.5s_infinite]" style={{
                            boxShadow: '0 0 10px #6be4e3, 0 0 20px #6be4e3'
                        }} />
                    )}
                </div>

                {/* Danger indicator for low values (except momentum) */}
                {!isMomentum && percentage < 30 && value > 0 && (
                    <div className="absolute right-0 top-0 w-1 h-full bg-disco-red animate-pulse" />
                )}

                {/* Momentum Reset Warning */}
                {isReset && (
                    <div className="absolute right-0 top-0 w-1 h-full bg-disco-red animate-pulse" />
                )}
            </div>
        </div>
    );
}

const CharacterHUD = ({ character, assets, onAssetsUpdate, className = "" }) => {
    const [showPortraitSettings, setShowPortraitSettings] = React.useState(false);

    if (!character) return null;

    return (
        <div className={`bg-disco-panel p-6 border-t border-disco-muted/20 flex flex-col relative overflow-hidden ${className}`}>
            {/* Grunge Overlay for Panel */}
            <div className="absolute inset-0 bg-grunge opacity-20 pointer-events-none"></div>

            <div className="flex items-start gap-6 mb-6 relative z-10">
                <div className="w-24 h-32 bg-disco-dark border-2 border-disco-paper/20 shadow-hard rotate-[-1deg] relative overflow-hidden group transition-transform hover:rotate-0">
                    {/* Static ID Badge Filter Overlay */}
                    <div className="absolute inset-0 bg-[url('/assets/noise.png')] opacity-10 mix-blend-overlay pointer-events-none z-10"></div>
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/60 z-10 pointer-events-none"></div>
                    {/* Portrait */}
                    <img
                        src={assets?.portrait || "/assets/defaults/avatar_wireframe.svg"}
                        alt="Character"
                        className="w-full h-full object-cover grayscale-[30%] contrast-125 hover:grayscale-0 transition-all duration-700"
                    />
                    {/* Edit Portrait Button via Overlay */}
                    <button
                        onClick={() => setShowPortraitSettings(true)}
                        className="absolute top-1 right-1 p-1 bg-black/50 hover:bg-disco-cyan/80 text-disco-cyan hover:text-black rounded opacity-0 group-hover:opacity-100 transition-opacity z-20"
                        title="Customize Appearance"
                    >
                        ✏️
                    </button>
                </div>
                <div className="flex-1 pt-2">
                    <h3 className="font-serif text-3xl font-bold text-disco-paper text-outline tracking-wider truncate" title={character.name}>
                        {character.name}
                    </h3>
                    <div className="flex gap-2 mt-3 flex-wrap">
                        <span className="px-2 py-0.5 bg-disco-red/10 border border-disco-red text-disco-red text-[10px] font-mono uppercase tracking-wider font-bold">Iron Sworn</span>
                        <span className="px-2 py-0.5 bg-disco-cyan/10 border border-disco-cyan text-disco-cyan text-[10px] font-mono uppercase tracking-wider font-bold">Lvl 1</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-x-8 gap-y-4 relative z-10 text-left">
                <StatBar label="Health" value={character.condition.health} max={5} color="bg-disco-red" />
                <StatBar label="Spirit" value={character.condition.spirit} max={5} color="bg-disco-purple" />
                <StatBar label="Supply" value={character.condition.supply} max={5} color="bg-disco-yellow" />
                {/* Momentum goes from -6 to +10 usually, but visually we can just map 0-10 or use a simpler visual for negative */}
                <StatBar label="Momentum" value={character.momentum.value} max={character.momentum.max_value || 10} color="bg-disco-cyan" isMomentum={true} />
            </div>

            {/* Portrait Settings Modal - Ported specific logic if needed, but reusing component */}
            <PortraitSettings
                isOpen={showPortraitSettings}
                onClose={() => setShowPortraitSettings(false)}
                characterName={character.name}
                onUpdate={(newAssets) => {
                    if (onAssetsUpdate) onAssetsUpdate(prev => ({ ...prev, ...newAssets }));
                }}
            />
        </div>
    );
};

export default CharacterHUD;
