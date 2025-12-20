import { useState, useEffect } from 'react'
import Layout from './Layout'
import PsycheDashboard from './components/PsycheDashboard'
import CharacterCreation from './components/CharacterCreation'
import { ToastProvider } from './components/ToastProvider'
import { TensionVignette, AmbientParticles, HijackOverlay } from './components/UXEffects'
import SoundscapeEngine from './components/SoundscapeEngine'
import { SoundEffectsProvider } from './contexts/SoundEffectsContext'
import { AccessibilityProvider } from './contexts/AccessibilityContext'
import api from './utils/api'

function App() {
  const [session, setSession] = useState(null)
  const [gameState, setGameState] = useState(null)
  const [assets, setAssets] = useState({ scene_image: null, portrait: null })
  const [loading, setLoading] = useState(false)
  const [tension, setTension] = useState(0.2) // Current tension level for effects
  const [hijackActive, setHijackActive] = useState(false)
  const [hijackAspect, setHijackAspect] = useState(null)
  const [isOnline, setIsOnline] = useState(true)
  const [showCharacterCreation, setShowCharacterCreation] = useState(true) // Start with creation

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Poll for psyche state to update tension
  useEffect(() => {
    const fetchPsyche = async () => {
      if (!session) return;
      try {
        const data = await api.get(`/psyche/${session}`);
        // Update tension based on stress level
        const stressLevel = data.profile?.stress_level || 0;
        setTension(stressLevel);

        // Check for hijack
        if (data.active_hijack && !hijackActive) {
          setHijackActive(true);
          setHijackAspect(data.active_hijack.aspect);
        }
      } catch (err) {
        // Silently fail - offline mode
        setIsOnline(false);
      }
    };

    const interval = setInterval(fetchPsyche, 2000);
    return () => clearInterval(interval);
  }, [session, hijackActive]);

  // Handle character creation completion
  const handleCharacterCreated = (data) => {
    setSession(data.session_id);
    setGameState(data.state);
    if (data.assets) setAssets(prev => ({ ...prev, ...data.assets }));
    setShowCharacterCreation(false);
    setIsOnline(true);
  };

  // Quick start for returning players (skip wizard)
  const handleQuickStart = async () => {
    setLoading(true);
    try {
      const data = await api.post('/session/start', {
        character_name: "Kaelen",
        background_vow: "Find the Truth"
      });
      handleCharacterCreated(data);
    } catch (err) {
      console.error("Failed to start session:", err);
      setIsOnline(false);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (actionText) => {
    if (!session) return;

    setLoading(true)
    try {
      const data = await api.post('/chat', {
        session_id: session,
        action: actionText
      });
      setGameState(data.state)
      if (data.assets) setAssets(prev => ({ ...prev, ...data.assets }))
      setIsOnline(true)
    } catch (err) {
      console.error("Action failed:", err)
      setIsOnline(false)
    } finally {
      setLoading(false)
    }
  }

  const handleHijackComplete = () => {
    setHijackActive(false);
    setHijackAspect(null);
  };

  // Show character creation wizard
  if (showCharacterCreation) {
    return (
      <AccessibilityProvider>
        <div className="min-h-screen bg-disco-bg">
          <AmbientParticles type="dust" count={20} />

          {/* Title */}
          <div className="pt-8 text-center">
            <h1 className="text-5xl font-serif text-disco-paper tracking-wider">
              STARFORGED
            </h1>
            <p className="text-disco-cyan font-mono text-sm mt-2">
              AI Game Master
            </p>
          </div>

          <CharacterCreation
            onComplete={handleCharacterCreated}
            onCancel={handleQuickStart}
          />
        </div>
      </AccessibilityProvider>
    );
  }

  if (!gameState) return (
    <div className="h-screen flex flex-col items-center justify-center text-disco-paper bg-disco-bg">
      <div className="text-4xl font-serif italic mb-4">Loading the Forge...</div>
      <div className="flex gap-2">
        {[0, 1, 2].map(i => (
          <div
            key={i}
            className="w-3 h-3 bg-disco-accent rounded-full animate-pulse"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
      {!isOnline && (
        <div className="mt-4 text-disco-red text-sm font-mono">
          ⚠ Offline - Waiting for connection...
        </div>
      )}
    </div>
  )

  return (
    <AccessibilityProvider>
      <SoundEffectsProvider>
        <ToastProvider>
          {/* Connection Status Indicator */}
          {!isOnline && (
            <div className="fixed top-4 right-4 z-[200] bg-disco-red/90 text-white px-4 py-2 rounded-lg font-mono text-sm border border-disco-red shadow-lg">
              ⚠ Offline Mode
            </div>
          )}

          {/* Ambient Particles - subtle floating dust */}
          <AmbientParticles type="dust" count={15} />

          {/* Tension Vignette - intensifies with stress */}
          <TensionVignette tension={tension} isActive={true} />

          {/* Hijack Overlay - full takeover on psychological hijack */}
          <HijackOverlay
            isActive={hijackActive}
            aspect={hijackAspect}
            onComplete={handleHijackComplete}
          />

          {/* Main Game Layout */}
          <Layout
            gameState={gameState}
            assets={assets}
            onAction={handleAction}
            isLoading={loading}
          />

          {/* Psyche Dashboard - shows psychological state */}
          <PsycheDashboard />

          {/* Soundscape Engine - ambient audio */}
          <SoundscapeEngine />
        </ToastProvider>
      </SoundEffectsProvider>
    </AccessibilityProvider>
  )
}

export default App
