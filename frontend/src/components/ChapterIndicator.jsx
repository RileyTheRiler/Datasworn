import React, { useState, useEffect } from 'react';

const ChapterIndicator = ({
    title,
    number,
    season,
    progress = 0,
    total = 1,
    missions = [],
    className = ""
}) => {
    const [expanded, setExpanded] = useState(false);

    // Season icons mapping
    const seasonIcons = {
        'Winter': '❄️',
        'Spring': '🌱',
        'Summer': '☀️',
        'Fall': '🍂'
    };

    return (
        <div
            className={`
                relative group transition-all duration-300 z-40
                ${expanded ? 'w-64' : 'w-auto'}
                ${className}
            `}
            onMouseEnter={() => setExpanded(true)}
            onMouseLeave={() => setExpanded(false)}
        >
            {/* Main Badge */}
            <div className={`
                flex items-center gap-3 px-3 py-1.5 
                bg-black/60 border border-disco-muted/30 rounded-full 
                backdrop-blur-sm shadow-lg cursor-help
                hover:border-disco-cyan/50 hover:bg-black/80 hover:shadow-glow
                transition-all duration-300
            `}>
                {/* Season Icon */}
                <div className="flex flex-col items-center justify-center w-8 h-8 rounded-full bg-disco-dark border border-disco-muted/20 text-lg">
                    {seasonIcons[season] || '✨'}
                </div>

                {/* Chapter Info */}
                <div className="flex flex-col">
                    <span className="text-[10px] font-mono text-disco-muted uppercase tracking-widest leading-none">
                        Chapter {number}
                    </span>
                    <span className="font-serif text-disco-paper font-bold tracking-wide text-sm whitespace-nowrap">
                        {title}
                    </span>
                </div>

                {/* Progress Ring (Mini) */}
                <div className="relative w-8 h-8 flex items-center justify-center ml-1">
                    <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                        <path
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="#334155"
                            strokeWidth="3"
                        />
                        <path
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="#22d3ee"
                            strokeWidth="3"
                            strokeDasharray={`${(progress / total) * 100}, 100`}
                            className="transition-all duration-1000 ease-out"
                        />
                    </svg>
                    <span className="absolute text-[9px] font-mono text-disco-cyan">
                        {progress}/{total}
                    </span>
                </div>
            </div>

            {/* Expanded Details Dropdown */}
            <div className={`
                absolute top-full right-0 mt-2 w-64 
                bg-black/90 border border-disco-cyan/30 rounded-lg 
                shadow-2xl backdrop-blur-md overflow-hidden
                transition-all duration-300 origin-top-right
                ${expanded ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 -translate-y-2 pointer-events-none'}
            `}>
                {/* Header */}
                <div className="px-4 py-2 bg-disco-cyan/10 border-b border-disco-cyan/20">
                    <h3 className="text-xs font-mono text-disco-cyan uppercase tracking-wider">
                        Current Objectives
                    </h3>
                </div>

                {/* Mission List */}
                <div className="p-3 space-y-2">
                    {missions.length > 0 ? (
                        missions.map((mission, idx) => (
                            <div key={idx} className="flex items-start gap-2">
                                <div className={`
                                    mt-1 w-3 h-3 rounded-full border flex items-center justify-center
                                    ${mission.completed
                                        ? 'bg-disco-cyan border-disco-cyan'
                                        : 'bg-transparent border-disco-muted'}
                                `}>
                                    {mission.completed && (
                                        <svg className="w-2 h-2 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={4} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </div>
                                <span className={`text-xs ${mission.completed ? 'text-disco-muted line-through' : 'text-disco-paper'}`}>
                                    {mission.name.replace(/_/g, ' ')}
                                </span>
                            </div>
                        ))
                    ) : (
                        <div className="text-xs text-disco-muted italic">No active missions</div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-3 py-1.5 bg-black/50 border-t border-disco-muted/20 text-[10px] text-disco-muted text-center font-mono">
                    SEASON: {season.toUpperCase()}
                </div>
            </div>
        </div>
    );
};

export default ChapterIndicator;
