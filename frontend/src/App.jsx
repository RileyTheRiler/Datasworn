import { useState, useEffect } from 'react'
import Layout from './Layout'

// API Base URL
const API_URL = 'http://localhost:8000/api';

function App() {
  const [session, setSession] = useState(null)
  const [gameState, setGameState] = useState(null)
  const [assets, setAssets] = useState({ scene_image: null, portrait: null })
  const [loading, setLoading] = useState(false)

  // Initial Load
  useEffect(() => {
    startSession();
  }, [])

  const startSession = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_name: "Kaelen",
          background_vow: "Find the Truth"
        })
      });
      const data = await res.json();
      setSession(data.session_id)
      setGameState(data.state)
      if (data.assets) setAssets(prev => ({ ...prev, ...data.assets }))
    } catch (err) {
      console.error("Failed to start session:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (actionText) => {
    if (!session) return;

    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session,
          action: actionText
        })
      });
      const data = await res.json();
      setGameState(data.state)
      if (data.assets) setAssets(prev => ({ ...prev, ...data.assets }))
    } catch (err) {
      console.error("Action failed:", err)
    } finally {
      setLoading(false)
    }
  }

  if (!gameState) return <div className="h-screen flex items-center justify-center text-disco-paper">Loading the Forge...</div>

  return (
    <Layout
      gameState={gameState}
      assets={assets}
      onAction={handleAction}
      isLoading={loading}
    />
  )
}

export default App
