import React, { useState, useEffect } from 'react';

/**
 * Tutorial - Interactive tutorial/onboarding system
 *
 * Features:
 * - Step-by-step guide through UI
 * - Spotlight highlighting
 * - Skip/restart options
 * - Persistent completion tracking
 */

const TUTORIAL_STEPS = [
    {
        id: 'welcome',
        title: 'Welcome to Starforged',
        description: 'This AI-powered game master will guide you through the dangerous frontiers of the Forge. Let me show you around.',
        target: null, // No specific target, just overlay
        position: 'center',
    },
    {
        id: 'viewport',
        title: 'Visual Viewport',
        description: 'This area displays your current location and surroundings. Watch as scenes come to life based on the narrative.',
        target: '.viewport-container',
        position: 'right',
    },
    {
        id: 'stats',
        title: 'Character Stats',
        description: 'Track your Health, Spirit, Supply, and Momentum here. Keep an eye on these—they determine your survival.',
        target: '.stats-panel',
        position: 'right',
    },
    {
        id: 'narrative',
        title: 'Narrative Feed',
        description: 'Your story unfolds here. Each entry reveals what happens, building an epic tale of your journey through the stars.',
        target: '.narrative-scroll',
        position: 'left',
    },
    {
        id: 'input',
        title: 'Action Input',
        description: 'Describe what you want to do here. Be creative! The AI will interpret your actions and shape the story accordingly.',
        target: '.action-input',
        position: 'top',
    },
    {
        id: 'skill-check',
        title: 'Skill Checks',
        description: 'When danger strikes, you'll roll dice to determine outcomes. Click a stat name to roll, or use keyboard shortcuts (1-5).',
        target: '.stats-panel',
        position: 'right',
    },
    {
        id: 'psyche',
        title: 'Psyche Dashboard',
        description: 'This tracks your mental state. Stress, trauma, and psychological hijacks can affect your character deeply.',
        target: '.psyche-dashboard',
        position: 'left',
    },
    {
        id: 'shortcuts',
        title: 'Keyboard Shortcuts',
        description: 'Press "?" at any time to view all keyboard shortcuts. Master these for faster gameplay!',
        target: null,
        position: 'center',
    },
    {
        id: 'complete',
        title: 'You're Ready!',
        description: 'The Forge awaits. Trust your instincts, make bold choices, and forge your own legend among the stars.',
        target: null,
        position: 'center',
    },
];

const Tutorial = ({ onComplete, onSkip }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isVisible, setIsVisible] = useState(true);
    const [hasCompletedBefore, setHasCompletedBefore] = useState(false);

    useEffect(() => {
        // Check if user has completed tutorial before
        const completed = localStorage.getItem('tutorial_completed');
        if (completed) {
            setHasCompletedBefore(true);
            setIsVisible(false);
        }
    }, []);

    const step = TUTORIAL_STEPS[currentStep];

    const handleNext = () => {
        if (currentStep < TUTORIAL_STEPS.length - 1) {
            setCurrentStep(prev => prev + 1);
        } else {
            handleComplete();
        }
    };

    const handlePrevious = () => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    };

    const handleComplete = () => {
        localStorage.setItem('tutorial_completed', 'true');
        setIsVisible(false);
        onComplete?.();
    };

    const handleSkipTutorial = () => {
        localStorage.setItem('tutorial_completed', 'true');
        setIsVisible(false);
        onSkip?.();
    };

    const handleRestart = () => {
        setCurrentStep(0);
        setIsVisible(true);
    };

    // Don't show tutorial if user has completed it before and it's not manually restarted
    if (!isVisible) {
        return (
            <button
                onClick={handleRestart}
                className="fixed bottom-4 left-4 z-[100] px-3 py-2 bg-disco-cyan/10 hover:bg-disco-cyan/20 border border-disco-cyan/30 text-disco-cyan font-mono text-xs rounded transition-colors"
                title="Restart Tutorial"
            >
                ? Tutorial
            </button>
        );
    }

    return (
        <>
            {/* Overlay */}
            <div className="fixed inset-0 bg-black/80 z-[200] backdrop-blur-sm" />

            {/* Spotlight effect for targeted elements */}
            {step.target && (
                <style>{`
                    ${step.target} {
                        position: relative;
                        z-index: 201 !important;
                        box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.8), 0 0 20px rgba(107, 228, 227, 0.5) !important;
                    }
                `}</style>
            )}

            {/* Tutorial Card */}
            <div
                className={`fixed z-[202] bg-disco-bg border-2 border-disco-cyan rounded-lg shadow-2xl max-w-md w-full p-6 ${
                    step.position === 'center'
                        ? 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'
                        : step.position === 'right'
                        ? 'top-1/2 right-8 -translate-y-1/2'
                        : step.position === 'left'
                        ? 'top-1/2 left-8 -translate-y-1/2'
                        : 'bottom-24 left-1/2 -translate-x-1/2'
                }`}
            >
                {/* Progress indicator */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex gap-1">
                        {TUTORIAL_STEPS.map((_, i) => (
                            <div
                                key={i}
                                className={`h-1 rounded-full transition-all ${
                                    i === currentStep
                                        ? 'w-8 bg-disco-cyan'
                                        : i < currentStep
                                        ? 'w-4 bg-disco-cyan/50'
                                        : 'w-4 bg-disco-muted/30'
                                }`}
                            />
                        ))}
                    </div>
                    <span className="text-disco-muted font-mono text-xs">
                        {currentStep + 1} / {TUTORIAL_STEPS.length}
                    </span>
                </div>

                {/* Content */}
                <div className="mb-6">
                    <h3 className="text-disco-cyan font-mono text-lg mb-2 flex items-center gap-2">
                        {currentStep === 0 && '👋'}
                        {currentStep === TUTORIAL_STEPS.length - 1 && '🚀'}
                        {step.title}
                    </h3>
                    <p className="text-disco-paper font-serif text-sm leading-relaxed">
                        {step.description}
                    </p>
                </div>

                {/* Navigation */}
                <div className="flex gap-2">
                    {currentStep > 0 && (
                        <button
                            onClick={handlePrevious}
                            className="px-4 py-2 bg-disco-muted/20 hover:bg-disco-muted/30 border border-disco-muted text-disco-muted font-mono text-sm rounded transition-colors"
                        >
                            ← Back
                        </button>
                    )}

                    <button
                        onClick={handleNext}
                        className="flex-1 px-4 py-2 bg-disco-cyan/20 hover:bg-disco-cyan/30 border border-disco-cyan text-disco-cyan font-mono text-sm rounded transition-colors"
                    >
                        {currentStep === TUTORIAL_STEPS.length - 1 ? 'Start Playing' : 'Next →'}
                    </button>

                    {currentStep === 0 && (
                        <button
                            onClick={handleSkipTutorial}
                            className="px-4 py-2 bg-disco-red/20 hover:bg-disco-red/30 border border-disco-red text-disco-red font-mono text-sm rounded transition-colors"
                        >
                            Skip
                        </button>
                    )}
                </div>

                {/* Hint */}
                {currentStep === 0 && (
                    <p className="mt-4 text-disco-muted font-mono text-xs text-center">
                        You can restart this tutorial anytime from the bottom-left corner
                    </p>
                )}
            </div>
        </>
    );
};

export default Tutorial;
