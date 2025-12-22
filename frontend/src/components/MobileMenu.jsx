import React, { useState } from 'react';

/**
 * MobileMenu - Hamburger menu for mobile navigation
 */
const MobileMenu = ({ onShowPanel, panels = {} }) => {
    const [isOpen, setIsOpen] = useState(false);

    const menuItems = [
        { key: 'stats', label: 'Character Stats', icon: '📊' },
        { key: 'skillCheck', label: 'Skill Check', icon: '🎲' },
        { key: 'blueprint', label: 'Tactical Map', icon: '🗺️' },
        { key: 'starMap', label: 'Star Map', icon: '✨' },
        { key: 'rumorBoard', label: 'Rumor Board', icon: '📋' },
        { key: 'shipBlueprint', label: 'Ship Status', icon: '🚀' },
        { key: 'album', label: 'Photo Album', icon: '📸' },
        { key: 'saveManager', label: 'Save/Load', icon: '💾' },
        { key: 'recap', label: 'Session Recap', icon: '📖' },
        { key: 'soundSettings', label: 'Sound Settings', icon: '🔊' },
        { key: 'quickReference', label: 'Quick Reference', icon: '❓' },
        { key: 'portraitSettings', label: 'Portrait', icon: '👤' },
    ];

    const handleItemClick = (key) => {
        onShowPanel(key);
        setIsOpen(false);
    };

    return (
        <>
            {/* Hamburger Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed top-4 right-4 z-[150] lg:hidden bg-disco-bg border-2 border-disco-cyan/50 rounded p-2 shadow-lg"
                aria-label="Menu"
            >
                <div className="w-6 h-5 flex flex-col justify-between">
                    <span
                        className={`block h-0.5 bg-disco-cyan transition-transform ${
                            isOpen ? 'rotate-45 translate-y-2' : ''
                        }`}
                    />
                    <span
                        className={`block h-0.5 bg-disco-cyan transition-opacity ${
                            isOpen ? 'opacity-0' : ''
                        }`}
                    />
                    <span
                        className={`block h-0.5 bg-disco-cyan transition-transform ${
                            isOpen ? '-rotate-45 -translate-y-2' : ''
                        }`}
                    />
                </div>
            </button>

            {/* Menu Overlay */}
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 bg-black/80 z-[140] lg:hidden"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Menu Panel */}
                    <div className="fixed top-0 right-0 bottom-0 w-72 bg-disco-bg border-l-2 border-disco-cyan/50 z-[145] lg:hidden overflow-y-auto">
                        <div className="p-4">
                            <h2 className="text-disco-cyan font-mono text-lg mb-4 border-b border-disco-cyan/30 pb-2">
                                MENU
                            </h2>

                            <div className="space-y-1">
                                {menuItems.map((item) => (
                                    <button
                                        key={item.key}
                                        onClick={() => handleItemClick(item.key)}
                                        className="w-full text-left px-3 py-2 rounded text-disco-paper hover:bg-disco-cyan/10 border border-transparent hover:border-disco-cyan/30 transition-colors flex items-center gap-3 font-mono text-sm"
                                    >
                                        <span className="text-lg">{item.icon}</span>
                                        {item.label}
                                    </button>
                                ))}
                            </div>

                            <div className="mt-6 pt-4 border-t border-disco-cyan/30">
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="w-full px-3 py-2 bg-disco-red/20 hover:bg-disco-red/30 border border-disco-red text-disco-red rounded font-mono text-sm transition-colors"
                                >
                                    Close Menu
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </>
    );
};

export default MobileMenu;
