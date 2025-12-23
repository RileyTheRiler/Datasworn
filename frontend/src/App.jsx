import { useState, useEffect } from 'react'
import Layout from './Layout'
import PsycheDashboard from './components/PsycheDashboard'
import CharacterCreation from './components/CharacterCreation'
import Tutorial from './components/Tutorial'
import { ToastProvider, useToast } from './components/ToastProvider'
import { TensionVignette, AmbientParticles, HijackOverlay } from './components/UXEffects'
import AudioManager from './components/AudioManager'
import { SoundEffectsProvider } from './contexts/SoundEffectsContext'
import { AccessibilityProvider } from './contexts/AccessibilityContext'
import { NPCCacheProvider } from './contexts/NPCCacheContext'
import { AudioProvider } from './contexts/AudioContext'
import { VoiceProvider } from './contexts/VoiceContext'
import api from './utils/api'
import { ErrorBoundary } from './components/ErrorStates'
import { LoadingText, LoadingDots } from './components/LoadingStates'
import ErrorBanner from './components/ErrorBanner'

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
  const [error, setError] = useState(null) // Error state for ErrorBanner
  const [lastAction, setLastAction] = useState(null) // Store last action for retry

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
      if (!session || document.hidden) return; // Pause when tab is inactive
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

    // Reduced from 2s to 10s to improve battery life and reduce server load
    const interval = setInterval(fetchPsyche, 10000);
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
    setError(null) // Clear previous errors
    setLastAction(actionText) // Store for retry

    try {
      const data = await api.post('/chat', {
        session_id: session,
        action: actionText
      });
      setGameState(data.state)
      if (data.assets) {
        setAssets(prev => ({ ...prev, ...data.assets }))
        if (data.assets.voice_audio && window.playVoice) {
          window.playVoice(data.assets.voice_audio);
        }
      }
      setIsOnline(true)
    } catch (err) {
      console.error("Action failed:", err)
      setIsOnline(false)

      // Show user-friendly error message
      const errorMessage = err.response?.data?.detail || err.message || "Unknown error";
      setError({
        message: "Failed to process your action",
        details: errorMessage,
        retryable: true
      });
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
      <LoadingText
        messages={[
          'Loading the Forge...',
          'Consulting the Oracle...',
          'Aligning the stars...',
          'Weaving threads of destiny...'
        ]}
        interval={2000}
      />
      <LoadingDots className="mt-4" />
      {!isOnline && (
        <div className="mt-6 text-disco-red text-sm font-mono border border-disco-red/50 bg-disco-red/10 px-4 py-2 rounded">
          ⚠ Offline - Waiting for connection...
        </div>
      )}
    </div>
  )

  return (
    <ErrorBoundary>
      <AccessibilityProvider>
        <AudioProvider>
          <SoundEffectsProvider>
            <VoiceProvider>
              <NPCCacheProvider>
                <ToastProvider>
              {/* Error Banner - show errors with retry option */}
              <ErrorBanner
                error={error}
                onRetry={() => lastAction && handleAction(lastAction)}
                onDismiss={() => setError(null)}
              />

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
                onAssetsUpdate={setAssets}
                onAction={handleAction}
                onGameStateUpdate={setGameState}
                isLoading={loading}
              />

              {/* Psyche Dashboard - shows psychological state */}
              <PsycheDashboard />

              {/* Audio Manager - handles all audio playback */}
              <AudioManager sessionId={session} />

              {/* Tutorial - interactive onboarding */}
              <Tutorial />
                </ToastProvider>
              </NPCCacheProvider>
            </VoiceProvider>
          </SoundEffectsProvider>
        </AudioProvider>
      </AccessibilityProvider>
    </ErrorBoundary>
  )
}

export default App
